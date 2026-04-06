# Course Plan

## Course Goal

This course is built for your background:

- camera application and camera data access
- chip interface and system-side debugging
- image processing engineering
- desire to avoid pure algorithm competition

The target is not "learn random knowledge".
The target is to grow into a stronger engineer in this direction:

camera system engineering -> Linux/system performance -> edge AI deployment -> robotics vision transferability

## What You Will Be Able To Do

After finishing the full route, you should be able to:

1. explain the main runtime bottlenecks in camera and image pipelines
2. diagnose common Linux-side performance issues with tools
3. reason about latency, throughput, contention, copying, and cache effects
4. understand how model deployment interacts with system bottlenecks
5. build enough robotics vision awareness to keep career mobility high

## Course Design Principles

This course is not book-first.
It is built around durable understanding.

Each lesson has five layers:

1. Why it matters for your real work
2. Core concepts and mental models
3. A small lab or tool exercise
4. Review and recall
5. A written note in your own words

The goal is to turn knowledge into:

- intuition
- debugging habits
- reusable memory

## Recommended Rhythm

For a full-time engineer, use this pace:

- workdays: 30 minutes
- weekend: 2 to 4 focused hours

For each lesson:

### Session 1
- Read the lesson
- Understand the mental model
- Mark what feels fuzzy

### Session 2
- Do the small lab
- Record what you observed

### Session 3
- Use one tool or run one measurement
- Connect the lesson to one problem from work

### Session 4
- Write your own summary
- Answer review questions from memory

## Phase Overview

### Phase 1: System Foundation
Goal:
Build strong intuition about concurrency, memory, cache, and Linux observability.

Why this phase matters:
This is the layer that helps you solve "why is it slow", "why does it jitter", and "why does it drop frames".

### Phase 2: Camera and Deployment Engineering
Goal:
Connect system knowledge to camera pipelines and deployed inference.

Why this phase matters:
This is where you become a bridge between camera data, runtime behavior, and edge deployment.

### Phase 3: Robotics Vision Transition
Goal:
Create a second career curve without throwing away your current experience.

Why this phase matters:
This gives you transferability into robotics and industrial vision.

## Full Lesson Map

## Phase 1: System Foundation

### Lesson 1: Processes, Threads, Locks, and Context Switching

Why it matters:
Most camera and image-processing systems are multi-threaded.
Many problems come from waiting, sharing, and switching rather than raw compute.

You will learn:

- process vs thread
- shared memory and ownership
- race condition vs lock contention
- context switching in plain language
- how to think about pipeline concurrency

Hands-on:

- compare single-thread, shared-lock, and low-contention versions

Deliverable:

- explain in your own words why more threads can make things slower

Tools:

- `top`
- `ps`
- `pidstat`

### Lesson 2: Virtual Memory, Pages, Page Faults, and `mmap`

Why it matters:
Large image buffers and repeated copies dominate many real systems.

You will learn:

- virtual memory intuition
- page and page fault basics
- heap vs stack vs mapped memory
- why copying hurts
- when `mmap` becomes useful

Hands-on:

- compare simple file reading with mapped access
- observe memory behavior with large buffers

Deliverable:

- explain why memory movement is a systems bottleneck

Tools:

- `vmstat`
- `/proc/<pid>/status`
- `time`

### Lesson 3: CPU, Cache, Locality, and Why Memory Access Dominates Performance

Why it matters:
Image and buffer-heavy code often loses to memory access, not arithmetic.

You will learn:

- cache hierarchy
- cache line
- locality
- cache miss intuition
- false sharing

Hands-on:

- compare sequential access and poor-locality access
- observe the effect of different data layouts

Deliverable:

- explain why "same algorithm complexity" can have very different runtime

Tools:

- `perf stat`
- `perf top`

### Lesson 4: Linux Observability for Engineers

Why it matters:
Knowing concepts is not enough.
You need to know how to see what the system is doing.

You will learn:

- when to use `top`, `pidstat`, `vmstat`, `iostat`
- how to use `strace` to identify waiting
- what `perf` tells you
- how to start narrowing a bottleneck

Hands-on:

- inspect one CPU-heavy program
- inspect one waiting-heavy program
- write down a first-pass diagnosis flow

