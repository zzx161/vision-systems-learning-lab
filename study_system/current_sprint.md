---
note_type: sprint
title: Current Sprint
phase: 1
sprint: week_01
status: active
completion: 10
estimated_minutes: 480
actual_minutes: 0
started_on: 2026-04-06
target_end: 2026-04-12
priority: high
tags:
  - study/sprint
  - phase/1
---

# Current Sprint

## Sprint Goal

Build a strong and practical foundation in:

1. Processes and threads
2. Virtual memory
3. Basic observability tools
4. System thinking for camera pipelines

## Week 1 Focus

### Topic A: Processes and Threads
- Understand the difference between process and thread
- Understand why context switch costs time
- Learn mutex, condition variable, and atomics at a practical level

### Topic B: Virtual Memory
- Understand virtual address vs physical memory intuition
- Understand page faults and why `mmap` matters
- Understand why copying large buffers is expensive

### Topic C: First Debugging Toolkit
- Learn `top`
- Learn `ps`
- Learn `pidstat`
- Learn `vmstat`

## This Sprint Has 4 Mini-Lessons

1. `courses/lesson_01_process_thread.md`
2. `courses/lesson_02_virtual_memory.md`
3. `courses/lesson_03_cache_and_locality.md`
4. `courses/lesson_04_linux_observability.md`

## Suggested Weekly Rhythm

### Day 1
- Read Lesson 1
- Write down your own explanation of process vs thread

### Day 2
- Do the first thread lab
- Record your observations

### Day 3
- Read Lesson 2
- Mark any part that still feels abstract

### Day 4
- Do one small memory experiment
- Compare at least two access or copy patterns

### Day 5
- Read Lesson 3
- Connect cache/locality ideas to image processing

### Day 6
- Read Lesson 4
- Use `top`, `pidstat`, and `vmstat` on one toy program

### Day 7
- Fill in `reviews/week_01_review.md`
- Re-answer review questions without looking

## Deliverables

- Read the route in `integrated_route.md`
- Read the lesson plan in `course_plan.md`
- Read Lesson 1 in `courses/lesson_01_process_thread.md`
- Read Lesson 2 in `courses/lesson_02_virtual_memory.md`
- Read Lesson 3 in `courses/lesson_03_cache_and_locality.md`
- Read Lesson 4 in `courses/lesson_04_linux_observability.md`
- Read the notes in `memory/module_01_process_thread.md`
- Read the notes in `memory/module_02_virtual_memory.md`
- Complete Lab 1 in `labs/lab_01_threads.md`
- Complete Lab 2 in `labs/lab_02_virtual_memory.md`
- Complete Lab 3 in `labs/lab_03_cache_locality.md`
- Complete Lab 4 in `labs/lab_04_observability.md`
- Write your own summary in `reviews/week_01_review.md`

## Done Criteria

You should be able to explain:

- Why threads share memory but processes usually do not
- Why lock contention can make multi-threading slower
- Why virtual memory helps but also introduces page behavior
- Why access pattern changes performance even for similar code
- Which tools to use when CPU is high or a process looks stuck
