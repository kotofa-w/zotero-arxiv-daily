# 导读 61｜忆阻器与 CMOS 混合集成的可重构逻辑

Qiangfei Xia、Warren Robinett、Michael W. Cumbie、Neel Banerjee、Thomas J. Cardinali、J. Joshua Yang、Wei Wu、Xuema Li、William M. Tong、Dmitri B. Strukov、Gregory S. Snider、Gilberto Medeiros-Ribeiro 与 R. Stanley Williams，2009，Nano Letters。正式题录：[DOI 10.1021/nl901874j](https://doi.org/10.1021/nl901874j)；出版方论文入口：[ACS Publications](https://pubs.acs.org/doi/10.1021/nl901874j)。事实依据为出版方摘要的 OpenAlex 转录，未核全文。

## 为什么读

忆阻器交叉阵列具有密集互连和可编程电阻状态的特点，可能与 CMOS 逻辑形成互补。本文展示了把忆阻器器件与 CMOS 电路结合、用于可重构逻辑的研究路径，是从器件特性走向电路功能的实例。

## 核心思想

论文研究混合忆阻器—CMOS 集成结构，利用可编程器件网络实现可重构逻辑功能，并报告了器件/电路层面的实验展示。理解结论时应区分单元器件行为、阵列连线与完整逻辑系统：小规模功能演示不等于已解决大规模制造、可靠性、写入能耗和互连问题。具体器件材料和制程结论应以论文实验条件为准。

## 对后续学习的作用

可据此追踪新型存储器如何承担逻辑功能，再与后来的 ISAAC、PRIME 和 RRAM 计算芯片比较模拟计算、存储和外围 CMOS 的分工。**IC 设计阅读延伸**：可探讨可重构逻辑阵列在可编程电路中的潜力，但本文不是主流数字标准单元流程的量产验证。

## 阅读前置与思考题

前置概念：CMOS 逻辑、忆阻器电阻状态、交叉阵列和可重构电路。思考：逻辑功能映射到器件电导后，写入误差和器件离散性怎样影响正确性？外围 CMOS 可能承担哪些阵列难以完成的任务？
