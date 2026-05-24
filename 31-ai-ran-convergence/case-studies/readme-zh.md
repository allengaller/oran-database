# 行业案例研究：2026 AI-RAN 部署

> **更新：2026-05** | 真实世界的 AI-RAN 部署、试验和启动

## 概述

本目录提供**真实 AI-RAN 部署的详细案例分析**，来自运营商、供应商和 2026 行业活动（MWC、GTC、IEEE ICC）。每个案例研究都包含：

- **背景** — 为什么部署 AI-RAN
- **架构** — 使用的技术栈
- **实现细节** — 代码片段、K8S manifest
- **结果** — 带前后对比的定量指标
- **经验教训** — 有效和无效的部分
- **K8S 工程师要点** — 如何复制

---

## 案例目录

### 1. [SoftBank — 商业 AI-RAN 启动](./softbank.md)
**地点**：日本 | **状态**：2026 年计划商业启动

SoftBank 是首家宣布 2026 年商业 AI-RAN 服务启动计划的主要运营商。该计划将基站重新设想为**多用途 AI + RAN + 边缘计算平台**，通过 B2B 边缘 AI 服务变现过剩 GPU 容量。

**亮点**：
- 时间感知 GPU 分区模型（RAN 优先，AI 弹性）
- 3 个收入流：连接、边缘 AI、数字孪生
- 多租户 K8S 架构
- 2027 年全国推广计划

[阅读完整案例研究](./softbank.md)

---

### 2. [Nokia + NVIDIA — MWC 2026 现场演示](./nokia-nvidia-mwc.md)
**地点**：巴塞罗那 | **状态**：MWC 2026 现场演示

在 **MWC Barcelona 2026**，Nokia 和 NVIDIA 交付了首次公开 **AI-with-RAN** 演示——在**同一 GPU** 上同时运行 5G 基带处理和 AI 推理工作负载，在类似运营商的真实环境中。

**亮点**：
- 3 个演示场景（正常、流量峰值、低峰）
- 定量结果表（吞吐、延迟、功率）
- 现场运营商环境规范
- 完整 K8S manifest

[阅读完整案例研究](./nokia-nvidia-mwc.md)

---

### 3. [T-Mobile + Nokia + NVIDIA — 美国试验](./tmobile-nokia-nvidia.md)
**地点**：美国（Bellevue, WA）| **状态**：2025-2026 现场试验

T-Mobile 的"Un-carrier"战略通过 AI-RAN 试验探索动态 GPU 分区、实时视频分析和企业 AI 捆绑包，针对美国密集城市场景。

**亮点**：
- 流量感知动态分区
- AI 工作负载优雅降级
- B2B 边缘 AI 服务（7 个试点客户）
- 18% 增量收入（初步结果）

[阅读完整案例研究](./tmobile-nokia-nvidia.md)

---

### 4. [Elisa（芬兰）— AI-RAN 现场试验](./elisa.md)
**地点**：赫尔辛基，芬兰 | **状态**：自 2025 年起活跃现场试验

芬兰领先电信运营商 Elisa 自 2018 年以来一直是 **AI 驱动 RAN 自动化**的先驱。2025-2026 年，Elisa 在赫尔辛基启动 **AI-RAN 现场试验**，结合 **NVIDIA Aerial SDK** 与其现有的 **AI 原生运营平台**，在北欧提供首个**商业级自治 RAN**。

**亮点**：
- 自然语言 NOC（LLM 供电）
- 能源节省 xApp（-30% 能源，零 SLA 违规）
- 带数字孪生的预测性维护（-40% 上门维护）
- 赫尔辛基城市 RF 模型

[阅读完整案例研究](./elisa.md)

---

### 5. [SynaXG + Eridan — 6G AI 原生无线电](./synaxg-eridan.md)
**地点**：美国 + 日本 | **状态**：活跃研发合作

**SynaXG**（斯坦福研究衍生的 AI-RAN 初创公司）和 **Eridan**（**数字 RF** 和 **Miracle Chip™** 硅片领导者）在 2025 年宣布合作开发 **AI 原生 6G 无线电**，将 AI 直接集成到**太赫兹 (THz) RF 层**。

**亮点**：
- GNN 用于 140 GHz 波束预测（-30% 对齐时间）
- Transformer 在线信道估计
- 实时数字孪生用于在线学习
- Eridan Miracle Chip™ 数字 RF

[阅读完整案例研究](./synaxg-eridan.md)

---

### 6. [LITEON DGX Spark — GTC 2026](./liteon-gtc.md)
**地点**：全球 | **状态**：在 NVIDIA GTC 2026 发布

在 **NVIDIA GTC 2026**，**LITEON Technology**（台湾电子制造商）发布了 **DGX Spark for Telecom** —— 紧凑、加固的边缘计算平台，专为**基站 AI-RAN 部署**设计。

**亮点**：
- NEBS Level 3 认证
- -48V DC 供电（电信标准）
- 预验证参考架构（Nokia、Rakuten、srsRAN）
- 预配置 K3s 栈
- 5 年 TCO 节省 27%

[阅读完整案例研究](./liteon-gtc.md)

---

### 7. [VIAVI + NVIDIA — 数字孪生测试集成](./viava-nvidia.md)
**地点**：全球 | **状态**：2025-2026 战略合作伙伴关系

**VIAVI Solutions**（网络测试和测量设备领导者）在 2025-2026 年深化了与 **NVIDIA** 的合作，为 AI-RAN 提供**集成测试和数字孪生解决方案**。该组合 **VIAVI + NVIDIA AODT** 平台使运营商能够预验证 AI 代理操作、生成训练数据、运行合规测试和模拟故障场景。

