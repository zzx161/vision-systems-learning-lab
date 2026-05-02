# 视觉系统学习实验室 Vision Systems Learning Lab

这是一个长期学习工作区，不是一次性笔记。

它的目标很明确：

- 建立 Linux 系统、体系结构、性能分析和系统工程的长期理解
- 让数据链路、时延、抖动、同步、部署这些问题变得更可解释
- 形成一套更通用、可迁移的工程能力

## 这套系统里有什么

- [roadmap.md](/home/zhixin/code/study_system/roadmap.md)
  总学习路线图，告诉你先学什么、后学什么。
- [course_plan.md](/home/zhixin/code/study_system/course_plan.md)
  课程总表，按课来推进。
- [current_sprint.md](/home/zhixin/code/study_system/current_sprint.md)
  当前冲刺内容，适合日常跟进。
- [operator_context.md](/home/zhixin/code/study_system/operator_context.md)
  人和工作上下文档案，帮助助手和你自己快速找回主线。
- [dashboard.md](/home/zhixin/code/study_system/dashboard.md)
  学习面板主页。
- [courses](/home/zhixin/code/study_system/courses)
  正式课程内容。
- [labs](/home/zhixin/code/study_system/labs)
  实验、代码和操作说明。
- [reviews](/home/zhixin/code/study_system/reviews)
  每周复盘和回顾。
- [tracking](/home/zhixin/code/study_system/tracking)
  进度统计、网页面板和快照。
- [scripts](/home/zhixin/code/study_system/scripts)
  自动化脚本。
- [playbooks](/home/zhixin/code/study_system/playbooks)
  可直接复用的排查清单、模板和决策表。

## 推荐使用方式

每次回来学习，都按这个顺序走：

1. 先看 [operator_context.md](/home/zhixin/code/study_system/operator_context.md)
2. 看 [current_sprint.md](/home/zhixin/code/study_system/current_sprint.md)
3. 打开对应课程
4. 跑一个实验或完成一个小任务
5. 写一条 session note
6. 刷新进度面板

这样学的重点不是“多”，而是“持续积累、不断复盘”。

## 授课语言和术语

默认用中文授课，但不要把所有核心概念都硬翻译成中文。
如果英文术语在工程现场更常用、更准确，就保留英文原词；第一次出现时可以补一个简短中文解释，之后直接使用英文。
例如 `token` 就保留为 `token`，不要翻译成“词元”。

## 这套课程现在有什么“干货结构”

为了让课程更像完整教材，而不只是一个大纲库，现在每一课都会尽量补齐这些固定模块：

1. 概念讲解：把关键词讲清楚，不默认你已经会。
2. 小案例：用具体场景把抽象概念落下来。
3. 判断表或清单：让你在真实问题前有抓手。
4. 一页速记卡：帮助你复盘时快速回忆。
5. 自测与复盘：把“看懂”变成“记住并会用”。

也就是说，后面的课程会更偏“能直接读着学”的形态。

## 为什么要这样学

这套系统想帮助你培养的是更通用的系统工程能力：

- 能把系统问题讲清楚
- 能把链路问题拆开
- 能定位性能瓶颈
- 能理解部署和运行时的真实限制

这类能力不依赖某一个特定岗位，迁移性也更强。

## 实战干货入口

如果你今天不想先读一大段课程，而是更想看“可以直接拿来用的东西”，优先打开这里：

- [playbooks/README.md](/home/zhixin/code/study_system/playbooks/README.md)
- [linux_perf_triage.md](/home/zhixin/code/study_system/playbooks/linux_perf_triage.md)
- [camera_pipeline_debug.md](/home/zhixin/code/study_system/playbooks/camera_pipeline_debug.md)
- [latency_budget_template.md](/home/zhixin/code/study_system/playbooks/latency_budget_template.md)
- [deployment_decision_matrix.md](/home/zhixin/code/study_system/playbooks/deployment_decision_matrix.md)
- [observability_checklist.md](/home/zhixin/code/study_system/playbooks/observability_checklist.md)

## 网页面板

本地学习站和公开站都已经接好了。

常用入口：

- 本地追踪页：
  [tracking/index.html](/home/zhixin/code/study_system/tracking/index.html)
- 公开站构建输出：
  [public/index.html](/home/zhixin/code/study_system/public/index.html)

## 自动化脚本

常用命令：

```bash
python3 /home/zhixin/code/study_system/scripts/new_session.py
python3 /home/zhixin/code/study_system/scripts/update_progress.py
python3 /home/zhixin/code/study_system/scripts/open_dashboard_localhost.py
python3 /home/zhixin/code/study_system/scripts/build_public_site.py
```

## 关于长期记忆

这套目录本身就是“外部记忆”。
以后我们继续学的时候，不需要从头聊起，可以直接基于这些文件往前推进。

如果你希望助手更像“带记忆地接手工作”，最值得先维护的是：

- [operator_context.md](/home/zhixin/code/study_system/operator_context.md)
- [current_sprint.md](/home/zhixin/code/study_system/current_sprint.md)
- 最近一次 session note

## 和我一起学习

这套课程不是让你自己硬啃的。
你可以直接把我当成长期陪学老师来用。

最推荐的方式是：

1. 先打开 [current_sprint.md](/home/zhixin/code/study_system/current_sprint.md)
2. 选当前要学的那一课
3. 回来直接说：
   - “开始第 1 课，带我学”
   - “我卡在第 2 课的 page fault”
   - “我看不懂第 3 课里的 false sharing”
   - “我做完实验了，帮我解释结果”

之后我会按课程正文继续带你学，而不是让你自己再去外面找资料。
