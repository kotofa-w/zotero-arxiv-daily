# 导读 62｜ISAAC：在忆阻器交叉阵列中执行 CNN 计算

Ali Shafiee、Anirban Nag、Naveen Muralimanohar、Rajeev Balasubramonian、John Paul Strachan、Miao Hu、R. Stanley Williams 与 Vivek Srikumar，2016，ISCA。正式题录：[DOI 10.1109/ISCA.2016.12](https://doi.org/10.1109/ISCA.2016.12)；出版方论文入口：[IEEE Xplore](https://ieeexplore.ieee.org/document/7551379)。事实依据为出版方摘要的 OpenAlex 转录，未核全文。

## 为什么读

卷积神经网络包含大量矩阵向量乘法，而电阻式存储器交叉阵列可利用电导与输入电压进行模拟乘加。ISAAC 研究如何围绕这种存内计算原语构建完整加速器，并处理阵列精度、数据流和外围电路问题。

## 核心思想

论文提出由忆阻器交叉阵列执行神经网络计算，并用数字逻辑和存储层级配套处理转换、控制及非线性等步骤。架构将模拟计算阵列组织成流水化单元以支持 CNN 推理。论文的性能/能效结论来自其架构评估和器件假设；不应误读为论文已经制造并实测了所有架构部件。模拟误差、ADC/DAC、写入与数据搬运均会影响系统级收益。

## 对后续学习的作用

可与 PRIME 比较：ISAAC 聚焦神经网络加速器组织，PRIME 将计算能力嵌入主存语境。**IC 设计阅读延伸**：探索存内计算用于 EDA 时，要确认矩阵运算是否占主导、精度是否容许模拟误差；这是研究假设，不是论文验证的应用。

## 阅读前置与思考题

前置概念：CNN 推理、交叉阵列、电导求和、ADC/DAC 和存储层次。思考：当模拟阵列完成乘加后，数据转换成本会不会抵消计算节省？哪些算子仍需要数字逻辑？
