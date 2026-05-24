# O-RAN 学术论文集合

## 概述
本目录包含与 O-RAN（开放无线接入网）技术相关的学术论文、研究出版物和技术研究报告的综合集合。论文按技术领域组织，便于研究和学习。

## 论文分类

### 架构论文 (`/architecture`)
专注于 O-RAN 架构设计、参考模型和系统级分析的研究论文。
- O-RAN 参考架构研究
- RAN 中的网络功能虚拟化
- 云原生 RAN 架构
- 多域编排论文

### RIC 和 AI 论文 (`/ric-ai`)
涵盖 RIC（RAN 智能控制器）架构、机器学习应用和智能算法的论文。
- RIC 架构和设计原则
- xApps/rApps 开发和部署
- 用于无线资源管理的 AI/ML
- 使用机器学习的网络优化
- 预测性维护和异常检测

### 接口标准论文 (`/interfaces`)
分析 O-RAN 接口协议、标准和互操作性的技术论文。
- E2 接口协议分析
- A1 接口策略管理
- O1 接口 NETCONF/YANG 模型
- F1 和 O-FH 接口规范
- 接口安全和性能研究

### 部署论文 (`/deployment`)
关于 O-RAN 部署策略、实施挑战和运营方面的研究。
- O-RAN 部署架构
- 硬件和基础设施要求
- 集成测试方法论
- 性能基准测试研究
- 运营挑战和解决方案

### 标准和合规论文 (`/standards`)
研究 O-RAN 标准化工作、合规测试和行业采用的论文。
- O-RAN 联盟规范分析
- ETSI 和 3GPP 标准集成
- 一致性测试方法论
- 多厂商互操作性研究
- 认证和合规框架

### 应用论文 (`/applications`)
探索 O-RAN 在各个领域和用例中应用的研究论文。
- 使用 O-RAN 的 5G 网络切片
- 工业互联网应用
- 联网车辆通信
- 智慧城市部署
- 边缘计算集成

### 调查论文 (`/surveys`)
提供 O-RAN 技术格局概述的综合性调查论文。
- O-RAN 技术调查
- 与传统 RAN 的比较研究
- 市场分析和采用趋势
- 未来研究方向
- 最新技术综述

### 2026 AI-RAN 论文 (`/ai-ran-2026`)  ← **2026年5月新增**
2026 年发表的 **AI-RAN 融合**前沿论文，涵盖 Agentic AI、数字孪生、6G AI 原生设计、后量子安全和真实部署案例。
- **Agentic AI** — 多层自治代理（战略/战术/反应层）
- **数字孪生** — NVIDIA AODT、实时同步、预验证
- **6G AI 原生** — 太赫兹、语义通信、物理信息机器学习
- **联邦学习** — 跨运营商隐私保护训练
- **安全** — 对抗攻击、后量子密码、AI-RAN 零信任
- **案例研究** — SoftBank、Nokia+MWC、Elisa、SynaXG+Eridan、LITEON、VIAVI

**完整论文目录**：参见 [AI-RAN 2026 论文索引](./ai-ran-2026/)
**深度解读**：参见 [31-ai-ran-convergence/paper-deep-dive](../31-ai-ran-convergence/paper-deep-dive/)

---

## 2026 AI-RAN 论文亮点（快速参考）

### 里程碑论文

| 论文 | 来源 | 年份 | 深度解读 |
|:---|:---|:---|:---|
| **Toward Autonomous O-RAN: Multi-Scale Agentic AI Framework** | arXiv 2602.14117 | 2026.2 | [阅读](../31-ai-ran-convergence/paper-deep-dive/arxiv-2602-14117.md) |
| **AI for Next-Generation 6G Technologies and Networks** | Springer | 2026.2 | [阅读](../31-ai-ran-convergence/paper-deep-dive/springer-6g-ai.md) |
| **AI-RAN: The Pathway to Future Wireless Networks** | ScienceDirect (ICT Express) | 2026 | [阅读](../31-ai-ran-convergence/paper-deep-dive/sciencedirect-2026.md) |
| **AI-Based Resource Management for O-RAN: Survey** | ScienceDirect (Ad Hoc Networks) | 2026.4 | [阅读](../31-ai-ran-convergence/paper-deep-dive/sciencedirect-survey-2026.md) |

### 2026 关键主题

1. **Agentic AI** — 基于 LLM 的战略代理 + DRL 战术代理 + 快速反应代理
2. **数字孪生成为基础** — AODT 和定制孪生现已成为安全的强制要求
3. **AI-RAN 作为平台** — 运营商通过 B2B AI 服务变现基站 GPU
4. **6G AI 原生设计** — AI 设计入物理层，而非外挂
5. **AI 安全** — 新威胁模型：AI 攻击 AI
6. **后量子过渡** — NIST PQC 标准（Kyber、Dilithium）集成到 O-RAN 接口

---

## 论文元数据格式

每个论文条目应包括：
- **标题**：完整论文标题
- **作者**：作者姓名和所属机构
- **出版物**：会议/期刊名称和年份
- **摘要**：关键贡献的简要总结
- **主要发现**：主要结果和含义
- **相关性**：如何应用于 O-RAN 实践
- **链接**：可用时提供 DOI 或直接访问链接

## 贡献

添加新论文的方法：
1. 将论文 PDF/文本放在相应的子目录中
2. 创建相应的元数据文件（.md）包含论文详细信息
3. 遵循命名约定：`作者_年份_标题_简短.md`
4. 用新条目更新类别 README

## 重要说明

- 所有论文都应正确引用完整的书目信息
- 尽可能关注同行评议的出版物
- 包括理论研究和实际实施研究
- 论文应与当前的 O-RAN 标准和实践相关
- 定期更新以反映最新的研究进展