**亮点**：
- TM500 UE 模拟器 + AODT 集成
- NITRO 测试自动化
- 合规工件生成（O-RAN WG11、GDPR）
- CI/CD 管道集成

[阅读完整案例研究](./viava-nvidia.md)

---

## 比较矩阵

| 案例 | 地点 | 状态 | 焦点 | 关键指标 |
|:---|:---|:---|:---|:---|
| **SoftBank** | 日本 | 商业启动 | 基站即平台 | +130% 收入潜力 |
| **Nokia+MWC** | 巴塞罗那 | 现场演示 | GPU 共享 | RAN SLO 维持 |
| **T-Mobile** | 美国 | 现场试验 | 城市部署 | +18% 收入 |
| **Elisa** | 芬兰 | 现场试验 | 自治 RAN | -30% 能源 |
| **SynaXG+Eridan** | 美国+日本 | 研发 | 6G AI 原生 | -29% 波束时间 |
| **LITEON** | 全球 | 已发布 | 边缘硬件 | -27% TCO |
| **VIAVI+NVIDIA** | 全球 | 合作 | 测试+孪生 | 提前 6 个月启动 |

---

## 2026 AI-RAN 关键主题

### 主题 1：动态 GPU 分区
每个案例都展示了一种在 RAN 和 AI 工作负载之间动态分区 GPU 的方法。关键技术：
- **NVIDIA MIG** — 硬件级隔离
- **时间感知调度** — 基于一天中的时间分区
- **流量感知调度** — 基于实时 RAN 负载分区
- **优雅降级** — AI 工作负载在 RAN 峰值时缩减

### 主题 2：数字孪生作为强制
没有案例在没有数字孪生的情况下部署 AI-RAN。孪生用于：
- 生产前的 AI 代理操作预验证
- 生成合成训练数据
- 实时漂移检测
- 故障场景模拟

### 主题 3：B2B 边缘 AI 变现
运营商不再将 RAN 视为成本中心。AI-RAN 实现新的 B2B 收入流：
- 视频分析（智慧城市、零售）
- 预测性维护（工业 IoT）
- 数字孪生即服务（城市规划）
- GPU 即服务（第三方 AI 工作负载）

### 主题 4：硬件成熟
2026 标志着 AI-RAN 从参考设计转向生产就绪硬件：
- **NVIDIA ARC-Compact** — 参考平台
- **LITEON DGX Spark** — 生产级 COTS
- **SynaXG + Eridan** — AI 原生 THz 无线电
- **NEBS 认证** — 电信级合规

### 主题 5：多供应商生态系统
无案例依赖单一供应商。所有部署都集成：
- 运营商（T-Mobile、SoftBank、Elisa）
- 硬件供应商（NVIDIA、LITEON、Eridan）
- 软件供应商（Nokia、Rakuten）
- 测试供应商（VIAVI）
- 云提供商（AWS 用于 AODT）

---

## K8S 工程师要点

### 模式 1：MIG 分区
每个案例都使用 NVIDIA MIG 隔离 RAN 和 AI 工作负载。参考模式：

```yaml
resources:
  limits:
    nvidia.com/mig-1g.6gb: 1  # L4 上的 1 个 MIG 切片
```

### 模式 2：实时内核
实时内核对基站非协商项。关键配置：
- PREEMPT_RT 补丁
- CPU 隔离（`isolcpus`）
- PTP 时间同步
- 实时调度器

### 模式 3：多租户 K8S
B2B 服务需要强隔离：
- 每客户命名空间
- 网络策略（默认拒绝）
- 资源配额（GPU、CPU、内存）
- 审计日志（用于合规）

### 模式 4：GPU 可观测性
每个案例都使用 **DCGM Exporter** 进行 GPU 监控：

```yaml
# 关键 GPU 指标
- DCGM_FI_DEV_GPU_UTIL          # GPU 利用率
- DCGM_FI_DEV_FB_USED           # 帧缓冲区使用
- DCGM_FI_DEV_GPU_TEMP          # 温度
- DCGM_FI_PROF_SM_ACTIVE        # SM 活跃度
```

---

## 部署时间表

```
2024 ──────────── 2025 ──────────── 2026 ──────────── 2027
  │                │                │                │
  │  Elisa 开始    │  T-Mobile      │  SoftBank      │  全国
  │  AI RAN 研究   │  实验室试验    │  商业启动      │  推广
  │                │  MWC 演示      │  LITEON        │
  │                │  研发          │  VIAVI+NVIDIA  │
  │                │  SynaXG+Eridan │  GTC 发布      │
```

---

## 额外资源

### 视频演示

- [MWC 2026 Nokia+NVIDIA 演示](https://www.nokia.com/mwc2026)
- [GTC 2026 LITEON DGX Spark 发布](https://www.nvidia.com/gtc/)
- [Elisa AI-RAN 现场演示](https://elisa.fi/en/ai-ran)

### 运营商白皮书

- [SoftBank AI-RAN 白皮书 (2024.12)](https://www.softbank.jp/corp/set/data/technology/research/story-event/ai-ran)
- [T-Mobile Un-carrier AI 战略](https://www.t-mobile.com/news/)
- [Elisa AI-RAN 案例研究](https://elisa.fi/en/ai-ran)

### 行业标准

- [AI-RAN 联盟](https://ai-ran.org/)
- [O-RAN 联盟](https://www.o-ran.org/)
- [3GPP 6G 研究项目](https://www.3gpp.org/release-20)

---

## 贡献

要添加新案例研究：

1. 确保是真实部署（非假设）
2. 包括定量结果（指标、KPI）
3. 提供架构图
4. 记录经验教训（不仅是成功）
5. 包括 K8S manifest 或代码片段
6. 用交叉引用更新本 README
