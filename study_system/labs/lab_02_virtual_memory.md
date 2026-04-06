---
note_type: lab
title: Virtual Memory, Copying, and mmap
track: linux_systems
phase: 1
related_lesson: 2
status: planned
completion: 0
estimated_minutes: 60
actual_minutes: 0
last_run:
next_review:
priority: high
tags:
  - study/lab
  - track/linux
  - phase/1
---

# Lab 2: Virtual Memory, Copying, and `mmap`

## Goal

Build intuition for three things:

- repeated full-buffer copies cost time
- access pattern changes runtime
- `read` and `mmap` move cost around differently

## Build

From `/home/zhixin/code/study_system/labs`:

```bash
make bin/lesson_02_memory
```

## Experiment A: Buffer Copy Cost

Run:

```bash
./bin/lesson_02_memory copy 256 20
```

Try a larger buffer:

```bash
./bin/lesson_02_memory copy 512 20
```

What to observe:

- bigger buffers usually take noticeably longer
- a copy that looks trivial in code is not trivial at runtime

## Experiment B: Sequential vs Poorer Locality

Sequential-like touch:

```bash
./bin/lesson_02_memory touch 256 64 20
```

Larger stride:

```bash
./bin/lesson_02_memory touch 256 4096 20
```

What to observe:

- stride changes runtime
- touching memory sparsely changes locality behavior

## Experiment C: `read` vs `mmap`

Run:

```bash
./bin/lesson_02_memory read_vs_mmap 128 10
```

What to observe:

- the faster one may vary by environment
- `mmap` is not "always faster"
- access pattern and where costs appear both matter

## Optional Tool Exercise

In another terminal:

```bash
vmstat 1
```

While one memory-heavy command is running, observe:

- runnable tasks
- memory activity
- whether the system feels smooth or pressured

## What To Record

- buffer size
- stride or mode
- runtime
- what surprised you
- one connection to image buffers in your work

## Questions To Answer After Running

1. Why can copying be a major bottleneck in image systems?
2. Why is changing stride enough to change runtime?
3. Why should you be cautious about saying "`mmap` is faster" without context?
