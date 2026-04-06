---
note_type: lab
title: Threads and Contention
track: linux_systems
phase: 1
related_lesson: 1
status: planned
completion: 0
estimated_minutes: 45
actual_minutes: 0
last_run:
next_review:
priority: high
tags:
  - study/lab
  - track/linux
  - phase/1
---

# Lab 1: Threads and Contention

## Goal

Feel the difference between:

- single-thread execution
- multi-thread execution with low contention
- multi-thread execution with high contention

## Tasks

1. Build the lab program.
2. Run the three versions through one executable.
3. Compare runtime.
4. Observe:
   - when threads help
   - when lock contention hurts
   - why separate ownership scales better

## Build

From `/home/zhixin/code/study_system/labs`:

```bash
make bin/lesson_01_threads
```

## Run

Default example:

```bash
./bin/lesson_01_threads 4 20000000
```

Try more than one thread count:

```bash
./bin/lesson_01_threads 2 20000000
./bin/lesson_01_threads 4 20000000
./bin/lesson_01_threads 8 20000000
```

## What The Program Does

It compares:

1. one single-thread version doing the same total work
2. one multi-thread version using a single shared mutex-protected counter
3. one multi-thread version where each thread owns its own counter

## What To Record

- Number of threads
- Total work size
- Runtime
- Which version was fastest
- Which version was slowest
- Your explanation for the difference

## Expected Insight

The shared mutex version may be slower than expected because coordination cost dominates.

The per-thread version is often much better because:

- less lock waiting
- clearer ownership
- lower coordination cost

## Optional Tool Exercise

Run the program in one terminal and observe it in another:

```bash
top
```

If `pidstat` is installed later:

```bash
pidstat -t 1 -p <pid>
```

## Questions To Answer After Running

1. Why is the shared-mutex version slow?
2. Why can the per-thread version be better even though it uses more threads?
3. What does this suggest about queue and buffer ownership in a camera pipeline?
