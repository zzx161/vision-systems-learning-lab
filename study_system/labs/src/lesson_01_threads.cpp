#include <atomic>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

#if defined(__linux__)
#include <sched.h>
#endif

namespace {

using Clock = std::chrono::steady_clock;

struct Result {
  std::string name;
  std::uint64_t counter = 0;
  double seconds = 0.0;
};

template <typename Fn>
Result RunCase(const std::string& name, Fn&& fn) {
  const auto start = Clock::now();
  const std::uint64_t counter = fn();
  const auto end = Clock::now();
  return {name, counter, std::chrono::duration<double>(end - start).count()};
}

std::uint64_t RunSingle(std::uint64_t iterations) {
  volatile std::uint64_t counter = 0;
  for (std::uint64_t i = 0; i < iterations; ++i) {
    ++counter;
  }
  return counter;
}

std::uint64_t RunSharedMutex(int thread_count, std::uint64_t iterations_per_thread) {
  volatile std::uint64_t counter = 0;
  std::mutex mutex;
  std::vector<std::thread> threads;
  threads.reserve(thread_count);

  for (int t = 0; t < thread_count; ++t) {
    threads.emplace_back([&]() {
      for (std::uint64_t i = 0; i < iterations_per_thread; ++i) {
        std::lock_guard<std::mutex> lock(mutex);
        ++counter;
      }
    });
  }

  for (auto& thread : threads) {
    thread.join();
  }

  return counter;
}

std::uint64_t RunSharedAtomic(int thread_count, std::uint64_t iterations_per_thread) {
  std::atomic<std::uint64_t> counter{0};
  std::vector<std::thread> threads;
  threads.reserve(thread_count);

  for (int t = 0; t < thread_count; ++t) {
    threads.emplace_back([&]() {
      for (std::uint64_t i = 0; i < iterations_per_thread; ++i) {
        counter.fetch_add(1, std::memory_order_relaxed);
      }
    });
  }

  for (auto& thread : threads) {
    thread.join();
  }

  return counter.load(std::memory_order_relaxed);
}

std::uint64_t RunPerThread(int thread_count, std::uint64_t iterations_per_thread) {
  std::vector<std::uint64_t> counters(thread_count, 0);
  std::vector<std::thread> threads;
  threads.reserve(thread_count);

  for (int t = 0; t < thread_count; ++t) {
    threads.emplace_back([&, t]() {
      volatile std::uint64_t local = 0;
      for (std::uint64_t i = 0; i < iterations_per_thread; ++i) {
        ++local;
      }
      counters[t] = local;
    });
  }

  for (auto& thread : threads) {
    thread.join();
  }

  std::uint64_t total = 0;
  for (const auto value : counters) {
    total += value;
  }
  return total;
}

std::uint64_t RunSingleSleepWait(int thread_count, int waits_per_thread,
                                std::chrono::milliseconds wait_time) {
  std::uint64_t completed_waits = 0;
  const int total_waits = thread_count * waits_per_thread;
  for (int i = 0; i < total_waits; ++i) {
    std::this_thread::sleep_for(wait_time);
    ++completed_waits;
  }
  return completed_waits;
}

std::uint64_t RunMultiSleepWait(int thread_count, int waits_per_thread,
                               std::chrono::milliseconds wait_time) {
  std::atomic<std::uint64_t> completed_waits{0};
  std::vector<std::thread> threads;
  threads.reserve(thread_count);

  for (int t = 0; t < thread_count; ++t) {
    threads.emplace_back([&]() {
      for (int i = 0; i < waits_per_thread; ++i) {
        std::this_thread::sleep_for(wait_time);
        completed_waits.fetch_add(1, std::memory_order_relaxed);
      }
    });
  }

  for (auto& thread : threads) {
    thread.join();
  }

  return completed_waits.load(std::memory_order_relaxed);
}

void PrintUsage(const char* argv0) {
  std::cerr << "Usage: " << argv0
            << " [thread_count] [iterations_per_thread] [pin_cpu]\n";
  std::cerr << "Example: " << argv0 << " 4 20000000\n";
  std::cerr << "Example pinned to CPU 0: " << argv0 << " 4 20000000 0\n";
}

bool PinToCpu(int cpu_id) {
#if defined(__linux__)
  cpu_set_t set;
  CPU_ZERO(&set);
  CPU_SET(cpu_id, &set);
  return sched_setaffinity(0, sizeof(set), &set) == 0;
#else
  (void)cpu_id;
  return false;
#endif
}

}  // namespace

