#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <string>
#include <thread>
#include <vector>

#if defined(__linux__)
#include <pthread.h>
#include <sched.h>
#endif

namespace {

using Clock = std::chrono::steady_clock;
using Microseconds = std::chrono::microseconds;

struct Options {
  // 模拟多少帧。帧数越多，越容易看到偶发的 tail latency。
  int frames = 300;
  // 每隔多少毫秒释放一帧。这个周期同时也是本实验里的 deadline。
  int period_ms = 10;
  // 每帧模拟多少微秒的 CPU 工作。这里不是 sleep，而是忙等计算。
  int work_us = 2000;
  // 后台干扰线程数量，用来模拟日志、后台任务或其他进程抢 CPU。
  int background_threads = 0;
  // 主线程绑定到哪个 CPU；-1 表示不绑定，让调度器自由安排。
  int pin_main_cpu = -1;
  // 后台线程绑定到哪个 CPU；-1 表示不绑定。
  int pin_background_cpu = -1;
};

struct Stats {
  // 平均值只能表示“通常情况”，不能代表最坏情况。
  double avg_us = 0.0;
  // p50/p90/p99 用来观察尾部延迟是否被少数慢帧拉高。
  std::int64_t p50_us = 0;
  std::int64_t p90_us = 0;
  std::int64_t p99_us = 0;
  // max 是最差的一帧，常用来观察偶发尖刺。
  std::int64_t max_us = 0;
  // 超过 deadline 的帧数。实时系统里，这个比平均值更敏感。
  int missed_deadlines = 0;
};

void PrintUsage(const char* argv0) {
  std::cerr
      << "Usage: " << argv0
      << " [frames] [period_ms] [work_us] [background_threads]"
      << " [pin_main_cpu] [pin_background_cpu]\n"
      << "Example baseline: " << argv0 << " 300 10 2000 0\n"
      << "Example noisy:    " << argv0 << " 300 10 2000 4\n"
      << "Example pinned:   " << argv0 << " 300 10 2000 4 0 1\n";
}

bool ParseInt(const char* text, int* out) {
  try {
    *out = std::stoi(text);
    return true;
  } catch (...) {
    return false;
  }
}

bool PinCurrentThreadToCpu(int cpu_id) {
#if defined(__linux__)
  if (cpu_id < 0) {
    return true;
  }

  cpu_set_t set;
  CPU_ZERO(&set);
  CPU_SET(cpu_id, &set);
  return pthread_setaffinity_np(pthread_self(), sizeof(set), &set) == 0;
#else
  (void)cpu_id;
  return cpu_id < 0;
#endif
}

void BusyWorkFor(Microseconds duration) {
  const auto end = Clock::now() + duration;
  volatile std::uint64_t value = 1;
  // 用忙等模拟 CPU-bound 处理。这样它会真实占用 CPU，而不是睡眠等待。
  while (Clock::now() < end) {
    value = value * 1664525 + 1013904223;
  }
}

Stats Summarize(std::vector<std::int64_t> values, std::int64_t deadline_us) {
  Stats stats;
  if (values.empty()) {
    return stats;
  }

  std::sort(values.begin(), values.end());
  const auto percentile = [&](double p) {
    // p99 不是最坏值，而是“99% 样本都不超过它”的位置。
    const std::size_t index = static_cast<std::size_t>(
        std::min<double>(values.size() - 1, (values.size() - 1) * p));
    return values[index];
  };

  const std::int64_t total =
      std::accumulate(values.begin(), values.end(), std::int64_t{0});
  stats.avg_us = static_cast<double>(total) / static_cast<double>(values.size());
  stats.p50_us = percentile(0.50);
  stats.p90_us = percentile(0.90);
  stats.p99_us = percentile(0.99);
  stats.max_us = values.back();
  stats.missed_deadlines =
      static_cast<int>(std::count_if(values.begin(), values.end(),
                                     [&](std::int64_t v) { return v > deadline_us; }));
  return stats;
}

Options ParseOptions(int argc, char** argv) {
  Options options;
  int* fields[] = {&options.frames,
                   &options.period_ms,
                   &options.work_us,
                   &options.background_threads,
                   &options.pin_main_cpu,
                   &options.pin_background_cpu};

  for (int i = 1; i < argc; ++i) {
    if (i > 6 || !ParseInt(argv[i], fields[i - 1])) {
      PrintUsage(argv[0]);
      std::exit(1);
    }
  }

  if (options.frames <= 0 || options.period_ms <= 0 || options.work_us <= 0 ||
      options.background_threads < 0) {
    PrintUsage(argv[0]);
    std::exit(1);
  }

  return options;
}

}  // namespace

