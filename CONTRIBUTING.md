# Contributing

这个仓库现在主要是一个个人学习系统，但内容结构已经比较完整。
如果后续继续维护，建议按下面的方式做，能避免仓库越来越乱。

## 最常改的内容

- 课程正文：`study_system/courses/`
- 实验说明与代码：`study_system/labs/`
- 排障清单与模板：`study_system/playbooks/`
- 进度和网页生成：`study_system/scripts/`

## 推荐工作流

1. 修改课程、实验、脚本或网页生成逻辑
2. 刷新进度
3. 重建公开站
4. 本地检查关键页面
5. 再提交和推送

## 常用命令

```bash
python3 study_system/scripts/update_progress.py
python3 study_system/scripts/build_public_site.py
python3 study_system/scripts/open_dashboard_localhost.py
```

## 提交前建议检查

- [study_system/tracking/today.md](study_system/tracking/today.md) 是否生成正常
- [study_system/tracking/progress_snapshot.md](study_system/tracking/progress_snapshot.md) 是否同步
- [study_system/tracking/index.html](study_system/tracking/index.html) 是否能打开
- [study_system/public/index.html](study_system/public/index.html) 是否已更新

## Git 注意事项

仓库根目录里有些文件更像本地工作区杂项，不建议随手提交：

- `bin/`
- `.vscode/settings.json`

如果不是这套学习系统的一部分，也尽量不要混进同一个提交里。

## 公开站发布

推送到 `main` 后会自动触发 GitHub Pages 发布。

相关工作流：

- [.github/workflows/deploy-study-site.yml](.github/workflows/deploy-study-site.yml)

公开部署说明：

- [study_system/PUBLIC_DEPLOY.md](study_system/PUBLIC_DEPLOY.md)

## 建议后续继续补的内容

- `LICENSE`
  让仓库的公开边界更清楚
- 课程页的术语索引
  方便长期复习
- 更多实验结果样例
  让课程更像完整教材
- 自动化发布前检查
  比如一键校验关键文件是否生成
