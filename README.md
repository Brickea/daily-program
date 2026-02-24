# daily-program

一个面向 Java、Python、Go、Ruby 的每日编程学习文档仓库。GitHub Pages 以 `docs/` 目录生成站点，并通过定时任务每天 UTC 07:00 为每种语言生成当日学习模板。

## 快速开始
- 在仓库 Settings 的 GitHub Pages 中，将发布源设置为 `docs/`。
- 访问 `docs/index.md` 了解站点结构，四个语言入口位于 `docs/{language}/README.md`。
- 定时任务配置位于 `.github/workflows/daily-learning.yml`，可手动使用 workflow_dispatch 立即生成当日文档。
- `.github/workflows/daily-feedback.yml` 会在每天 UTC 00:00 汇总前一日反馈并生成下一日的计划模板，避免与 07:00 的当日文档生成冲突。