int main(int argc, char** argv) {
  const Options options = ParseOptions(argc, argv);
  std::atomic<bool> stop_background{false};
  std::vector<std::thread> background_threads;

  for (int i = 0; i < options.background_threads; ++i) {
    background_threads.emplace_back([&, i]() {
      const int cpu = options.pin_background_cpu >= 0
                          ? options.pin_background_cpu + (i % 1)
                          : -1;
      if (!PinCurrentThreadToCpu(cpu)) {
        std::cerr << "warning: failed to pin background thread to CPU " << cpu
                  << "\n";
      }
      // 后台线程不断做短 CPU 工作再 yield，模拟系统里的后台干扰。
      // 它的目的不是完成业务，而是制造调度竞争。
      while (!stop_background.load(std::memory_order_relaxed)) {
        BusyWorkFor(Microseconds(500));
        std::this_thread::yield();
      }
    });
  }

  if (!PinCurrentThreadToCpu(options.pin_main_cpu)) {
    std::cerr << "warning: failed to pin main thread to CPU "
              << options.pin_main_cpu << "\n";
  }

  std::vector<std::int64_t> frame_latencies_us;
  std::vector<std::int64_t> start_jitter_us;
  frame_latencies_us.reserve(options.frames);
  start_jitter_us.reserve(options.frames);

  const auto period = std::chrono::milliseconds(options.period_ms);
  const auto work = Microseconds(options.work_us);
  auto next_release = Clock::now() + period;

  for (int frame = 0; frame < options.frames; ++frame) {
    // sleep_until 模拟“下一帧应该在这个时刻到来”。
    // 如果线程被调度晚了，actual_start 就会晚于 next_release。
    std::this_thread::sleep_until(next_release);
    const auto actual_start = Clock::now();
    const auto jitter =
        std::chrono::duration_cast<Microseconds>(actual_start - next_release);

    // 这里模拟一帧的处理时间，例如预处理、轻量算法或回调里的 CPU 工作。
    BusyWorkFor(work);

    const auto finish = Clock::now();
    // latency 从计划释放时间开始算，所以包含“醒晚了/等 CPU”的时间。
    // 这能帮助我们区分：代码本身没变重，但调度导致整帧变晚。
    const auto latency =
        std::chrono::duration_cast<Microseconds>(finish - next_release);

    start_jitter_us.push_back(jitter.count());
    frame_latencies_us.push_back(latency.count());
    next_release += period;
  }

  stop_background.store(true, std::memory_order_relaxed);
  for (auto& thread : background_threads) {
    thread.join();
  }

  const auto deadline_us =
      std::chrono::duration_cast<Microseconds>(period).count();
  const Stats latency = Summarize(frame_latencies_us, deadline_us);
  const Stats jitter = Summarize(start_jitter_us, deadline_us);

  std::cout << "frames=" << options.frames
            << " period_ms=" << options.period_ms
            << " work_us=" << options.work_us
            << " background_threads=" << options.background_threads
            << " pin_main_cpu=" << options.pin_main_cpu
            << " pin_background_cpu=" << options.pin_background_cpu << "\n";

  std::cout << std::fixed << std::setprecision(1);
  std::cout << "frame_latency_us"
            << " avg=" << latency.avg_us
            << " p50=" << latency.p50_us
            << " p90=" << latency.p90_us
            << " p99=" << latency.p99_us
            << " max=" << latency.max_us
            << " missed_deadlines=" << latency.missed_deadlines << "\n";

  std::cout << "start_jitter_us"
            << " avg=" << jitter.avg_us
            << " p50=" << jitter.p50_us
            << " p90=" << jitter.p90_us
            << " p99=" << jitter.p99_us
            << " max=" << jitter.max_us << "\n";

  return 0;
}