Deliverable:

- build your first troubleshooting checklist

Tools:

- `top`
- `pidstat`
- `vmstat`
- `strace`
- `perf`

## Phase 2: Camera and Deployment Engineering

### Lesson 5: Camera Data Path, Buffers, and Frame Lifecycle

Why it matters:
You already work near this layer.
This lesson helps you see the whole path as one system.

You will learn:

- sensor to ISP to memory intuition
- frame lifecycle and buffering
- producer-consumer thinking
- where latency accumulates

Hands-on:

- draw one real pipeline from your work
- mark ownership, queueing, and copy points

Deliverable:

- one pipeline map in your own words

### Lesson 6: Latency, Jitter, Frame Drops, and Synchronization

Why it matters:
Many hard production issues are timing problems, not functional problems.

You will learn:

- latency vs throughput
- jitter
- backpressure
- frame drop causes
- synchronization mindset

Hands-on:

- analyze one imaginary or real frame-drop scenario

Deliverable:

- write a structured diagnosis approach for unstable frame timing

### Lesson 7: ONNX and Inference Runtime Basics for System Engineers

Why it matters:
This is your bridge into edge AI deployment without becoming a pure algorithm engineer.

You will learn:

- what ONNX is
- basic inference runtime flow
- operator execution intuition
- deployment pipeline overview

Hands-on:

- trace a simple model export and runtime path conceptually

Deliverable:

- explain where system bottlenecks can appear in inference deployment

### Lesson 8: Quantization, TensorRT, and Platform Toolchains

Why it matters:
This is where deployment value becomes practical on real hardware.

You will learn:

- quantization intuition
- accuracy vs latency tradeoff
- engine building basics
- platform-specific deployment mindset

Hands-on:

- compare FP and INT deployment tradeoffs conceptually or through a small example

Deliverable:

- explain what can be optimized without touching model training

### Lesson 9: Profiling Deployed Inference

Why it matters:
A deployed model can be "correct" but still unusable if the pipeline is slow or unstable.

You will learn:

- CPU bottleneck vs bandwidth bottleneck
- memory copy cost in inference pipelines
- preprocessing and postprocessing overhead
- first-pass runtime diagnosis

Hands-on:

- break down latency into stages

Deliverable:

- one latency budget template for deployment tasks

## Phase 3: Robotics Vision Transition

### Lesson 10: ROS2 Basics for Vision Engineers

Why it matters:
ROS2 is a practical entry point into robotics systems.

You will learn:

- pub/sub model
- node thinking
- topic flow
- launch-system awareness

Hands-on:

- draw a simple camera-to-processing-to-output ROS2 graph

Deliverable:

- explain how your current pipeline experience maps onto robotics middleware

### Lesson 11: Calibration, Hand-Eye Calibration, and 3D Vision Awareness

Why it matters:
This is a transferable systems skill for robotics and industrial vision.

You will learn:

- calibration purpose
- intrinsics and extrinsics intuition
- hand-eye calibration awareness
- why 3D vision changes system assumptions

Hands-on:

- explain one calibration problem in plain language

Deliverable:

- one short note on where calibration failures show up in a product

### Lesson 12: End-to-End Project Design

Why it matters:
Knowledge becomes durable when it is integrated.

You will learn:

- how to choose a small project
- how to split it into system, runtime, and debugging tasks
- how to document what you built

Hands-on:

- define one personal project and its milestones

Deliverable:

- one project brief with technical goals and learning goals

## Milestones

### Milestone A
Finish Lessons 1 to 4.

You should be able to:

- explain concurrency and memory bottlenecks
- use basic Linux tools to inspect runtime behavior
- reason about cache and copying effects

### Milestone B
Finish Lessons 5 to 9.

You should be able to:

- analyze a camera or deployment pipeline as a system
- discuss latency and bottleneck sources with more confidence
- approach edge deployment from a system-engineering angle

### Milestone C
Finish Lessons 10 to 12.

You should be able to:

- describe a credible robotics vision transition path
- design a portfolio-quality learning project

## Standard Lesson Output

For each lesson, you should leave behind:

1. one concept summary
2. one experiment or tool observation
3. one work-related example
4. one set of answered review questions

## Current Active Lesson

Lesson 1
