---
note_type: lesson
title: Profiling Deployed Inference
track: edge_deployment
phase: 2
lesson: 9
status: planned
completion: 0
estimated_minutes: 110
actual_minutes: 0
last_studied:
next_review:
priority: medium
tags:
  - study/lesson
  - track/deployment
  - phase/2
---

# Lesson 9: Profiling Deployed Inference

## Why This Matters

A deployed model can be correct and still be unusable.

Common reasons:

- preprocessing is slow
- memory copies are excessive
- the runtime stalls on transfer
- performance is unstable under load
- tail latency breaks real-time expectations

Profiling is how you replace vague blame with measurable truth.

## Learning Objectives

After this lesson, you should be able to:

1. build a latency budget for a deployed inference pipeline
2. separate preprocessing, execution, and postprocessing cost
3. reason about compute-bound vs transfer-bound vs memory-bound behavior
4. choose a sensible profiling order instead of measuring randomly
5. document a deployment bottleneck clearly

## The First Rule Of Profiling

Do not start with "optimize."
Start with "where does the time go?"

For one inference path, always split:

1. input acquisition
2. preprocessing
3. host-to-device or host-to-accelerator transfer
4. runtime execution
5. device-to-host transfer if present
6. postprocessing
7. output packaging or publishing

This split already rules out a lot of bad guesses.

## Build A Latency Budget

A latency budget is a simple breakdown of where time is spent.

Example categories:

- capture:
  4 ms
- preprocess:
  9 ms
- transfer:
  3 ms
- inference:
  11 ms
- postprocess:
  5 ms
- output:
  2 ms

This matters because the largest number is not always the most important number.
Sometimes the real pain is:

- the most variable stage
- the stage that blocks the whole pipeline
- the stage that grows with resolution or stream count

## Three Bottleneck Families

### Compute-Bound

The system is limited by actual execution kernels.

Possible signs:

- accelerator busy for long periods
- runtime stage dominates consistently
- reducing model size helps a lot

### Memory-Bound

The system spends too much time waiting on memory movement or poor access patterns.

Possible signs:

- heavy resize or color conversion cost
- large resolution changes hurt sharply
- copies and layout conversions dominate

### Transfer-Bound

Movement between CPU and accelerator becomes the real limiter.

Possible signs:

- model execution itself looks acceptable
- data movement still dominates total latency
- small graphs perform surprisingly poorly because setup cost is large

## Tail Behavior Matters

A stable average can still hide bad spikes.

When profiling, record at least:

- average latency
- p95 or p99 if possible
- maximum observed latency
- variability between repeated runs

If only averages are recorded, important failure patterns may remain invisible.

## A Good Profiling Order

When a pipeline is slow, profile in this order:

1. whole-pipeline end-to-end latency
2. stage-level breakdown
3. copy and transfer count
4. runtime-specific execution profile
5. CPU-side support work such as preprocessing and postprocessing
6. concurrency effects under multiple streams or load

This order prevents premature deep dives into the wrong stage.

## What To Watch In Deployment

Useful questions include:

1. how much time is spent before inference starts
2. how much time is spent after inference ends
3. are tensors copied more than once
4. does dynamic shape increase overhead
5. does batch size change resource behavior
6. what happens when stream count increases
7. how much does tail latency move under sustained load

## Practical Task

Create a latency budget worksheet with these rows:

- input acquisition
- preprocessing
- transfer in
- runtime execution
- transfer out
- postprocessing
- publication or output

For each row, add:

- average latency
- worst observed latency
- notes on variability
- notes on likely root cause

## Stretch Task

Take one hypothetical underperforming deployment and answer:

1. what would I measure first
2. what evidence would prove it is compute-bound
3. what evidence would prove it is copy-bound
4. what evidence would prove it is unstable rather than simply slow

## What A Strong Deliverable Looks Like

By the end of this lesson, you should have:

- one reusable latency budget table
- one bottleneck classification note
- one profiling order checklist
- one explanation of why averages are not enough

## Common Mistakes

### Mistake 1

Measuring only the runtime kernel and ignoring pipeline overhead.

### Mistake 2

Mixing one-time initialization cost with steady-state latency.

### Mistake 3

Ignoring tail latency and only reporting means.

### Mistake 4

Trying to optimize before proving which stage dominates.

## Review Questions

1. Why is a stage-by-stage latency budget valuable?
2. How do compute-bound and transfer-bound problems differ?
3. Why can a small model still have disappointing end-to-end latency?
4. What should you measure besides average time?
5. What is a sensible first profiling order?

## Connection To The Next Lesson

Lesson 10 starts the robotics transition path with ROS2 basics for vision engineers.
