# Vision Systems Learning Lab

一个以中文为主的长期学习仓库，主题围绕：

- Linux 系统能力
- 性能分析与可观测性
- 计算机体系结构基础
- 数据链路与边缘部署
- 机器人视觉与系统迁移能力

这个仓库不只是放笔记，更像一套可以持续推进的学习系统：

- 有课程
- 有实验
- 有复盘
- 有进度面板
- 有公开网页
- 有自动化脚本

## 在线访问

- GitHub Pages: https://zzx161.github.io/vision-systems-learning-lab/
- GitHub 仓库: https://github.com/zzx161/vision-systems-learning-lab

## 仓库里有什么

主要内容都在 [study_system](study_system/) 下面：

- [README.md](study_system/README.md)
  学习系统总入口
- [roadmap.md](study_system/roadmap.md)
  总路线图
- [course_plan.md](study_system/course_plan.md)
  课程总表
- [current_sprint.md](study_system/current_sprint.md)
  当前冲刺
- [operator_context.md](study_system/operator_context.md)
  人物与工作上下文档案
- [courses](study_system/courses/)
  16 节正式课程
- [labs](study_system/labs/)
  对应实验和代码
- [playbooks](study_system/playbooks/)
  可直接复用的排查清单、模板和决策表
- [tracking](study_system/tracking/)
  进度快照、今日建议和网页面板

## 快速开始

如果你只是想直接进入内容，推荐按这个顺序：

1. 打开 [tracking/today.md](study_system/tracking/today.md)
2. 看 [operator_context.md](study_system/operator_context.md)
3. 看 [current_sprint.md](study_system/current_sprint.md)
4. 进入当前课程
5. 做对应实验
6. 学完后更新学习记录

## 常用脚本

```bash
python3 study_system/scripts/start_study_session.py
python3 study_system/scripts/finish_study_session.py --minutes 30
python3 study_system/scripts/update_progress.py
python3 study_system/scripts/open_dashboard_localhost.py
python3 study_system/scripts/build_public_site.py
```

## 常用入口

- [今日学习建议](study_system/tracking/today.md)
- [人物与工作上下文](study_system/operator_context.md)
- [学习进度快照](study_system/tracking/progress_snapshot.md)
- [网页面板](study_system/tracking/index.html)
- [公开站构建说明](study_system/PUBLIC_DEPLOY.md)

## 仓库结构

```text
.
├── .github/workflows/
│   └── deploy-study-site.yml
├── study_system/
│   ├── courses/
│   ├── labs/
│   ├── logs/
│   ├── playbooks/
│   ├── reviews/
│   ├── scripts/
│   ├── templates/
│   └── tracking/
└── README.md
```

## 这个仓库适合谁

如果你正在补这些方向，这个仓库会比较合适：

- 想系统学习 Linux、性能和体系结构
- 想把“知道概念”变成“能分析真实系统”
- 希望有一套可持续追踪的学习系统
- 希望把学习结果整理成公开可展示的网页

## 更新公开站

推送到 `main` 后，GitHub Actions 会自动构建并部署 Pages。

工作流文件在：

- [.github/workflows/deploy-study-site.yml](.github/workflows/deploy-study-site.yml)

如果你想本地先预览，可以运行：

```bash
python3 study_system/scripts/build_public_site.py
```

## 维护说明

如果后续继续扩课程、补实验、改面板，建议先看：

- [CONTRIBUTING.md](CONTRIBUTING.md)

## 说明

这个仓库目前没有额外加开源许可证。
如果后面想明确开源边界，最值得补的下一项是 `LICENSE`。
