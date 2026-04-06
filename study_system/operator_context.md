---
note_type: profile
title: 人物与工作上下文
status: active
last_updated: 2026-04-06
tags:
  - study/profile
  - assistant/context
---

# 人物与工作上下文

## 你现在大概率在做什么

这套仓库显示出的主线很明确：

- 你在往视觉系统 / 系统工程方向迁移或深化
- 你关心 Linux、性能、链路、时延、部署、可观测性这些“真实系统问题”
- 你不是只想背概念，而是想把它们变成可迁移的工程能力

如果一句话概括：

你大概率是一个正在强化系统能力的视觉工程师，或者正在往这一类岗位靠近的人。

## 你当前最重要的学习目标

- 把 Linux 系统基础补成真正可用的直觉
- 把性能分析和观测能力做成稳定套路
- 把数据链路、延迟、抖动、拷贝、同步这些问题讲清楚
- 为后面的相机系统、推理部署、ROS2 和量产工程打地基

## 当前冲刺摘要

- 当前 sprint：`week_01`
- 日期范围：`2026-04-06` 到 `2026-04-12`
- 当前课程：`courses/lesson_01_process_thread.md`
- 当前实验：`labs/lab_01_threads.md`
- 当前状态：刚开始建立第一阶段基础，学习记录已创建，但还没形成大量积累

## 这套系统是怎么用的

每次继续时，优先看这些文件：

1. `current_sprint.md`
2. `tracking/progress_snapshot.md`
3. `tracking/today.md`
4. 最近一次 `logs/sessions/*.md`

如果学习结束，要更新记录并刷新派生页面：

1. `python3 scripts/finish_study_session.py --minutes 30`
2. `python3 scripts/update_progress.py`
3. 如果内容要公开展示，再运行 `python3 scripts/build_public_site.py`

## 给后续助手的启动说明

如果你是新接手的助手，不要一上来问“你是做什么的”。先基于这个文件和以下入口建立上下文：

1. 读 `operator_context.md`
2. 读 `current_sprint.md`
3. 读 `tracking/today.md`
4. 读最近一次 `logs/sessions/*.md`

然后按下面的方式协作：

- 默认把用户当成正在补系统能力的视觉工程背景学习者
- 解释时优先联系真实链路问题，不只讲抽象概念
- 先接住当前学习进度，再决定补概念、做实验还是做复盘
- 如果要推断身份或岗位，明确说这是基于仓库内容的推断

## 已知限制

- 这份档案是根据当前仓库内容推断出来的，不一定等于你的完整职业身份
- 如果你的方向变化了，这份文件应该优先更新
- 这份文件服务于“快速接手上下文”，不是正式简历
