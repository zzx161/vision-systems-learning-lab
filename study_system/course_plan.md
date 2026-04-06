# Course Plan

## Positioning

This is not a generic CS survey.
It is a career-facing learning path built around your real background:

- camera application development
- chip-side integration and interface debugging
- image pipeline engineering
- desire to avoid pure algorithm competition

The route is designed to help you become a stronger systems engineer with two clear growth directions:

1. go deeper into camera and Linux systems engineering
2. extend into edge AI deployment and robotics vision without switching to a pure algorithm role

## What Makes This Course Different

This course follows the structure that strong modern learning platforms often use:

- path-based learning instead of isolated topics
- concrete outcomes for every lesson
- small projects and portfolio artifacts
- repeated review instead of one-time reading
- checkpoints that connect directly to work problems

The idea is simple:
every lesson should give you one durable mental model, one observable experiment, and one written artifact.

## Final Outcome

By the end of the full path, you should be able to:

1. explain the main bottlenecks in a camera and image-processing pipeline
2. diagnose Linux-side performance issues with the right tools instead of guessing
3. reason about latency, throughput, copying, cache effects, contention, and backpressure
4. understand how edge deployment interacts with memory bandwidth, preprocessing, and runtime stability
5. design a small but convincing portfolio project that shows systems thinking rather than pure coding

## Learning Experience Design

Each lesson has the same structure:

1. Why this matters in your real work
2. Core concepts and mental models
3. A practical task, lab, or drawing exercise
4. A deliverable you can keep
5. Review questions for long-term memory

Each phase ends with a milestone artifact:

- Phase 1:
  A Linux performance troubleshooting checklist
- Phase 2:
  A camera-to-runtime bottleneck map
- Phase 3:
  A small project brief or demo system plan

## Recommended Pace

For a full-time engineer, the best rhythm is:

- workdays:
  30 to 40 minutes
- weekend:
  2 to 4 focused hours

Recommended pattern for one lesson:

### Session 1

- read the lesson
- mark fuzzy concepts
- rewrite the key model in your own words

### Session 2

- do the lab or practical task
- record observations
- note one thing that surprised you

### Session 3

- connect the lesson to one real problem from work
- capture a checklist or diagnosis flow

### Session 4

- answer review questions from memory
- write one short summary note

## Three Learning Tracks

### Track A: Linux and Systems Foundation

Goal:
build intuition about concurrency, memory, cache, scheduling, and observability.

Career value:
this is the part that makes you useful when a real system becomes unstable, slow, or hard to explain.

### Track B: Camera Systems and Edge Deployment

Goal:
connect your existing camera background with runtime behavior, inference deployment, and platform constraints.

Career value:
this is where you become a bridge between sensor data, systems performance, and deployed AI.

### Track C: Robotics and 3D Vision Transfer

Goal:
open a second career curve in robotics and industrial vision while reusing your current strengths.

Career value:
this gives you mobility beyond a single industry cycle.

## Phase Overview

## Phase 1: System Foundation

Goal:
understand why systems become slow, unstable, and jittery even when the code looks reasonable.

Milestone artifact:
build your own troubleshooting flow for CPU spikes, contention, memory pressure, and waiting.

## Phase 2: Camera and Deployment Engineering

Goal:
understand the camera data path, timing behavior, and deployment bottlenecks as one connected system.

Milestone artifact:
produce a bottleneck map from camera input to inference output.

## Phase 3: Robotics Vision Transition

Goal:
gain transferability into robotics through middleware, calibration, and a scoped project.

Milestone artifact:
finish one end-to-end project brief or prototype plan suitable for a public portfolio.

## Full Lesson Map

| Lesson | Theme | Core Question | Main Deliverable |
| --- | --- | --- | --- |
| 1 | Processes, threads, locks, context switching | Why can more threads make things slower? | concurrency checklist |
| 2 | Virtual memory, pages, `mmap` | Why is moving memory often the real bottleneck? | memory movement note |
| 3 | CPU cache and locality | Why can the same algorithm run very differently? | cache intuition summary |
| 4 | Linux observability | How do I see what the system is doing? | first troubleshooting flow |
| 5 | Camera data path and buffers | Where does one frame really travel? | pipeline ownership map |
| 6 | Latency, jitter, sync, drops | Why does frame timing become unstable? | timing diagnosis template |
| 7 | ONNX and runtime basics | What happens between a model file and real execution? | deployment path sketch |
| 8 | Quantization and toolchains | What trade-offs turn a model into a product? | deployment decision matrix |
| 9 | Profiling deployed inference | Where is the time actually going? | latency budget worksheet |
| 10 | ROS2 basics | How do camera systems map into robot middleware? | ROS2 pipeline diagram |
| 11 | Calibration and 3D vision | How do calibration errors become system failures? | calibration symptom map |
| 12 | End-to-end project | How do I turn learning into visible evidence? | project brief or demo plan |

## Lesson Outcomes

## Phase 1: System Foundation

### Lesson 1: Processes, Threads, Locks, and Context Switching

Focus:
shared state, contention, waiting, and scheduling behavior.

What you should be able to do:

