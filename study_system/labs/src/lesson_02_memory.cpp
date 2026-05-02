#include <chrono>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <string>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <vector>

namespace {

using Clock = std::chrono::steady_clock;

void PrintUsage(const char* argv0) {
  std::cerr << "Usage:\n";
  std::cerr << "  " << argv0 << " copy [size_mb] [rounds]\n";
  std::cerr << "  " << argv0 << " touch [size_mb] [stride_bytes] [rounds]\n";
  std::cerr << "  " << argv0 << " read_vs_mmap [size_mb] [rounds]\n";
  std::cerr << "  " << argv0 << " read_vs_mmap_once [size_mb]\n";
  std::cerr << "  " << argv0 << " read_vs_mmap_repeated [size_mb] [rounds]\n";
  std::cerr << "  " << argv0 << " mmap_phases [size_mb] [rounds]\n";
}

double SecondsSince(Clock::time_point start) {
  return std::chrono::duration<double>(Clock::now() - start).count();
}

std::uint64_t TouchBuffer(const std::vector<std::uint8_t>& buffer,
                          std::size_t stride_bytes, int rounds) {
  volatile std::uint64_t sum = 0;
  for (int round = 0; round < rounds; ++round) {
    for (std::size_t i = 0; i < buffer.size(); i += stride_bytes) {
      sum += buffer[i];
    }
  }
  return sum;
}

int RunCopy(std::size_t size_mb, int rounds) {
  const std::size_t bytes = size_mb * 1024 * 1024;
  std::vector<std::uint8_t> src(bytes, 7);
  std::vector<std::uint8_t> dst(bytes, 0);

  const auto start = Clock::now();
  for (int round = 0; round < rounds; ++round) {
    std::memcpy(dst.data(), src.data(), bytes);
    dst[round % dst.size()] ^= 1;
  }
  const double seconds = SecondsSince(start);

  std::cout << "mode=copy size_mb=" << size_mb << " rounds=" << rounds
            << " seconds=" << std::fixed << std::setprecision(6) << seconds
            << "\n";
  std::cout << "Observation: repeated full-buffer copies consume time and bandwidth.\n";
  return 0;
}

int RunTouch(std::size_t size_mb, std::size_t stride_bytes, int rounds) {
  if (stride_bytes == 0) {
    std::cerr << "stride_bytes must be > 0\n";
    return 1;
  }

  const std::size_t bytes = size_mb * 1024 * 1024;
  std::vector<std::uint8_t> buffer(bytes, 1);

  const auto start = Clock::now();
  const std::uint64_t sum = TouchBuffer(buffer, stride_bytes, rounds);
  const double seconds = SecondsSince(start);

  std::cout << "mode=touch size_mb=" << size_mb << " stride_bytes=" << stride_bytes
            << " rounds=" << rounds << " sum=" << sum << " seconds=" << std::fixed
            << std::setprecision(6) << seconds << "\n";
  std::cout << "Observation: changing stride changes locality and runtime.\n";
  return 0;
}

std::filesystem::path CreateTempFile(std::size_t bytes) {
  std::filesystem::path pattern =
      std::filesystem::temp_directory_path() / "study_system_memory_lab_XXXXXX";
  std::string path_template = pattern.string();
  std::vector<char> mutable_path(path_template.begin(), path_template.end());
  mutable_path.push_back('\0');

  int fd = ::mkstemp(mutable_path.data());
  if (fd < 0) {
    throw std::runtime_error("failed to open temp file");
  }
  const std::filesystem::path path(mutable_path.data());

  std::vector<std::uint8_t> chunk(1024 * 1024, 3);
  std::size_t written = 0;
  while (written < bytes) {
    const std::size_t remaining = bytes - written;
    const std::size_t to_write = std::min(chunk.size(), remaining);
    const auto rc = ::write(fd, chunk.data(), to_write);
    if (rc < 0) {
      ::close(fd);
      throw std::runtime_error("failed to write temp file");
    }
    written += static_cast<std::size_t>(rc);
  }
  ::fsync(fd);
  ::lseek(fd, 0, SEEK_SET);
  ::close(fd);
  return path;
}

std::uint64_t TouchEveryPage(const std::uint8_t* data, std::size_t bytes, int rounds) {
  volatile std::uint64_t sum = 0;
  for (int round = 0; round < rounds; ++round) {
    for (std::size_t i = 0; i < bytes; i += 4096) {
      sum += data[i];
    }
  }
  return sum;
}

std::uint64_t SequentialRead(int fd, std::size_t bytes, int rounds,
                             bool read_each_round) {
  std::vector<std::uint8_t> buffer(bytes);
  volatile std::uint64_t sum = 0;
  for (int round = 0; round < rounds; ++round) {
    if (round == 0 || read_each_round) {
      ::lseek(fd, 0, SEEK_SET);
      std::size_t total = 0;
      while (total < bytes) {
        const auto rc = ::read(fd, buffer.data() + total, bytes - total);
        if (rc <= 0) {
          break;
        }
        total += static_cast<std::size_t>(rc);
      }
    }
    sum += TouchEveryPage(buffer.data(), bytes, 1);
  }
  return sum;
}

std::uint64_t SequentialMmap(int fd, std::size_t bytes, int rounds) {
  void* mapping = ::mmap(nullptr, bytes, PROT_READ, MAP_PRIVATE, fd, 0);
  if (mapping == MAP_FAILED) {
    throw std::runtime_error("mmap failed");
  }

  auto* data = static_cast<std::uint8_t*>(mapping);
  const std::uint64_t sum = TouchEveryPage(data, bytes, rounds);

  ::munmap(mapping, bytes);
  return sum;
}

int RunReadVsMmap(std::size_t size_mb, int rounds, bool read_each_round,
                  const std::string& mode_name) {
  const std::size_t bytes = size_mb * 1024 * 1024;
  const auto path = CreateTempFile(bytes);
  int fd = ::open(path.c_str(), O_RDONLY);
  if (fd < 0) {
    std::cerr << "failed to reopen temp file\n";
    return 1;
  }

  const auto read_start = Clock::now();
  const auto read_sum = SequentialRead(fd, bytes, rounds, read_each_round);
  const double read_seconds = SecondsSince(read_start);

  const auto mmap_start = Clock::now();
  const auto mmap_sum = SequentialMmap(fd, bytes, rounds);
  const double mmap_seconds = SecondsSince(mmap_start);

  ::close(fd);
  std::filesystem::remove(path);

  std::cout << "mode=" << mode_name << " size_mb=" << size_mb << " rounds=" << rounds
            << " read_each_round=" << (read_each_round ? "yes" : "no") << "\n";
  std::cout << "read_sum=" << read_sum << " read_seconds=" << std::fixed
            << std::setprecision(6) << read_seconds << "\n";
  std::cout << "mmap_sum=" << mmap_sum << " mmap_seconds=" << std::fixed
            << std::setprecision(6) << mmap_seconds << "\n";
  if (read_each_round) {
    std::cout << "Observation: repeated read copies data again; mmap reuses one mapping.\n";
  } else {
    std::cout << "Observation: both paths load once, then repeatedly touch resident data.\n";
  }
  return 0;
}

int RunMmapPhases(std::size_t size_mb, int rounds) {
  const std::size_t bytes = size_mb * 1024 * 1024;
  const auto path = CreateTempFile(bytes);
  int fd = ::open(path.c_str(), O_RDONLY);
  if (fd < 0) {
    std::cerr << "failed to reopen temp file\n";
    return 1;
  }

  const auto map_start = Clock::now();
  void* mapping = ::mmap(nullptr, bytes, PROT_READ, MAP_PRIVATE, fd, 0);
  const double map_seconds = SecondsSince(map_start);
  if (mapping == MAP_FAILED) {
    ::close(fd);
    std::filesystem::remove(path);
    throw std::runtime_error("mmap failed");
  }

  auto* data = static_cast<std::uint8_t*>(mapping);
  const auto first_touch_start = Clock::now();
  const auto first_sum = TouchEveryPage(data, bytes, 1);
  const double first_touch_seconds = SecondsSince(first_touch_start);

  const auto repeat_touch_start = Clock::now();
  const auto repeat_sum = TouchEveryPage(data, bytes, rounds);
  const double repeat_touch_seconds = SecondsSince(repeat_touch_start);

  ::munmap(mapping, bytes);
  ::close(fd);
  std::filesystem::remove(path);

  std::cout << "mode=mmap_phases size_mb=" << size_mb << " repeat_rounds=" << rounds
            << "\n";
  std::cout << "map_seconds=" << std::fixed << std::setprecision(6) << map_seconds
            << "\n";
  std::cout << "first_touch_sum=" << first_sum
            << " first_touch_seconds=" << std::fixed << std::setprecision(6)
            << first_touch_seconds << "\n";
  std::cout << "repeat_touch_sum=" << repeat_sum
            << " repeat_touch_seconds=" << std::fixed << std::setprecision(6)
            << repeat_touch_seconds << "\n";
  std::cout << "Observation: mmap setup is cheap; first touch is where page costs appear.\n";
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
    if (mode == "copy") {
      const std::size_t size_mb = argc >= 3 ? std::stoull(argv[2]) : 256;
      const int rounds = argc >= 4 ? std::stoi(argv[3]) : 20;
      return RunCopy(size_mb, rounds);
    }
    if (mode == "touch") {
      const std::size_t size_mb = argc >= 3 ? std::stoull(argv[2]) : 256;
      const std::size_t stride_bytes = argc >= 4 ? std::stoull(argv[3]) : 64;
      const int rounds = argc >= 5 ? std::stoi(argv[4]) : 20;
      return RunTouch(size_mb, stride_bytes, rounds);
    }
    if (mode == "read_vs_mmap") {
      const std::size_t size_mb = argc >= 3 ? std::stoull(argv[2]) : 128;
      const int rounds = argc >= 4 ? std::stoi(argv[3]) : 10;
      return RunReadVsMmap(size_mb, rounds, true, "read_vs_mmap");
    }
    if (mode == "read_vs_mmap_once") {
      const std::size_t size_mb = argc >= 3 ? std::stoull(argv[2]) : 128;
      return RunReadVsMmap(size_mb, 1, false, "read_vs_mmap_once");
    }
    if (mode == "read_vs_mmap_repeated") {
      const std::size_t size_mb = argc >= 3 ? std::stoull(argv[2]) : 128;
      const int rounds = argc >= 4 ? std::stoi(argv[3]) : 10;
      return RunReadVsMmap(size_mb, rounds, false, "read_vs_mmap_repeated");
    }
    if (mode == "mmap_phases") {
      const std::size_t size_mb = argc >= 3 ? std::stoull(argv[2]) : 128;
      const int rounds = argc >= 4 ? std::stoi(argv[3]) : 10;
      return RunMmapPhases(size_mb, rounds);
    }
  } catch (const std::exception& ex) {
    std::cerr << "error: " << ex.what() << "\n";
    return 1;
  }

  PrintUsage(argv[0]);
  return 1;
}
