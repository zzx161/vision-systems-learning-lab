# Module 1: Processes and Threads

## What Problem This Solves

This module helps you understand:

- why a program may become slow under concurrency
- why multi-threading does not automatically improve throughput
- where lock contention and context switching come from

## Core Ideas

### Process
A process is an isolated execution context with its own virtual address space and resources.

### Thread
A thread is an execution unit inside a process.
Threads in the same process share the same address space and many resources.

### Why Threads Are Useful
- lower communication cost than processes
- easier shared-state access
- can use multiple CPU cores

### Why Threads Are Dangerous
- races
- deadlocks
- contention
- false sharing
- hard-to-reproduce latency spikes

## Practical Mental Model

When a program becomes slow, ask:

1. Is it CPU-bound or waiting?
2. Is it waiting on a lock?
3. Is there too much context switching?
4. Are threads fighting over shared data?

## What To Remember

- More threads is not always faster.
- Shared memory is convenient but expensive to coordinate.
- The bottleneck is often coordination, not computation.

## Review Questions

1. What resource does each process own independently?
2. Why can threads communicate faster than processes?
3. Why can adding threads make latency worse?
4. What is the difference between race and contention?