- explain process vs thread clearly
- identify race, contention, deadlock, and oversubscription
- connect context switching to latency jitter

Checkpoint:
write down why adding threads to a pipeline can make it slower.

### Lesson 2: Virtual Memory, Pages, Page Faults, and `mmap`

Focus:
memory layout, page behavior, and the cost of copying large buffers.

What you should be able to do:

- describe heap, stack, mapped memory, and page faults
- explain why memory movement dominates some workloads
- choose when `mmap` is worth considering

Checkpoint:
compare two data access strategies and explain the difference.

### Lesson 3: CPU, Cache, Locality, and Why Memory Access Dominates Performance

Focus:
cache hierarchy, locality, false sharing, and performance intuition.

What you should be able to do:

- explain cache lines and locality in plain language
- recognize false sharing patterns
- connect access patterns to real image-processing performance

Checkpoint:
show one example where layout matters more than algorithm complexity.

### Lesson 4: Linux Observability for Engineers

Focus:
tool-first diagnosis using `top`, `pidstat`, `vmstat`, `strace`, and `perf`.

What you should be able to do:

- choose the right first tool for a symptom
- separate CPU-heavy, wait-heavy, and memory-heavy failures
- create a first-pass diagnosis flow instead of guessing

Checkpoint:
run at least one tool on one toy workload and record the signal you saw.

## Phase 2: Camera and Deployment Engineering

### Lesson 5: Camera Data Path, Buffers, and Frame Lifecycle

Focus:
frame ownership, queueing, copying, and backpressure inside a camera pipeline.

What you should be able to do:

- draw the path of one frame from sensor input to downstream output
- identify the owner of each buffer
- mark likely hidden copy points and queue buildup points

Checkpoint:
make a pipeline map from one real work scenario.

### Lesson 6: Latency, Jitter, Frame Drops, and Synchronization

Focus:
tail latency, timing stability, frame drops, and sync strategy.

What you should be able to do:

- explain latency, throughput, jitter, and tail latency separately
- reason about why a pipeline can look fine on average but fail in production
- write a diagnosis flow for frame drops and sync drift

Checkpoint:
build a timing diagnosis template you could reuse at work.

### Lesson 7: ONNX and Inference Runtime Basics for System Engineers

Focus:
how a model becomes an executable runtime graph and where runtime cost appears.

What you should be able to do:

- describe the path from training output to deployable runtime
- distinguish preprocessing, graph execution, and postprocessing cost
- reason about where copies and layout conversions appear

Checkpoint:
trace one model from source format to runtime execution.

### Lesson 8: Quantization, TensorRT, and Platform Toolchains

Focus:
precision trade-offs, calibration data, toolchain constraints, and platform decisions.

What you should be able to do:

- explain INT8, FP16, and mixed-precision trade-offs
- compare two platform toolchains from an engineering perspective
- think about deployment stability, memory fit, and debug cost

Checkpoint:
write a small decision matrix for one deployment target.

### Lesson 9: Profiling Deployed Inference

Focus:
latency budgeting, stage-by-stage profiling, copies, transfer, and tail behavior.

What you should be able to do:

- build a latency budget for an inference pipeline
- decide which stage to profile first
- distinguish compute bottlenecks from transfer and preprocessing bottlenecks

Checkpoint:
produce a profiling worksheet you could reuse for any future model.

## Phase 3: Robotics Vision Transition

### Lesson 10: ROS2 Basics for Vision Engineers

Focus:
nodes, topics, launch, QoS, and mapping vision pipelines into robot middleware.

What you should be able to do:

- explain the basic ROS2 communication model
- map one camera pipeline into nodes and topics
- reason about where reliability and QoS matter

Checkpoint:
draw one ROS2-style data flow.

### Lesson 11: Calibration, Hand-Eye Calibration, and 3D Vision Awareness

Focus:
intrinsics, extrinsics, error propagation, hand-eye calibration, and 3D sensing intuition.

What you should be able to do:

- explain intrinsics and extrinsics in practical terms
- connect calibration errors to downstream system symptoms
- understand why 3D setups create new failure modes

Checkpoint:
write a symptom-to-cause map for calibration failures.

### Lesson 12: End-to-End Project Design

Focus:
turn the whole route into a small but convincing systems project.

What you should be able to do:

- choose a project with the right scope
- break it into system, runtime, tooling, and debugging tasks
- present it as public career evidence

Checkpoint:
finish a one-page project brief or start a small prototype.

## Portfolio Artifacts

By the end of the route, try to keep these artifacts:

1. one troubleshooting checklist
2. one memory or cache experiment note
3. one camera pipeline map
4. one latency budget worksheet
5. one deployment decision matrix
6. one ROS2-style system diagram
7. one project brief or demo repository

These artifacts matter because they prove applied engineering thinking, not just passive reading.

## How To Use The Public Site

The public site should feel like a personal learning portal, not a pile of notes.
When we continue improving it, we should bias toward:

- clearer lesson outcomes
- progress by phase
- checkpoint artifacts
- project-based milestones
- better reading flow on detail pages

That will make it feel closer to platforms like Coursera, DeepLearning.AI, and Frontend Masters in structure, even though the content is fully personalized.
