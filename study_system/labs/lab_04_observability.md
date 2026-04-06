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

Terminal A:

```bash
./bin/lesson_04_runtime_shapes cpu 15
```

Terminal B:

```bash
top
```

Observe:

- CPU usage should look high
- the process should look actively running

## Step 2: Run a Sleep-Heavy Program

Terminal A:

```bash
./bin/lesson_04_runtime_shapes sleep 15
```

Terminal B:

```bash
top
```

Observe:

- CPU usage should be much lower
- the process is alive but not doing heavy compute

## Step 3: Run a Mixed Program

Terminal A:

```bash
./bin/lesson_04_runtime_shapes mixed 15
```

Terminal B:

```bash
top
vmstat 1
```

Observe:

- behavior looks different from pure CPU-heavy or pure sleep-heavy
- this is closer to many real systems than a toy pure-CPU loop

## Step 4: Run an IO-Shaped Program

Terminal A:

```bash
./bin/lesson_04_runtime_shapes io 15
```

Terminal B:

```bash
top
vmstat 1
```

Observe:

- some work happens, but it is not the same shape as the CPU-heavy case

## Optional Tool Exercise

If installed later:

```bash
strace -p <pid>
pidstat -t 1 -p <pid>
```

## What To Record

- which mode you ran
- what `top` showed
- what `vmstat` showed
- how you would classify the runtime shape

## Questions To Answer After Running

1. How can you tell CPU-heavy and sleep-heavy programs apart quickly?
2. Why is "the program is slow" not enough information by itself?
3. Which runtime shape feels closest to a real camera pipeline stage?
