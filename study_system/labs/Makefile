CXX := g++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra -pedantic -pthread
SRC_DIR := src
BIN_DIR := bin

TARGETS := \
	$(BIN_DIR)/lesson_01_threads \
	$(BIN_DIR)/lesson_02_memory \
	$(BIN_DIR)/lesson_03_cache \
	$(BIN_DIR)/lesson_04_runtime_shapes \
	$(BIN_DIR)/lesson_06_tail_latency

.PHONY: all clean

all: $(TARGETS)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BIN_DIR)/lesson_01_threads: $(SRC_DIR)/lesson_01_threads.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@

$(BIN_DIR)/lesson_02_memory: $(SRC_DIR)/lesson_02_memory.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@

$(BIN_DIR)/lesson_03_cache: $(SRC_DIR)/lesson_03_cache.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@

$(BIN_DIR)/lesson_04_runtime_shapes: $(SRC_DIR)/lesson_04_runtime_shapes.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@

$(BIN_DIR)/lesson_06_tail_latency: $(SRC_DIR)/lesson_06_tail_latency.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< -o $@

clean:
	rm -rf $(BIN_DIR)
