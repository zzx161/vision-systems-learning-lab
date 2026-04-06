---
note_type: lesson
title: Latency, Jitter, Frame Drops, and Synchronization
track: camera_systems
phase: 2
lesson: 6
status: planned
completion: 0
estimated_minutes: 120
actual_minutes: 0
last_studied:
next_review:
priority: high
tags:
  - study/lesson
  - track/camera
  - phase/2
---

# Lesson 6: Latency, Jitter, Frame Drops, and Synchronization

## Why This Matters

In production systems, many failures are timing failures:

- frame arrives late
- latency fluctuates badly
- downstream misses data
- synchronization drifts under load

## What You Will Learn

1. latency vs throughput
2. average latency vs tail latency
3. jitter and why users feel it
4. common frame-drop causes
5. synchronization mindset for camera pipelines

## Mental Model

When a frame pipeline looks unstable, ask:

1. Is one stage slower than the others?
2. Is queue depth hiding the real bottleneck?
3. Is timing stable or only average performance acceptable?
4. Is backpressure spreading through the whole chain?

## Practical Output

Write one diagnosis flow for:

- intermittent frame drops
- burst-load jitter
- synchronization mismatch between stages

## Next Lesson

Lesson 7 moves into ONNX and inference runtime basics.
