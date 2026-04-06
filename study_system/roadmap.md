# Roadmap

## Phase 1: Core Linux Runtime View

### Module 1: Processes and Threads
- Process vs thread
- User mode vs kernel mode
- Context switch
- Synchronization: mutex, condition variable, atomics
- Common concurrency bugs

### Module 2: Memory
- Virtual memory
- Stack vs heap
- Page, page fault
- Anonymous memory
- File mapping with `mmap`
- Copy cost and memory layout awareness

### Module 3: IO and Data Path
- File IO basics
- Buffered IO vs `mmap`
- Blocking vs non-blocking
- `select` / `poll` / `epoll`
- Zero-copy intuition
- DMA basic intuition

### Module 4: Scheduling and Latency
- Scheduler basics
- Priority
- CPU affinity
- Latency jitter
- Real-time thinking

### Module 5: Observability and Debugging
- `top`, `htop`
- `ps`, `pidstat`
- `vmstat`, `iostat`
- `strace`
- `perf`
- `gdb`

## Phase 2: Computer Architecture for Performance

### Module 6: CPU Execution Basics
- Pipeline
- Out-of-order execution
- Branch prediction
- Why "same complexity" code can run differently

### Module 7: Cache and Locality
- L1 / L2 / L3
- Cache line
- Spatial locality
- Temporal locality
- Cache miss
- False sharing

### Module 8: Memory Hierarchy and Bandwidth
- Register vs cache vs DRAM
- Latency vs bandwidth
- Why memory movement dominates performance

### Module 9: Multi-core and Consistency
- Shared memory model intuition
- Cache coherence
- Memory ordering basics
- Contention
- Scalability limits

### Module 10: SIMD and Data-Oriented Thinking
- SIMD intuition
- Why layout matters
- Array-of-struct vs struct-of-array intuition
- Hot-loop optimization thinking

## Phase 3: Camera/System-Oriented Engineering

### Module 11: Camera Data Path
- Sensor to memory path
- ISP position in the pipeline
- Buffering
- Frame drop causes
- Latency accounting

### Module 12: Stable Production Engineering
- Monitoring
- Backpressure
- Fault isolation
- Regression thinking
- Repeatable debugging workflow

## Suggested Order

Start here:

1. Module 1
2. Module 2
3. Module 5
4. Module 7
5. Module 8
6. Module 3
7. Module 4
8. Module 9
9. Module 10
10. Module 11
11. Module 12

## Learning Rule

For each module, do four things:

1. Build a concept map
2. Run at least one small experiment
3. Write your own summary
4. Answer review questions one week later
