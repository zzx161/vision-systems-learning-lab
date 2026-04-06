---
note_type: lesson
title: 虚拟内存、Page、Page Fault 与 mmap
track: linux_systems
phase: 1
lesson: 2
status: planned
completion: 0
estimated_minutes: 120
actual_minutes: 0
last_studied:
next_review:
priority: high
tags:
  - study/lesson
  - track/linux
  - phase/1
---

# 第 2 课：虚拟内存、Page、Page Fault 与 `mmap`

## Why This Matters For You

Camera and image software often handles:

- large frame buffers
- repeated format conversion
- intermediate copies
- file-backed data and logs
- memory pressure under sustained load

If you do not understand memory behavior, many performance problems look random.
Once you understand virtual memory, pages, and copying cost, a lot of runtime behavior becomes easier to reason about.

## Learning Objectives

After this lesson, you should be able to:

1. explain virtual memory in plain language
2. describe what a page is and why page faults cost time
3. explain why copying large buffers is expensive even when code looks simple
4. describe when `mmap` is useful and when it is not
5. connect memory behavior to image and camera pipelines

## Part 1: Virtual Memory in Plain Language

Each process sees its own virtual address space.
That address space looks continuous to the program, but the operating system maps it to real physical pages behind the scenes.

Simple mental model:

- virtual memory is the map your process sees
- physical memory is the actual terrain underneath
- the OS is responsible for translating between them

This helps because:

- processes stay isolated
- memory can be managed flexibly
- files and shared regions can be mapped cleanly

## Part 2: What Is a Page

The operating system manages memory in chunks called pages.

You do not usually work with one byte at a time at the OS level.
You work with pages, even if your code only touches a few bytes.

Why this matters:

- touching one byte may still bring in a whole page
- scattered access can cause extra overhead
- page behavior affects latency and throughput

## Part 3: Page Fault

A page fault happens when the program accesses memory that is not yet mapped in the needed way.
The operating system must step in and handle it.

That handling may include:

- mapping a fresh page
- loading file-backed data
- updating internal structures

Important point:

- page faults are normal
- too many page faults at the wrong time can hurt performance badly

## Part 4: Why Copying Hurts

Many engineers first think performance is dominated by arithmetic.
In real data pipelines, memory movement is often the larger cost.

In image systems, a frame may be:

1. captured
2. copied into a queue
3. converted into another format
4. copied into preprocessing
5. copied again for output

Each copy consumes:

- memory bandwidth
- CPU time
- cache capacity

So a "simple copy" is not a harmless implementation detail.
It is often one of the bottlenecks.

## Part 5: Stack, Heap, and Mapped Memory

### Stack

- thread-local
- fast and structured
- limited in size

### Heap

- dynamic allocation
- common for buffers and objects
- easy to overuse without noticing

### Mapped memory

- memory created through `mmap`
- useful for files, shared memory, or special data handling patterns

The important lesson is not memorizing definitions.
It is learning that different memory regions behave differently in design and debugging.

## Part 6: What `mmap` Gives You

`mmap` lets a process map a file or shared region into its address space.

Why engineers use it:

- avoid some explicit read/copy patterns
- share memory across processes
- simplify access to large file-backed data

But `mmap` is not magical.
It changes how data is accessed and when costs appear.
It does not make bad access patterns disappear.

## Part 7: Camera-Related Mental Model

If a camera pipeline feels slow, ask:

1. How many full-frame copies happen?
2. Which stage owns the original buffer?
3. Are we allocating too often?
4. Are we touching memory in a cache-friendly way?
5. Are page faults or memory pressure appearing under burst load?

This is the systems version of memory thinking.

## Common Misunderstandings

### Misunderstanding 1
"If CPU usage is not high, memory is probably fine."

Correction:
The CPU may be stalled on memory or spending time moving data inefficiently.

### Misunderstanding 2
"A copy is cheap because it is just one line of code."

Correction:
The amount of code is unrelated to the amount of memory traffic.

### Misunderstanding 3
"`mmap` is always faster than normal IO."

Correction:
It depends on access pattern, fault behavior, data size, and how the data is used.

## Lab

Suggested mini-experiments:

1. allocate a large buffer and touch it sequentially
2. allocate a large buffer and touch it with a larger stride
3. compare repeated copying with reusing one buffer
4. compare `read`-based access and `mmap`-based access on a simple file

Read:

- `../labs/lab_02_virtual_memory.md`
- `../labs/src/lesson_02_memory.cpp`

## Suggested Observation Record

Write down:

- buffer size
- access pattern
- runtime
- whether behavior changed after the first run
- what you think happened

## Tool Exercise

Try these:

1. use `time` to compare different runs
2. use `vmstat 1` during a memory-heavy run
3. inspect `/proc/<pid>/status` for memory-related fields

## Review Questions

1. Why does a process use virtual memory instead of directly managing physical memory?
2. Why can page faults add latency?
3. Why is copying large image buffers often a first-class performance problem?
4. What kind of problem can `mmap` help with?
5. Why is memory layout almost as important as algorithm choice in data-heavy code?

## Your Note Template

Write these in your own words:

- Virtual memory:
- Page:
- Page fault:
- Why copying hurts:
- When `mmap` may help:
- One example from my work:

## Next Lesson

Lesson 3 will cover:

- cache hierarchy
- locality
- cache miss intuition
- false sharing
- why memory access patterns dominate performance
