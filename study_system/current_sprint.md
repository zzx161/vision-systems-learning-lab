---
note_type: sprint
title: 当前冲刺
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

# 当前冲刺

## 本周目标

这一周不求学很多，而是把第一阶段最关键的 4 节真正学进去：

1. 进程、线程、锁与上下文切换
2. 虚拟内存、Page、Page Fault 与 `mmap`
3. CPU Cache、局部性与内存访问性能
4. Linux 观测与排障基础

这 4 节是后面所有内容的地基。
如果这一块建立起直觉，后面你看数据链路、掉帧、延迟、部署 Profiling 都会顺很多。

## 本周重点

### 重点 A：把线程真正想明白

不是只会建线程，而是要知道：

- 共享状态为什么危险
- 为什么锁会让系统变慢
- 为什么上下文切换会导致抖动

### 重点 B：把内存真正看成系统问题

不是只知道堆和栈，而是要知道：

- 为什么 buffer 很贵
- page fault 为什么会突然影响时延
- 为什么高频数据链路特别怕重复拷贝

### 重点 C：开始建立性能直觉

不是只记 cache 这个词，而是要知道：

- 为什么访问模式比你想的更重要
- 为什么 false sharing 会拖垮多线程
- 为什么“复杂度一样”不代表跑得一样

### 重点 D：学会第一批观察工具

不是死记命令，而是先知道：

- 系统忙不忙看什么
- 某个线程有没有问题看什么
- 程序像卡住了一样时先看什么

## 这一周要学的课程

1. [lesson_01_process_thread.md](/home/zhixin/code/study_system/courses/lesson_01_process_thread.md)
2. [lesson_02_virtual_memory.md](/home/zhixin/code/study_system/courses/lesson_02_virtual_memory.md)
3. [lesson_03_cache_and_locality.md](/home/zhixin/code/study_system/courses/lesson_03_cache_and_locality.md)
4. [lesson_04_linux_observability.md](/home/zhixin/code/study_system/courses/lesson_04_linux_observability.md)

## 这一周的建议节奏

### 第 1 天

- 读第 1 课
- 自己写一句话解释“进程和线程到底差在哪”

### 第 2 天

- 做线程实验
- 记录你看到的现象

### 第 3 天

- 读第 2 课
- 把你最不理解的 2 个词标出来

### 第 4 天

- 做内存或拷贝实验
- 写一句话解释“为什么搬运数据很贵”

### 第 5 天

- 读第 3 课
- 想一想你见过的哪段代码最可能受 cache 影响

### 第 6 天

- 读第 4 课
- 用 `top`、`pidstat`、`vmstat` 看一次实验程序

### 第 7 天

- 写周复盘
- 关掉资料，自己答复盘题

## 本周实验

- [lab_01_threads.md](/home/zhixin/code/study_system/labs/lab_01_threads.md)
- [lab_02_virtual_memory.md](/home/zhixin/code/study_system/labs/lab_02_virtual_memory.md)
- [lab_03_cache_locality.md](/home/zhixin/code/study_system/labs/lab_03_cache_locality.md)
- [lab_04_observability.md](/home/zhixin/code/study_system/labs/lab_04_observability.md)

## 本周交付物

这一周不要追求做很多，重点是留下 4 个东西：

1. 一段你自己写的“进程 vs 线程”解释
2. 一段你自己写的“为什么高频数据链路怕拷贝”解释
3. 一段你自己写的“为什么访问模式影响性能”解释
4. 一份你自己的初版排障顺序

## 和我一起学的方式

你学到哪一步都可以直接回来找我，不需要等都学完。

最推荐你直接这样说：

- “开始第 1 课，带我学”
- “我看完第 2 课了，但 page fault 还是很抽象”
- “我做了线程实验，结果不会解释”
- “我不知道第 3 课该怎么和真实程序联系”

我会按你卡住的位置继续讲，不会让你自己再去拼资料。

## 本周完成标准

到这周结束时，你至少应该能用自己的话解释：

- 为什么线程共享内存，而进程通常不共享
- 为什么锁竞争会让多线程变慢
- 为什么虚拟内存和 page 行为会影响时延
- 为什么访问模式会影响真实程序性能
- 遇到 CPU 高、程序卡、系统抖时，你先该看什么工具
