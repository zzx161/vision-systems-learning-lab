---
note_type: lab
title: Scheduling, Affinity, and Tail Latency
track: linux_systems
phase: 2
related_lesson: 6
status: done
completion: 100
estimated_minutes: 50
actual_minutes: 15
last_run: 2026-05-02
next_review: 2026-05-09
priority: high
tags:
  - study/lab
  - track/linux
  - phase/2
---

# Lab 6: Scheduling, Affinity, and Tail Latency

## Goal

See why average latency is not enough.

This lab simulates a periodic frame-processing thread:

1. A frame is released every fixed period.
2. The main thread wakes up and does a fixed amount of CPU work.
3. Optional background threads create CPU interference.
4. The program prints average, p50, p90, p99, max, and missed deadlines.

## Code Links

- Source: [`src/lesson_06_tail_latency.cpp`](src/lesson_06_tail_latency.cpp)
- Build rule: [`Makefile`](Makefile)

## Build

From `/home/zhixin/code/study_system/labs`:

```bash
make bin/lesson_06_tail_latency
```

## Experiment 1: Baseline

### How To Run

```bash
./bin/lesson_06_tail_latency 300 10 2000 0
```

Arguments:

- `300`: number of frames
- `10`: one frame every 10 ms
- `2000`: each frame does about 2000 us of CPU work
- `0`: no background interference threads

### What To Look At

Look at:

- `frame_latency_us avg`
- `frame_latency_us p99`
- `frame_latency_us max`
- `missed_deadlines`
- `start_jitter_us p99`

### How To Interpret

The deadline is the period: `10 ms = 10000 us`.

If `p99` and `max` are far below `10000`, this simulated pipeline is stable.
If `missed_deadlines` is greater than zero, some frames missed their period.

## Experiment 2: Add Background CPU Interference

### How To Run

```bash
./bin/lesson_06_tail_latency 300 10 2000 4
```

### What To Look At

Compare with Experiment 1:

- Did `avg` change a little or a lot?
- Did `p99` change more than `avg`?
- Did `max` become much worse?
- Did `start_jitter_us` increase?

### How To Interpret

If `avg` is acceptable but `p99` or `max` becomes much worse, this is a tail
latency problem.

If `start_jitter_us` grows, the main thread is waking up late or not getting CPU
quickly enough.

## Experiment 3: Try CPU Affinity

### How To Run

Pin the main thread to CPU 0 and background work to CPU 1:

```bash
./bin/lesson_06_tail_latency 300 10 2000 4 0 1
```

### What To Look At

Compare with Experiment 2:

- Does `start_jitter_us p99` improve?
- Does `frame_latency_us p99` improve?
- Does `max` become less extreme?
- Are deadlines still missed?

### How To Interpret

Affinity can reduce interference, but it is not guaranteed to help.

It helps when the main issue is scheduling interference or migration. It may not
help if the real bottleneck is CPU capacity, memory bandwidth, a lock, or a
device queue.

## Experiment 4: Overload The Period

### How To Run

Make the per-frame work close to the period:

```bash
./bin/lesson_06_tail_latency 300 10 9000 0
```

Then add interference:

```bash
./bin/lesson_06_tail_latency 300 10 9000 2
```

### What To Look At

- `missed_deadlines`
- `p99`
- `max`

### How To Interpret

When work is close to the deadline, the system has little slack.
Even small scheduling delays can make tail latency much worse.

## Key Conclusion

For realtime-ish systems:

```text
avg tells you the normal case.
p99/max tell you whether the system occasionally hurts you.
start_jitter tells you whether the thread starts late.
missed_deadlines tells you whether the pipeline violated its time budget.
```
