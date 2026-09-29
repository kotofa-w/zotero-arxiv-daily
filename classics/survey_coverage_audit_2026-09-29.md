# 综述论文学习路径覆盖与本批核验（2026-09-29）

本批沿用每日经典的一篇轮转：`load_catalog` 按 `(path, year, title)` 排序，`select_classic` 选下一篇未发送论文。没有新增发信频率、抓取作业或 Zotero 自动导入。候选先查正式题录与摘要，核对作者、年份、期刊、DOI、版本及本地去重，再写入 `verified_review.csv` 和一对一四节导读。导读必须标明实际使用的摘要或全文来源；网页搜索命中不能直接进入生产目录。

| 路径 | 本批后的综述/总览锚点 | 核验状态 |
| --- | --- | --- |
| 01 foundations | *Reinforcement Learning: A Survey*（1996，新增）；既有 HMM tutorial | JAIR 出版页核验新稿 |
| 02 networks | *Deep learning*（2015，新增） | Nature 出版页标为 Review Article |
| 03 architecture | *A survey of multicore processors*（2009，新增） | IEEE 出版页核验题录与摘要 |
| 04 circuits | 既有 *FinFETs: From Devices to Architectures*（2014） | 本批未重新核验既有条目 |
| 05 design automation | *Machine Learning for Electronic Design Automation: A Survey*（2021，新增） | HKUST 机构库给出完整题录、同行评审状态和摘要；ACM 出版页访问验证阻断 |
| 06 AI hardware | 已合并 *Efficient Processing of Deep Neural Networks: A Tutorial and Survey*（2017） | 上批 IEEE 出版页核验 |
| 07 memory computing | 既有 *In-memory computing with resistive switching devices*（2018） | 本批未重新核验既有条目 |

## 本批新稿证据

- 01：JAIR [出版页](https://www.jair.org/index.php/jair/article/view/10166)，DOI `10.1613/jair.301`；1996 年、三位作者与摘要已核。导读只据摘要。
- 02：Nature [出版页](https://www.nature.com/articles/nature14539)，DOI `10.1038/nature14539`；2015 年、三位作者、Review Article 与摘要已核。导读只据摘要。
- 03：IEEE [出版页](https://ieeexplore.ieee.org/document/5230801/)，DOI `10.1109/MSP.2009.934110`；2009 年、三位作者、*IEEE Signal Processing Magazine* 26(6) 26–37 与摘要已核。导读只据摘要和页面可见引言。
- 05：HKUST [机构库记录](https://researchportal.hkust.edu.hk/en/publications/machine-learning-for-electronic-design-automation-a-survey/)，DOI `10.1145/3451179`；2021 年、16 位作者、ACM TODAES 26(5) 文章 40、同行评审状态与摘要已核。导读只据机构库摘要；ACM 页面本次未能直接读取。

## 暂缓候选

- 03：Sparsh Mittal，*A Survey of Techniques for Architecting and Managing Asymmetric Multicore Processors*，ACM Computing Surveys 48(3)，2016，DOI `10.1145/2856125`。Google 索引到 [ACM 页面](https://dl.acm.org/doi/10.1145/2856125)的题名、发表日期和部分摘要；直接访问遇到站点安全验证，未取得可复核的完整摘要。本批选用已核 IEEE 综述，此候选暂不写入目录。
- 05：既有 OpenROAD 条目是流程概览，不能充当对 EDA 研究的全面综述。本批新增的 Huang 等人综述覆盖机器学习用于 EDA 的层级，但也不等于整个 EDA 学科的完整历史。
- 06：Chen 等人的 2020 年加速器综述仍因 ScienceDirect 验证页未核出版方内容，不纳入目录。

## 离线检查

本批草稿目录共 71 条，七路径数量为 13/16/10/7/10/9/6；71 个标识符唯一，71 条导读 manifest 与目录一对一，所有导读均通过四节加载。四篇新稿在实际轮转中排第 7、23、35、56；四篇均通过零日常论文时的经典邮件渲染。完整 pytest 在本机因缺少 `hydra` 未启动，本次没有修改轮转或渲染逻辑。
