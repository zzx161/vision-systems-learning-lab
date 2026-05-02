---
note_type: lab
title: First Observability Practice
track: linux_tools
phase: 1
related_lesson: 4
status: planned
completion: 0
estimated_minutes: 45
actual_minutes: 0
last_run:
next_review:
priority: medium
tags:
  - study/lab
  - track/linux
  - phase/1
---

# Lab 4: First Observability Practice

## Goal

Learn to recognize different runtime shapes:

- CPU-heavy
- sleep-heavy
- mixed
- IO-shaped

## Build

From `/home/zhixin/code/study_system/labs`:

```bash
make bin/lesson_04_runtime_shapes
```

## Step 1: Run a CPU-Heavy Program

### How To Run

Terminal A runs the workload:

```bash
./bin/lesson_04_runtime_shapes cpu 15
```

Terminal B observes it with `top`.
First find the PID:

```bash
pgrep -f './bin/lesson_04_runtime_shapes cpu 15'
```

Then watch only that process:

```bash
top -p <pid>
```

You can also use `pidstat`:

```bash
pidstat -p <pid> -u -w 1
```

For a system-wide view:

```bash
vmstat 1
```

### What To Look At

- In `top`, look at `S` and `%CPU`.
- In `pidstat`, look at `%usr`, `%system`, `%CPU`, `cswch/s`, and `nvcswch/s`.
- In `vmstat`, look at `r`, `us`, `sy`, `id`, `wa`, and `cs`.

### How To Interpret

- `top` shows `S=R` and high `%CPU`: the process is running on CPU.
- `pidstat` shows high `%usr`: most time is user-space computation.
- `cswch/s` is low: it is not voluntarily sleeping often.
- `vmstat us` rises and `id` falls: CPU is doing user-space work.

Conclusion:

```text
This is CPU-heavy. If a real program looks like this, next suspect algorithm
hotspots, tight loops, image processing, or inference runtime.
```

## Step 2: Run a Sleep-Heavy Program

### How To Run

Terminal A:

```bash
./bin/lesson_04_runtime_shapes sleep 15
```

Terminal B:

```bash
pgrep -f './bin/lesson_04_runtime_shapes sleep 15'
top -p <pid>
pidstat -p <pid> -u -w 1
vmstat 1
```

### What To Look At

- In `top`, look at `S` and `%CPU`.
- In `pidstat`, look at `%CPU` and `cswch/s`.
- In `vmstat`, look at `id`, `wa`, and `cs`.

### How To Interpret

- `top` shows `S=S` and low `%CPU`: the process is sleeping/waiting.
- `pidstat %CPU` is near zero: it is not computing.
- `pidstat cswch/s` is higher: it voluntarily gives up CPU when sleeping.
- `vmstat id` stays high: the system is mostly idle.

Conclusion:

```text
This is wait-heavy. If a real program looks like this, do not start with CPU
profiling. First ask what it is waiting for: timer, queue, lock, IO, camera frame,
or downstream response.
```

## Step 3: Run a Mixed Program

### How To Run

Terminal A:

```bash
./bin/lesson_04_runtime_shapes mixed 15
```

Terminal B:

```bash
pgrep -f './bin/lesson_04_runtime_shapes mixed 15'
top -p <pid>
pidstat -p <pid> -u -w 1
vmstat 1
```

### What To Look At

- In `top`, watch whether `%CPU` is between the CPU-heavy and sleep-heavy cases.
- In `pidstat`, compare `%usr` and `cswch/s`.
- In `vmstat`, watch `us`, `id`, and `cs`.

### How To Interpret

- Some CPU plus regular voluntary context switches means the program alternates between work and waiting.
- If `%CPU` is still very low, the current workload is more wait-heavy than mixed.
- Sampling tools may catch only the sleep part, so compare several samples or use `/usr/bin/time -v`.

Helpful summary command:

```bash
/usr/bin/time -v ./bin/lesson_04_runtime_shapes mixed 15
```

Look at:

- `User time`
- `System time`
- `Percent of CPU`
- `Voluntary context switches`

Conclusion:

```text
Many real pipeline stages are mixed: compute a little, wait for data, compute
again, then wait for output. Do not classify them using only one top sample.
```

## Step 4: Run an IO-Shaped Program

### How To Run

Terminal A:

```bash
./bin/lesson_04_runtime_shapes io 15
```

Terminal B:

```bash
pgrep -f './bin/lesson_04_runtime_shapes io 15'
top -p <pid>
pidstat -p <pid> -u -w 1
vmstat 1
```

Use `strace` when you want to see system calls:

```bash
strace -p <pid>
```

If the program is short, run it directly under `strace`:

```bash
strace ./bin/lesson_04_runtime_shapes io 3
```

### What To Look At

- In `top`, `%CPU` may be low or moderate.
- In `pidstat`, `%system` may rise if kernel work is significant.
- In `vmstat`, `wa` may rise if real storage IO is waiting.
- In `strace`, look for repeated `open`, `read`, `write`, `poll`, `ioctl`, `futex`, or similar calls.

### How To Interpret

- Low `%CPU` does not mean no work; the process may be waiting on IO.
- High `%system` points toward kernel/system-call work.
- High `wa` points toward IO wait at the system level.
- `strace` tells you what kind of kernel call the program is making or waiting in.

Conclusion:

```text
This is IO-shaped. In camera systems, similar shapes often appear as read, poll,
ioctl, SDK calls, file writes, network sends, or device waits.
```

## Optional Tool Exercise

Useful process/thread tools:

```bash
pidstat -t 1 -p <pid>
pidstat -p <pid> -u -w 1
strace -p <pid>
```

`pidstat -t` splits by thread when the process has multiple threads.
`pidstat -u -w` shows CPU and context switches.
`strace -p` attaches to a running process and shows system calls.

If attaching with `strace -p` is blocked by permissions, run the program directly under `strace`.

## What To Record

- which mode you ran
- what `top` showed
- what `vmstat` showed
- how you would classify the runtime shape

## Questions To Answer After Running

1. How can you tell CPU-heavy and sleep-heavy programs apart quickly?
2. Why is "the program is slow" not enough information by itself?
3. Which runtime shape feels closest to a real camera pipeline stage?
