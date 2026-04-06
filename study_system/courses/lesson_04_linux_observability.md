---
note_type: lesson
title: Linux Observability for Engineers
track: linux_tools
phase: 1
lesson: 4
status: planned
completion: 0
estimated_minutes: 100
actual_minutes: 0
last_studied:
next_review:
priority: medium
tags:
  - study/lesson
  - track/linux
  - phase/1
---

# Lesson 4: Linux Observability for Engineers

## Why This Matters For You

Systems knowledge becomes valuable only when you can use it to inspect a real running program.

This lesson gives you the first practical toolbox for:

- CPU spikes
- stuck processes
- waiting-heavy behavior
- memory-pressure signals
- first-pass runtime diagnosis

## Learning Objectives

After this lesson, you should be able to:

1. choose a reasonable first tool for a runtime symptom
2. use `top`, `pidstat`, `vmstat`, `strace`, and `perf` at a basic level
3. distinguish CPU-heavy and waiting-heavy programs
4. write a first-pass diagnosis flow for common runtime issues

## Part 1: Observability Mindset

Do not start with guesses like:

- maybe the algorithm is slow
- maybe C++ is inefficient

Start with observation:

1. Is CPU high or low?
2. Is the process running or sleeping?
3. Are threads busy or mostly waiting?
4. Is memory pressure visible?
5. Are syscalls or locks dominating?

## Part 2: Tool Roles

### `top`
Use when you want a fast global view.

Good for:

- CPU usage
- rough memory usage
- whether the process is active

### `pidstat`
Use when you want per-process or per-thread behavior over time.

Good for:

- thread-level CPU patterns
- seeing whether one thread is the hotspot

### `vmstat`
Use when you want system-level memory and scheduling signals.

Good for:

- runnable tasks
- blocking
- memory-related pressure

### `strace`
Use when you suspect the program is waiting in syscalls.

Good for:

- file IO waits
- sleep behavior
- repeated syscall patterns

### `perf`
Use when you need function-level or event-level performance clues.

Good for:

- hotspots
- instruction and event statistics
- CPU-side performance analysis

## Part 3: Symptom to Tool Mapping

If CPU is high:

- start with `top`
- then `pidstat`
- then `perf`

If the process looks stuck:

- start with `ps`
- then `strace`

If the system feels jittery:

- start with `vmstat`
- then `pidstat`

If one pipeline stage seems unexpectedly slow:

- start with `pidstat`
- then `perf`

## Lab

Pick or write:

1. one CPU-heavy program
2. one waiting-heavy program

Then inspect both with:

- `top`
- `pidstat`
- `strace`

Write down how the signals differ.

Read:

- `../labs/lab_04_observability.md`
- `../labs/src/lesson_04_runtime_shapes.cpp`

## Deliverable

Write a simple diagnosis flow:

- If CPU is high, I will check ...
- If the process is stuck, I will check ...
- If latency becomes unstable, I will check ...

## Review Questions

1. When is `pidstat` more useful than `top`?
2. What kind of question is `strace` good at answering?
3. Why should observation come before optimization?
4. Which tools would you try first for frame-drop investigation on Linux?