int main(int argc, char** argv) {
  int thread_count = 4;
  std::uint64_t iterations_per_thread = 20000000;
  int pin_cpu = -1;

  if (argc >= 2) {
    try {
      thread_count = std::stoi(argv[1]);
    } catch (...) {
      PrintUsage(argv[0]);
      return 1;
    }
  }

  if (argc >= 3) {
    try {
      iterations_per_thread = std::stoull(argv[2]);
    } catch (...) {
      PrintUsage(argv[0]);
      return 1;
    }
  }

  if (argc >= 4) {
    try {
      pin_cpu = std::stoi(argv[3]);
    } catch (...) {
      PrintUsage(argv[0]);
      return 1;
    }
  }

  if (thread_count <= 0 || iterations_per_thread == 0) {
    PrintUsage(argv[0]);
    return 1;
  }

  if (pin_cpu >= 0 && !PinToCpu(pin_cpu)) {
    std::cerr << "Failed to pin process to CPU " << pin_cpu << "\n";
    return 1;
  }

  const std::uint64_t total_iterations =
      static_cast<std::uint64_t>(thread_count) * iterations_per_thread;
  constexpr int kWaitsPerThread = 5;
  constexpr auto kWaitTime = std::chrono::milliseconds(50);

  std::vector<Result> results;
  results.push_back(RunCase("single_thread_total_work", [&]() {
    return RunSingle(total_iterations);
  }));
  results.push_back(RunCase("shared_mutex_counter", [&]() {
    return RunSharedMutex(thread_count, iterations_per_thread);
  }));
  results.push_back(RunCase("shared_atomic_counter", [&]() {
    return RunSharedAtomic(thread_count, iterations_per_thread);
  }));
  results.push_back(RunCase("per_thread_counter", [&]() {
    return RunPerThread(thread_count, iterations_per_thread);
  }));
  results.push_back(RunCase("single_thread_sleep_wait", [&]() {
    return RunSingleSleepWait(thread_count, kWaitsPerThread, kWaitTime);
  }));
  results.push_back(RunCase("multi_thread_sleep_wait", [&]() {
    return RunMultiSleepWait(thread_count, kWaitsPerThread, kWaitTime);
  }));

  std::cout << "thread_count=" << thread_count
            << " iterations_per_thread=" << iterations_per_thread
            << " total_iterations=" << total_iterations;
  if (pin_cpu >= 0) {
    std::cout << " pinned_cpu=" << pin_cpu;
  }
  std::cout << "\n\n";

  std::cout << std::left << std::setw(28) << "case" << std::setw(18) << "counter"
            << "seconds\n";
  for (const auto& result : results) {
    std::cout << std::left << std::setw(28) << result.name << std::setw(18)
              << result.counter << std::fixed << std::setprecision(6)
              << result.seconds << "\n";
  }

  std::cout << "\nWhat to look for:\n";
  std::cout << "- shared_mutex_counter is often much slower than expected\n";
  std::cout << "- shared_atomic_counter avoids the mutex but still shares one hot counter\n";
  std::cout << "- per_thread_counter should scale better because coordination is lower\n";
  std::cout << "- multi_thread_sleep_wait overlaps waiting time even on one CPU core\n";
  std::cout << "- single_thread_total_work is a useful baseline for total work\n";
  return 0;
}
