---
note_type: lesson
title: 进程、线程、锁与上下文切换
track: linux_systems
phase: 1
lesson: 1
status: active
completion: 15
estimated_minutes: 120
actual_minutes: 0
last_studied: 2026-04-06
next_review: 2026-04-13
priority: high
tags:
  - study/lesson
  - track/linux
  - phase/1
---

# 第 1 课：进程、线程、锁与上下文切换

## Why This Matters For You

You work close to camera input and image processing.
That means your programs often have to:

- receive data continuously
- move large buffers
- coordinate multiple threads
- avoid latency spikes
- avoid frame drops

Many real problems in this kind of system are not "algorithm problems".
They are scheduling, contention, memory, and synchronization problems.

So Lesson 1 is the beginning of system thinking.

## Learning Objectives

After this lesson, you should be able to:

1. explain the difference between process and thread without using textbook wording
2. describe why shared state is both useful and dangerous
3. distinguish race condition, contention, deadlock, and context switching
4. connect multi-thread behavior to frame latency and pipeline stability
5. design a very small experiment to verify your understanding

## Part 1: Process and Thread

### Process
A process is a running program with its own virtual address space and system resources.

Simple mental model:

- different processes are like different apartments
- each apartment has its own space
- going from one apartment to another is relatively expensive

### Thread
A thread is an execution path inside a process.
Threads in the same process share memory and most resources.

Simple mental model:

- threads are like several workers inside the same apartment
- they can use the same table, tools, and whiteboard
- cooperation is easier
- conflict is also easier

## Part 1.5: What Is Actually Shared

When threads live inside one process, they typically share:

- virtual address space
- heap memory
- global variables
- file descriptors
- many process-level resources

But each thread still has its own:

- program counter
- register state
- stack

This matters because:

- sharing makes communication easier
- private execution state makes scheduling possible
- shared heap data is where most bugs and contention appear

## Part 2: Why Engineers Use Threads

Three common reasons:

1. Use multiple CPU cores
2. Separate tasks, such as capture thread, processing thread, and output thread
3. Keep one slow task from blocking the whole pipeline

In camera software, a typical split might be:

- one thread receives frames
- one thread converts or preprocesses data
- one thread sends results downstream

This sounds efficient, but only if data sharing and synchronization are designed well.

## Part 2.5: A Better Pipeline Question

When designing a threaded pipeline, do not only ask:

- how many threads should I create

Also ask:

- where is the queue
- who owns the buffer
- when is a frame copied
- who blocks when downstream becomes slow
- what must be strictly ordered and what can run independently

These are system-engineering questions, and they are more valuable than "how do I add threads quickly".

## Part 3: Why Threads Become Trouble

Threads are useful because they share memory.
Threads are dangerous for the same reason.

Typical problems:

### Race condition
Two threads read and write shared data at the same time without proper coordination.

Result:

- wrong values
- random failures
- hard-to-reproduce bugs

Simple example:

- capture thread updates frame metadata
- processing thread reads the same metadata midway
- output is inconsistent even though both threads "look correct"

### Lock contention
Multiple threads need the same lock and spend time waiting.

Result:

- CPU may still be busy
- throughput drops
- latency rises

Simple example:

- every frame update takes one global mutex
- more worker threads only create more waiting on the same lock

### Deadlock
Two or more threads wait on each other forever.

Result:

- system looks stuck
- no forward progress

Simple example:

- thread A holds queue lock and waits for state lock
- thread B holds state lock and waits for queue lock

### Context switch overhead
The CPU has to stop one thread and continue another.

Result:

- extra overhead
- cache disruption
- latency jitter

Simple example:

- several runnable threads fight for CPU time
- hot data leaves cache more often
- frame-to-frame timing becomes uneven

## Part 4: Context Switch in Plain Language

The CPU cannot run every runnable thread at the exact same time.
When it switches from one thread to another, it needs to save current execution state and restore another one.

This is called a context switch.

Why it matters:

- it has direct overhead
- it breaks cache locality
- frequent switching can make a system feel unstable under load

Practical intuition:

- a single context switch is normal
- too many context switches often signal oversubscription, lock-heavy design, or excessive waiting/wakeup behavior

For a camera pipeline, this means:

- frame handling may become uneven
- one stage may suddenly lag
- you may see intermittent delay or frame drops

