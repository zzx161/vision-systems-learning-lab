#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;

struct alignas(64) PaddedCounter {
  std::uint64_t value = 0;
};

void PrintUsage(const char* argv0) {
  std::cerr << "Usage:\n";
  std::cerr << "  " << argv0 << " stride [size_mb] [stride_ints] [rounds]\n";
  std::cerr << "  " << argv0 << " false_sharing [iterations_per_thread]\n";
}

double SecondsSince(Clock::time_point start) {
  return std::chrono::duration<double>(Clock::now() - start).count();
}

int RunStride(std::size_t size_mb, std::size_t stride_ints, int rounds) {
  if (stride_ints == 0) {
    std::cerr << "stride_ints must be > 0\n";
    return 1;
  }

  const std::size_t count = size_mb * 1024 * 1024 / sizeof(std::uint32_t);
  std::vector<std::uint32_t> data(count, 1);
  volatile std::uint64_t sum = 0;

  const auto start = Clock::now();
  for (int round = 0; round < rounds; ++round) {
    for (std::size_t i = 0; i < data.size(); i += stride_ints) {
      sum += data[i];
    }
  }
  const double seconds = SecondsSince(start);

  std::cout << "mode=stride size_mb=" << size_mb << " stride_ints=" << stride_ints
            << " rounds=" << rounds << " sum=" << sum << " seconds=" << std::fixed
            << std::setprecision(6) << seconds << "\n";
  std::cout << "Observation: larger stride often hurts locality.\n";
  return 0;
}

int RunFalseSharing(std::uint64_t iterations_per_thread) {
  struct SharedCounter {
    std::uint64_t a = 0;
    std::uint64_t b = 0;
  };

  SharedCounter shared;
  PaddedCounter padded_a;
  PaddedCounter padded_b;

  const auto shared_start = Clock::now();
  std::thread shared_t1([&]() {
    for (std::uint64_t i = 0; i < iterations_per_thread; ++i) {
      ++shared.a;
    }
  });
  std::thread shared_t2([&]() {
    for (std::uint64_t i = 0; i < iterations_per_thread; ++i) {
      ++shared.b;
    }
  });
  shared_t1.join();
  shared_t2.join();
  const double shared_seconds = SecondsSince(shared_start);
  const std::uint64_t shared_total = shared.a + shared.b;

  const auto padded_start = Clock::now();
  std::thread padded_t1([&]() {
    for (std::uint64_t i = 0; i < iterations_per_thread; ++i) {
      ++padded_a.value;
    }
  });
  std::thread padded_t2([&]() {
    for (std::uint64_t i = 0; i < iterations_per_thread; ++i) {
      ++padded_b.value;
    }
  });
  padded_t1.join();
  padded_t2.join();
  const double padded_seconds = SecondsSince(padded_start);
  const std::uint64_t padded_total = padded_a.value + padded_b.value;

  std::cout << "mode=false_sharing iterations_per_thread=" << iterations_per_thread
            << "\n";
  std::cout << "shared_total=" << shared_total << "\n";
  std::cout << "shared_cache_line_seconds=" << std::fixed << std::setprecision(6)
            << shared_seconds << "\n";
  std::cout << "padded_total=" << padded_total << "\n";
  std::cout << "padded_cache_line_seconds=" << std::fixed << std::setprecision(6)
            << padded_seconds << "\n";
  std::cout << "Observation: logically independent counters can still interfere through cache lines.\n";
  return 0;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2) {
    PrintUsage(argv[0]);
    return 1;
  }

  try {
    const std::string mode = argv[1];
    if (mode == "stride") {
      const std::size_t size_mb = argc >= 3 ? std::stoull(argv[2]) : 256;
      const std::size_t stride_ints = argc >= 4 ? std::stoull(argv[3]) : 1;
      const int rounds = argc >= 5 ? std::stoi(argv[4]) : 20;
      return RunStride(size_mb, stride_ints, rounds);
    }
    if (mode == "false_sharing") {
      const std::uint64_t iterations_per_thread =
          argc >= 3 ? std::stoull(argv[2]) : 200000000;
      return RunFalseSharing(iterations_per_thread);
    }
  } catch (const std::exception& ex) {
    std::cerr << "error: " << ex.what() << "\n";
    return 1;
  }

  PrintUsage(argv[0]);
  return 1;
}
