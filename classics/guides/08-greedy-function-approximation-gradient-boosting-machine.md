# 导读 08｜梯度提升：在函数空间逐步逼近目标

Jerome H. Friedman，*The Annals of Statistics* 29(5)，1189–1232（2001）。[DOI](https://doi.org/10.1214/aos/1013203451) · [Project Euclid 出版方论文页与摘要](https://projecteuclid.org/journals/annals-of-statistics/volume-29/issue-5/Greedy-function-approximation-A-gradient-boosting-machine/10.1214/aos/1013203451.full)。

## 为什么读

本文把 boosting 表述为函数空间中的数值优化：模型不是一次拟合完成，而是逐轮加入简单函数，让组合预测逐步改善。这个视角把“提升”从某一种分类器组合技巧推广为可按损失函数设计的算法框架。

## 核心思想

作者以 stagewise additive expansion 表示预测函数，每轮选择一个新的基函数及其系数，使选定损失下降；在函数空间中，这与沿负梯度方向前进相联系。论文分别给出平方误差、绝对误差、Huber-M 回归损失和多类别 logistic 分类的算法，并讨论把回归树作为基学习器时的具体增强方式。树模型便于处理非线性和交互，但每轮仍是贪心添加，不能由此推出全局最优。

## 对后续学习的作用

读后可用“损失是什么、每轮拟合什么、组合如何累积”拆解现代 boosting 实现，并区分通用梯度提升框架与特定树模型实现。**IC 设计阅读延伸**：若用树模型估计设计质量，逐轮优化损失的思路可帮助理解 surrogate-based 搜索；论文没有研究 EDA，也不保证代理指标与真实 PPA 一致。

## 阅读前置与思考题

前置概念：经验风险、梯度下降、加性模型、回归树与分类损失。可先读摘要及第 2 节的函数空间视角，再看第 4 节的树提升。

思考题：若目标损失对异常值敏感，平方误差与 Huber-M 会怎样影响每轮新增树所拟合的方向？
