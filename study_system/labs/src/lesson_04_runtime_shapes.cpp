#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;

void PrintUsage(const char* argv0) {
  std::cerr << "Usage:\n";
  std::cerr << "  " << argv0 << " cpu [seconds]\n";
  std::cerr << "  " << argv0 << " sleep [seconds]\n";
  std::cerr << "  " << argv0 << " mixed [seconds]\n";
  std::cerr << "  " << argv0 << " io [seconds]\n";
}

void BusyForSeconds(int seconds) {
  volatile double sink = 0.0;
  const auto end = Clock::now() + std::chrono::seconds(seconds);
  while (Clock::now() < end) {
    for (int i = 1; i < 10000; ++i) {
      sink += std::sqrt(static_cast<double>(i));
    }
  }
  std::cout << "busy_sink=" << std::fixed << std::setprecision(2) << sink << "\n";
}

void SleepForSeconds(int seconds) {
  const auto end = Clock::now() + std::chrono::seconds(seconds);
  int wakeups = 0;
  while (Clock::now() < end) {
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    ++wakeups;
  }
  std::cout << "wakeups=" << wakeups << "\n";
}

void MixedForSeconds(int seconds) {
  const auto end = Clock::now() + std::chrono::seconds(seconds);
  volatile double sink = 0.0;
  int wakeups = 0;
  while (Clock::now() < end) {
    for (int i = 1; i < 30000; ++i) {
      sink += std::sqrt(static_cast<double>(i));
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(30));
    ++wakeups;
  }
  std::cout << "mixed_sink=" << std::fixed << std::setprecision(2) << sink
            << " wakeups=" << wakeups << "\n";
}

void IoForSeconds(int seconds) {
  const std::string path = "/tmp/study_system_runtime_io.txt";
  std::ofstream out(path, std::ios::binary | std::ios::trunc);
  out << std::string(1024 * 1024, 'a');
  out.close();

  const auto end = Clock::now() + std::chrono::seconds(seconds);
  std::uint64_t reads = 0;
  std::vector<char> buffer(4096);

  while (Clock::now() < end) {
    std::ifstream in(path, std::ios::binary);
    while (in.read(buffer.data(), static_cast<std::streamsize>(buffer.size())) ||
           in.gcount() > 0) {
      reads += static_cast<std::uint64_t>(in.gcount());
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(20));
  }

  std::cout << "bytes_read=" << reads << "\n";
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2) {
    PrintUsage(argv[0]);
    return 1;
  }

  try {
    const std::string mode = argv[1];
    const int seconds = argc >= 3 ? std::stoi(argv[2]) : 10;
    if (seconds <= 0) {
      PrintUsage(argv[0]);
      return 1;
    }

    std::cout << "mode=" << mode << " seconds=" << seconds << "\n";
    if (mode == "cpu") {
      BusyForSeconds(seconds);
      return 0;
    }
    if (mode == "sleep") {
      SleepForSeconds(seconds);
      return 0;
    }
    if (mode == "mixed") {
      MixedForSeconds(seconds);
      return 0;
    }
    if (mode == "io") {
      IoForSeconds(seconds);
      return 0;
    }
  } catch (const std::exception& ex) {
    std::cerr << "error: " << ex.what() << "\n";
    return 1;
  }

  PrintUsage(argv[0]);
  return 1;
}
