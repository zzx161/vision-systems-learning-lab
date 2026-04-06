---
note_type: lesson
title: CPU, Cache, Locality, and Why Memory Access Dominates Performance
track: architecture
phase: 1
lesson: 3
status: planned
completion: 0
estimated_minutes: 120
actual_minutes: 0
last_studied:
next_review:
priority: high
tags:
  - study/lesson
  - track/architecture
  - phase/1
---

# Lesson 3: CPU, Cache, Locality, and Why Memory Access Dominates Performance

## Why This Matters For You

Image processing, format conversion, and data movement are often limited by memory behavior.
If you understand cache and locality, many "mysterious" performance gaps stop being mysterious.

## Learning Objectives

After this lesson, you should be able to:

1. explain what cache is trying to solve
2. describe spatial and temporal locality in plain language
3. explain why cache misses slow programs down
4. recognize false sharing as a multi-thread performance trap
5. connect memory access pattern to image-processing performance

## Part 1: Why Cache Exists

CPU cores can execute instructions far faster than main memory can deliver data.
Cache exists to reduce that gap.

Simple mental model:

- CPU is a very fast worker
- DRAM is a large but distant warehouse
- cache is the small nearby shelf

If the worker keeps walking back to the warehouse, throughput suffers.

## Part 2: Locality

### Spatial locality
If you access one location, you are likely to access nearby locations soon.

### Temporal locality
If you access one location now, you are likely to access it again soon.

Programs that respect locality usually run better because cache helps them more.

## Part 3: Cache Miss Intuition

When the needed data is not in cache, the CPU must wait much longer.

That means:

- fewer useful instructions retire
- pipelines stall
- runtime increases even if algorithm complexity looks the same on paper

## Part 4: False Sharing

False sharing happens when multiple threads update different variables that sit on the same cache line.
The variables are logically separate, but the hardware still has to coordinate ownership of the shared line.

Result:

- extra coherence traffic
- poor scaling
- confusing slowdown

This is one of the classic reasons multi-threaded code disappoints.

## Part 5: Image and Buffer Example

If you process an image row by row with contiguous access, performance is often decent.
If you jump through memory with poor stride patterns, performance may fall sharply.

Why:

- good locality helps cache
- poor locality causes more misses
- memory traffic starts dominating

## Lab

Suggested mini-experiments:

1. sequential array traversal
2. large-stride traversal
3. two-thread counter update with and without padding

Read:

- `../labs/lab_03_cache_locality.md`
- `../labs/src/lesson_03_cache.cpp`

## Tool Exercise

Use:

- `perf stat`
- `perf top`

Try to observe:

- runtime difference
- cache-related counters if available
- hotspots in hot loops

## Review Questions

1. Why can cache-friendly code beat cache-unfriendly code even with similar algorithmic complexity?
2. What is the difference between spatial and temporal locality?
3. What is false sharing in plain language?
4. Why does this matter for image processing and buffer-heavy systems?

## Next Lesson

Lesson 4 will cover:

- Linux observability tools
- how to inspect CPU, waiting, memory, and syscall behavior
- how to build a first-pass diagnosis flow
