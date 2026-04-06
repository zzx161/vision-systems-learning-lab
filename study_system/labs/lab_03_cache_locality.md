---
note_type: lab
title: Cache, Locality, and False Sharing
track: architecture
phase: 1
related_lesson: 3
status: planned
completion: 0
estimated_minutes: 60
actual_minutes: 0
last_run:
next_review:
priority: high
tags:
  - study/lab
  - track/architecture
  - phase/1
---

# Lab 3: Cache, Locality, and False Sharing

## Goal

See three ideas become concrete:

- locality affects speed
- larger stride usually hurts cache behavior
- independent-looking threads can still interfere through false sharing

## Build

From `/home/zhixin/code/study_system/labs`:

```bash
make bin/lesson_03_cache
```

## Experiment A: Stride and Locality

Good locality:

```bash
./bin/lesson_03_cache stride 256 1 20
```

Poorer locality:

```bash
./bin/lesson_03_cache stride 256 16 20
./bin/lesson_03_cache stride 256 64 20
```

What to observe:

- runtime often increases as stride grows
- the code is still "simple", but memory behavior changed

## Experiment B: False Sharing

Run:

```bash
./bin/lesson_03_cache false_sharing 200000000
```

What to observe:

- the shared-cache-line version can be slower
- the padded version reduces interference between threads

## Optional Tool Exercise

If `perf` becomes available later:

```bash
perf stat ./bin/lesson_03_cache stride 256 1 20
perf stat ./bin/lesson_03_cache stride 256 64 20
```

## What To Record

- stride
- runtime
- false-sharing result
- your explanation using "cache line" and "locality"

## Questions To Answer After Running

1. Why can two loops with similar logic run very differently?
2. What is false sharing in your own words?
3. Where might false sharing appear in camera or image-processing code?
