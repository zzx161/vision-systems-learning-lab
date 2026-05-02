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

Run the legacy comparison:

```bash
./bin/lesson_02_memory read_vs_mmap 128 10
```

What to observe:

- `read` repeats the full read each round
- `mmap` maps once and reuses the same mapping
- this mode shows why repeated full reads are expensive, not that `mmap` is always better

Run a cleaner one-pass comparison:

```bash
./bin/lesson_02_memory read_vs_mmap_once 128
```

What to observe:

- both paths touch the data once
- results may be closer than in the legacy repeated-read mode
- the faster one can vary by filesystem, cache state, and machine

Run a repeated-touch comparison:

```bash
./bin/lesson_02_memory read_vs_mmap_repeated 128 10
```

What to observe:

- `read` loads the file into a user buffer once, then touches that buffer repeatedly
- `mmap` maps the file once, then touches the mapping repeatedly
- this is closer to comparing repeated access after setup

Split `mmap` setup from first touch:

```bash
./bin/lesson_02_memory mmap_phases 128 10
```

What to observe:

- `mmap` setup itself is usually very cheap
- the first touch is where page costs show up
- repeated touches are often much cheaper once pages are resident

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
3. In `mmap_phases`, why is setup cheap but first touch more expensive?
4. Why should you be cautious about saying "`mmap` is faster" without context?
