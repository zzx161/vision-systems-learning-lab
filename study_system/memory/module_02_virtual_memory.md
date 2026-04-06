# Module 2: Virtual Memory

## What Problem This Solves

This module helps you understand:

- why large buffers are expensive
- why memory usage and memory performance are not the same thing
- why `mmap` and shared memory matter in systems work

## Core Ideas

### Virtual Memory
Each process sees a continuous virtual address space.
The operating system maps those virtual addresses to physical memory pages.

### Page
Memory is managed in fixed-size chunks called pages.

### Page Fault
When the CPU touches a page that is not currently mapped as needed, the OS must handle it.
That handling has cost.

### Anonymous Memory
Memory not backed by a file, like heap allocations.

### File Mapping
`mmap` can map file content or shared regions into a process address space.

## Practical Mental Model

When memory problems appear, ask:

1. Is memory usage too high?
2. Is copying too frequent?
3. Are page faults happening at a bad time?
4. Is the access pattern cache-friendly?

## What To Remember

- Memory movement is often the real cost.
- A "simple copy" may dominate runtime in data-heavy systems.
- Good layout and fewer copies matter a lot in camera and image pipelines.

## Review Questions

1. Why is virtual memory useful?
2. What is a page fault in simple terms?
3. Why can repeated buffer copying be expensive?
4. When might `mmap` be useful?
