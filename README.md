# daily-program

一个面向 Java、Python、Go、Ruby 的每日编程学习文档仓库。GitHub Pages 以 `docs/` 目录生成站点，并通过定时任务每天 UTC 07:00 为每种语言从权威网站、论坛、GitHub 等来源自动收集并生成当日学习内容。

## 快速开始
- 在仓库 Settings 的 GitHub Pages 中，将发布源设置为 `docs/`。
- 访问 `docs/index.md` 了解站点结构，四个语言入口位于 `docs/{language}/README.md`。
- 定时任务配置位于 `.github/workflows/daily-learning.yml`，每天 UTC 07:00 自动从配置的数据源收集内容并生成学习文档。
- 可手动使用 workflow_dispatch 立即生成当日文档。
- 数据源配置位于 `config/sources.yaml`，可以自定义每种语言的学习内容来源（RSS 订阅、GitHub 仓库等）。
- GitHub Pages 发布由 `.github/workflows/pages-deploy.yml` 负责，在定时任务成功完成后自动构建并部署 `docs/` 目录，无需额外触发。

## 数据源配置
每种编程语言都有自己的权威数据源，包括：
- **Java**: Oracle Java Blog, Spring Blog, Baeldung, InfoQ Java, Reddit r/java
- **Python**: Python.org News, Real Python, PyPI Updates, Planet Python, Reddit r/Python
- **Go**: Go Blog, Golang Weekly, Reddit r/golang, Awesome Go
- **Ruby**: Ruby on Rails Blog, Ruby Weekly, RubyFlow, Reddit r/ruby

可以通过编辑 `config/sources.yaml` 文件自定义每种语言的数据源。
