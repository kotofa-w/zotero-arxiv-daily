# Zotero-arXiv-Daily · 中文论文日报与经典阅读

基于 [TideDra/zotero-arxiv-daily](https://github.com/TideDra/zotero-arxiv-daily) 的个人维护分支。项目根据 Zotero 文献库筛选新论文，通过 GitHub Actions 定时发送邮件；此分支增加中文摘要译文与导读、独立的经典论文学习路径，以及 arXiv API 异常时的 RSS 元数据回退。原项目的推荐、邮件和多来源检索能力由 TideDra 开发，见文末致谢。

## 功能

- 从 arXiv、bioRxiv、medRxiv 和 ChemRxiv 检索新论文，按 Zotero 文献摘要计算相关度。可用集合路径限定或排除排序语料。
- 为入选论文生成中文摘要译文和导读，标明导读依据是摘要还是取得的正文片段；生成失败时保留原有摘要展示路径。
- 可选的「每日经典」栏目从仓库中的 71 篇目录选一篇，覆盖 AI 基础、神经网络、计算机体系结构、电路、设计自动化、AI 硬件和存内计算七条学习路径。目录包含经典研究及部分综述、教程；按路径、年份和题名顺序轮转。
- 经典目录及导读保存在 [`classics/`](classics/)；运行时读取本地文件，不会自动抓取综述或将目录写入 Zotero。新增综述须先核实题录、正式版本、摘要及重复项，再加入目录与对应导读。
- 经典发送历史保存在独立的 `classics-state` 分支。只有计划任务的邮件获 SMTP 接受后才推进历史；手动试发不推进。

推荐质量取决于 Zotero 条目的摘要、所选文献源及模型。经典目录是阅读安排，不代表 71 篇均经过全文审校或已经投递到收件箱。

## 快速开始

需要 Zotero 用户 ID、具有读取权限的 Zotero API key、SMTP 发信账号和兼容 OpenAI API 的模型接口。Fork 此仓库后，在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 中设置：

| 类型 | 名称 | 用途 |
| --- | --- | --- |
| Secret | `ZOTERO_ID`, `ZOTERO_KEY` | Zotero 数字用户 ID 与只读 API key |
| Secret | `SENDER`, `SENDER_PASSWORD`, `RECEIVER` | SMTP 发件地址、授权码和收件地址 |
| Secret | `OPENAI_API_KEY`, `OPENAI_API_BASE` | 模型 API 密钥与基地址 |
| Variable | `CUSTOM_CONFIG` | 覆盖 [`config/base.yaml`](config/base.yaml) 的 YAML 配置 |

`CUSTOM_CONFIG` 的示例（按自己的邮件服务商、模型和学科修改）：

```yaml
zotero:
  user_id: ${oc.env:ZOTERO_ID}
  api_key: ${oc.env:ZOTERO_KEY}
  include_path: null

email:
  sender: ${oc.env:SENDER}
  receiver: ${oc.env:RECEIVER}
  smtp_server: smtp.qq.com
  smtp_port: 465
  sender_password: ${oc.env:SENDER_PASSWORD}

llm:
  api:
    key: ${oc.env:OPENAI_API_KEY}
    base_url: ${oc.env:OPENAI_API_BASE}
  api_mode: chat_completion
  generation_kwargs:
    model: gpt-4o-mini

source:
  arxiv:
    category: ["cs.AI", "cs.CV", "cs.LG", "cs.CL"]

executor:
  source: ["arxiv"]
```

`${oc.env:NAME}` 从环境变量取值。完整可配置项见 [`config/base.yaml`](config/base.yaml)；配置覆盖顺序见 [`config/default.yaml`](config/default.yaml)。不要把真实密钥写入仓库文件。

在 **Actions → Test → Run workflow** 手动检查邮件路径。Test 是调试运行，会取测试论文，并且不会推进经典历史。正式的 [`Send emails daily`](.github/workflows/main.yml) 默认在每天 **22:00 UTC** 启动；周末或节假日可能没有新的 arXiv 论文。工作流日志中的 SMTP 接受只证明发信服务器接收了邮件，收件箱投递仍需在邮箱核对。

## 启用每日经典

经典栏目默认关闭。启用前，应在 fork 中创建 `classics-state` 分支，并在分支根目录放入 `daily_classics.json`；初始内容可参考 [`classics/state.example.json`](classics/state.example.json)。随后将 Actions Variable `CLASSICS_ENABLED` 设为 `true`。计划工作流会检出该分支，在 SMTP 接受邮件后提交发送历史。若状态分支缺失，启用后的工作流会在检出阶段失败。

手动运行 **Actions → Test** 并选中 `preview_classics`，可试发包含经典栏目的邮件；这次运行不会写入发送历史。`preview_daily_reading` 则生成不发邮件的中文导读 HTML 预览。经典推荐不依赖将 71 篇目录导入个人 Zotero；若个人库里有 `学科经典` 集合，该集合不计入普通阅读排序，只有直接位于 `学科经典/兴趣种子` 且有原始摘要的文献可提供有限的兴趣种子权重。路径和上限见 [`config/base.yaml`](config/base.yaml)。

## 本地运行

安装 [uv](https://docs.astral.sh/uv/) 和 Python 3.13 或更新版本，设置上表环境变量，并将自己的配置写入 `config/custom.yaml` 后，在仓库根目录运行：

```bash
uv run src/zotero_arxiv_daily/main.py
```

本地启用经典时，还需提供 `classics-state/daily_classics.json`，并设置 `CLASSICS_ENABLED=true`。本地运行不会以计划任务身份自动推进历史。只检查中文导读生成、且不连接 Zotero 或 SMTP 时，可运行 `uv run python -m zotero_arxiv_daily.preview_daily_reading`；它使用仓库中的示例论文并生成 `daily-reading-preview.html`。

## 项目结构与边界

- [`src/zotero_arxiv_daily/`](src/zotero_arxiv_daily/)：检索、排序、中文导读、邮件与经典轮转代码。
- [`config/`](config/)：基础配置及本地覆盖入口。
- [`classics/verified_review.csv`](classics/verified_review.csv)、[`classics/guides/`](classics/guides/)：经典题录、逐篇导读和索引。综述覆盖与核验范围见 [`classics/survey_coverage_audit_2026-09-29.md`](classics/survey_coverage_audit_2026-09-29.md)。
- [`.github/workflows/`](.github/workflows/)：计划发送、手动测试和 CI。部署者需自行维护 Actions Secrets、Variables 与状态分支。

## 原项目与致谢

本仓库 fork 自 **[TideDra](https://github.com/TideDra)** 开发的 [Zotero-arXiv-Daily](https://github.com/TideDra/zotero-arxiv-daily)。原作者设计并实现了基于 Zotero 的论文推荐、邮件发送与 GitHub Actions 部署；本分支在此基础上维护中文阅读和经典学习路径。感谢原项目及其依赖的 [pyzotero](https://github.com/urschrei/pyzotero)、[arxiv.py](https://github.com/lukasschwab/arxiv.py) 和 [sentence-transformers](https://github.com/UKPLab/sentence-transformers)。如需支持原开发者，请访问[原项目](https://github.com/TideDra/zotero-arxiv-daily)。

本项目沿用 [AGPL-3.0 许可证](LICENSE)。