## Part 5: The Most Important Mental Model

When multi-threaded code becomes slow, do not ask only:

"How do I make this code run in parallel?"

Ask these first:

1. What data is shared?
2. Who owns each buffer?
3. Where do threads wait?
4. Is the bottleneck compute, memory, or coordination?
5. Is extra threading helping, or just adding contention?

That shift in thinking is what separates feature coding from systems engineering.

## Part 5.5: A First Debugging Checklist

When multi-thread code is slower than expected, check:

1. Are there more runnable threads than CPU cores?
2. Is one global lock protecting too much work?
3. Is data being copied between stages more than necessary?
4. Are threads waking each other too often for tiny pieces of work?
5. Is one slow stage causing backpressure through the whole pipeline?

This checklist will come back again in later lessons.

## Part 6: Camera-Related Example

Imagine this pipeline:

1. capture thread reads camera frames
2. processing thread does format conversion
3. output thread sends frames to downstream

Now imagine all three stages use one shared queue protected by one mutex.

Possible result:

- capture thread waits for lock
- processing thread waits for data
- output thread occasionally blocks the others
- even if CPU usage is not full, frame latency still increases

This is why "more threads" does not automatically mean "faster pipeline".

## Part 6.5: How This Shows Up In Real Work

In camera and image systems, symptoms often look like this:

- CPU is not full, but latency is still bad
- average runtime looks okay, but tail latency is terrible
- frame drops only appear under burst load
- adding one more worker thread makes performance worse

These symptoms usually point to:

- contention
- poor queue design
- too many copies
- scheduling jitter
- poor ownership boundaries

## Part 7: What You Need To Remember

### Key Conclusion 1
Threads improve concurrency, but shared data creates coordination cost.

### Key Conclusion 2
Performance problems are often caused by contention and memory movement, not raw computation.

### Key Conclusion 3
To debug multi-thread systems, you need to observe waiting, contention, and switching behavior.

## Common Misunderstandings

### Misunderstanding 1
"More threads means better performance."

Correction:
More threads only help when useful work scales and coordination cost stays low.

### Misunderstanding 2
"CPU usage is not full, so the program is not bottlenecked."

Correction:
A program can be bottlenecked by waiting, lock contention, memory stalls, or poor pipeline structure.

### Misunderstanding 3
"If it works functionally, the threading design is probably fine."

Correction:
Functional correctness and runtime quality are different questions.
A correct design can still have bad latency and instability.

## Lab

Read:

- `../labs/lab_01_threads.md`
- `../labs/src/lesson_01_threads.cpp`

What you should do:

1. build one single-thread version
2. build one shared-counter multi-thread version
3. build one per-thread-counter version
4. compare runtime
5. write your explanation

## Suggested Lab Record Format

Record these fields:

- hardware and CPU core count
- number of threads
- total increments or total work
- measured runtime
- what you expected before running
- what actually happened
- your explanation after seeing the result

## Tool Exercise

After running the lab, also try:

1. run `top` and observe CPU usage while the program runs
2. run `pidstat -t 1 -p <pid>` for a longer-running version
3. compare whether the shared-lock version creates more waiting behavior

Do not worry if the signals are noisy.
The goal is simply to start looking at runtime behavior instead of only looking at code.

## Review Questions

1. Why are threads cheaper to communicate with than processes?
2. Why can a multi-thread version be slower than a single-thread version?
3. What is the difference between race condition and lock contention?
4. Why can context switching hurt latency in a camera pipeline?

## Self-Test

If you can answer these without looking back, you probably understood the core:

1. Why do threads share heap memory but not stack memory?
2. Why can one global mutex destroy parallelism?
3. Why can low CPU usage still come with bad throughput?
4. What would you inspect first in a multi-stage camera pipeline that sometimes drops frames?

## Your Note Template

Write these in your own words:

- Process:
- Thread:
- Lock contention:
- Context switch:
- One example from my work:

## Work Connection Prompt

Think of one real module from your work and answer:

1. Where are the threads?
2. What data is shared?
3. Where might contention happen?
4. Where might wakeups or waiting happen?
5. If frame drops happen, which stage would you inspect first?

## Next Lesson

Lesson 2 will cover:

- virtual memory
- pages
- page faults
- `mmap`
- why copying data hurts systems performance
