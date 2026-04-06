---
note_type: lesson
title: ONNX and Inference Runtime Basics for System Engineers
track: edge_deployment
phase: 2
lesson: 7
status: planned
completion: 0
estimated_minutes: 100
actual_minutes: 0
last_studied:
next_review:
priority: medium
tags:
  - study/lesson
  - track/deployment
  - phase/2
---

# Lesson 7: ONNX and Inference Runtime Basics for System Engineers

## Why This Matters

You do not need to become a pure algorithm engineer to gain deployment value.
What matters is understanding how a model becomes a runtime system on real hardware.

In real products, model value depends on:

- whether export works
- whether preprocessing matches training assumptions
- whether runtime execution is stable
- whether memory layout and copies destroy the expected speedup

This lesson is about the engineering path from model artifact to deployed execution.

## Learning Objectives

After this lesson, you should be able to:

1. explain what ONNX represents at a practical level
2. describe the path from source model to runtime execution
3. distinguish model compute from preprocessing and postprocessing cost
4. identify common layout and copy overhead in an inference pipeline
5. trace one simple deployment path as a systems engineer

## Mental Model: A Model File Is Not A Product

A trained model is only one layer.
A deployable system usually includes:

1. source model artifact
2. export step
3. graph conversion or optimization
4. runtime engine
5. preprocessing
6. inference execution
7. postprocessing
8. packaging and observability

If any one of these layers is fragile, the final deployment is fragile.

## What ONNX Is

ONNX is best understood as an interchange format for model graphs and tensors.

For your current goal, the key point is not every file detail.
The key point is:

- it provides a common representation between training and deployment ecosystems
- it makes graph conversion and runtime choice easier
- it does not remove the need to understand deployment constraints

Useful attitude:

"ONNX helps models travel between tools, but it does not magically solve runtime cost."

## A Practical Deployment Path

One simple path looks like this:

1. model is trained in PyTorch
2. model is exported to ONNX
3. ONNX graph is checked or simplified
4. runtime or toolchain turns the graph into an executable form
5. input data is preprocessed to match the model contract
6. runtime executes operators
7. outputs are decoded or filtered for use

The system engineer cares about every interface in this path.

## What An Inference Runtime Actually Does

At a high level, the runtime is responsible for:

- loading the graph
- allocating tensors or buffers
- choosing execution kernels
- scheduling operator execution
- managing memory movement

This means runtime performance depends on more than the model itself.
It also depends on:

- data layout
- operator support
- precision choice
- hardware target
- copy count
- batch and shape assumptions

## Where Time Goes In Practice

A naive mental model says:

"the model is slow"

A better systems mental model says:

"which stage is slow?"

Time may be spent in:

- input acquisition
- image decode or color conversion
- resize or normalization
- CPU to GPU or CPU to accelerator transfer
- graph execution
- output parsing
- result packaging

This is why many "runtime" problems are actually pipeline problems.

## Common Hidden Costs

These costs are frequently underestimated:

- NHWC to NCHW conversion
- repeated normalization on CPU
- unnecessary tensor copies
- dynamic shape overhead
- unsupported operators falling back to CPU
- conversion between toolchain-specific buffer types

In some systems, these costs dominate the model compute itself.

## Questions A System Engineer Should Ask

1. What is the source model format?
2. Why is this runtime chosen?
3. What layout does the runtime expect?
4. How many copies happen before execution starts?
5. Does any operator fall back to an unexpected backend?
6. What is the latency split between preprocess, execute, and postprocess?

These questions are how you add value without becoming a model researcher.

## A Small Thinking Framework

When a deployment underperforms, classify the issue first:

### Export Problem

The model cannot be converted cleanly or produces mismatched outputs.

### Compatibility Problem

The runtime or toolchain does not support the graph as expected.

### Data Contract Problem

Preprocessing or tensor layout no longer matches the model assumption.

### Systems Problem

The graph may be fine, but runtime behavior is limited by memory, transfer, contention, or platform overhead.

## Practical Task

Trace one simple model path with this template:

- source framework
- export format
- runtime target
- input layout
- preprocessing steps
- postprocessing steps
- likely copy points
- likely profiling points

You can use a model from work, a public YOLO example, or a hypothetical pipeline.

## Stretch Task

Write one paragraph comparing:

- "the model is slow"
- "the deployment path is slow"

The second framing is almost always more accurate and more useful.

## What A Strong Deliverable Looks Like

By the end of this lesson, you should have:

- one deployment path sketch
- one list of runtime assumptions
- one list of likely hidden copies
- one guess about the most expensive non-model stage

## Common Mistakes

### Mistake 1

Treating ONNX as the final answer instead of a transfer format.

### Mistake 2

Ignoring preprocessing and postprocessing when discussing runtime speed.

### Mistake 3

Assuming hardware acceleration automatically removes system bottlenecks.

### Mistake 4

Not checking whether graph operators or data layouts match runtime expectations.

## Review Questions

1. Why is ONNX useful even if it does not solve runtime performance by itself?
2. What are the common stages between a source model and deployed execution?
3. Why can preprocessing dominate total latency?
4. What kinds of copies usually hide around layout conversion?
5. What questions would you ask before blaming the model itself?

## Connection To The Next Lesson

Lesson 8 continues this route by focusing on quantization, TensorRT, and deployment toolchains.
