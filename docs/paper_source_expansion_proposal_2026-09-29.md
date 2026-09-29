# 待实现方向：正式发表论文源

状态：封存方案；未实现、未启用、未加入生产邮件。记录日期：2026-09-29。

## 结论

当前不直接增加生产论文源。若现有邮件持续漏掉目标领域的重要正式发表论文，再试点一个范围有限的 IEEE 正式题录源；试点只记录候选，不改变邮件。ACM、Elsevier、Springer 和广域索引暂不同时接入。

## 判断依据

- fork 的生产 `CUSTOM_CONFIG` 当前只有 `executor.source: ["arxiv"]`，订阅类别为 `cs.AR`、`cs.ET`、`cs.LG`、`eess.SY`、`physics.app-ph`，每日邮件最多 10 篇；`CLASSICS_ENABLED=true` 属于独立栏目。
- 2026-09-24 至 09-29 最近六次定时运行的原始候选数依次为 155、151、162、0、0、141。有候选的工作日均远超邮件上限；周末零候选不能证明需要增加来源。运行记录见 [GitHub Actions](https://github.com/kotofa-w/zotero-arxiv-daily/actions/workflows/main.yml)。
- 现有执行器把多个来源的 `Paper` 直接合并后排序，缺少跨来源 DOI／题名去重；正式版和 arXiv 预印本可能重复。入口见 [`executor.py`](../src/zotero_arxiv_daily/executor.py)。
- 项目已有 arXiv、bioRxiv、medRxiv、ChemRxiv 检索器；ChemRxiv 检索器已直接使用 Crossref REST API。扩大来源数量本身不会解决推荐相关性问题。

## 候选来源与用途

| 来源 | 可能用途 | 启用前需核实 |
| --- | --- | --- |
| [IEEE Xplore Metadata API](https://developer.ieee.org/docs) | 目标期刊／会议的正式题录、摘要、DOI | API key、查询范围、摘要覆盖、配额；全文访问与题录接口分开 |
| [OpenAlex](https://github.com/J535D165/pyalex) | 跨出版社发现与 DOI、开放版本线索 | 2026 年起需要 API key；严格按目标刊物、类型和日期过滤，避免候选泛滥 |
| [Crossref](https://github.com/sckott/habanero) | ACM 等正式论文题录和 DOI 校验 | 摘要可能缺失；可沿用现有 HTTP 调用，无须先引入客户端依赖 |
| [Semantic Scholar](https://github.com/danielnsilva/semanticscholar) | 补充摘要、引用关系 | 覆盖与速率限制；不作为付费全文下载途径 |
| [Springer Nature 官方客户端](https://github.com/springernature/springernature_api_client)、[pybliometrics](https://github.com/pybliometrics-dev/pybliometrics) | 出版商或 Scopus 专用 API 的后续选项 | API key、机构授权和可返回字段；不因学校订阅而推定可自动抓取全文 |
| [Unpaywall 客户端](https://github.com/unpywall/unpywall) | 按 DOI 查开放获取版本 | 仅作阅读链接补充，不作每日新论文发现主源 |

东南大学图书馆公开列出 [IEEE IEL](https://lib.seu.edu.cn/bencandy.php?fid=251&id=1480)、[ACM DL](https://lib.seu.edu.cn/bencandy.php?fid=251&id=1471)、[ScienceDirect](https://lib.seu.edu.cn/bencandy.php?fid=251&id=1420) 和 [Springer 电子期刊](https://lib.seu.edu.cn/bencandy.php?fid=251&id=1415) 等订购资源。这些是人工阅读入口；GitHub Actions 不自动继承校园网、CARSI 或个人账户的全文权限。ACM 当前没有已核实、适合此日报直接接入的成熟专用客户端；网页登录态爬虫不作为计划任务方案。

## 恢复实施时的最小步骤

1. 抽样查看近期邮件前 10 篇，记录具体漏掉的目标正式论文，确认覆盖缺口。
2. 在汇总排序前加入跨来源去重：优先 DOI；无 DOI 时用规范化题名、作者和年份核对，保留预印本与正式版的关系。
3. 对有限的 IEEE 刊物／会议运行 7–14 天只读影子采集，记录候选数、摘要可用率、与 arXiv 重合数，以及人工判定的新增相关论文。影子阶段不发邮件、不下载订阅全文。
4. 只有确有稳定的新增相关论文时，再决定是否加入正式日报，并核对邮件上限 10 篇下的排序影响；否则维持现状。

本文件仅保存方向与评估门槛，不创建自动化、密钥或待执行任务。
