---
title: "34. O-RAN/AI-RAN 主要厂商档案"
description: "本章节为 O-RAN 和 AI-RAN 生态系统中的主要厂商建立独立企业档案，涵盖设备商、芯片商、云服务商和测试厂商的产品线、技术能力和市场定位。"
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-08-25"
keywords: ['AI-RAN', 'RIC', '5G']
---

# 34. O-RAN/AI-RAN 主要厂商档案

## 概述

本章节为 O-RAN 和 AI-RAN 生态系统中的主要厂商建立独立企业档案，涵盖设备商、芯片商、云服务商和测试厂商的产品线、技术能力和市场定位。

## 厂商分类

### 设备商（RAN Infrastructure）

| 厂商 | 总部 | O-RAN 产品线 | AI-RAN 能力 | 文档链接 |
|------|------|--------------|-------------|----------|
| **Ericsson** | 瑞典 | Ericsson RAN Compute, Open RAN | AI/ML 优化, 与 NVIDIA 合作 | [详细档案](./ericsson/) |
| **Nokia** | 芬兰 | Nokia AirScale, ReefShark | MantaRay NM, AI-RAN 联合方案 | [详细档案](./nokia/) |
| **Samsung** | 韩国 | Samsung vRAN 3.0 | AI-RAN 解决方案 | [详细档案](./samsung/) |
| **Mavenir** | 美国 | Cloud RAN, Open RAN | RIC 集成, AI/ML | [详细档案](./mavenir/) |
| **Huawei** | 中国 | 5G RAN, O-RAN 兼容方案 | AI 节能, 智能运维 | [详细档案](./huawei/) |
| **ZTE** | 中国 | 5G RAN, UniSeer | AI 优化, 智能网络 | [详细档案](./zte/) |

### 芯片/平台商（Semiconductor & Platforms）

| 厂商 | 产品线 | AI-RAN 角色 | 文档链接 |
|------|--------|-------------|----------|
| **NVIDIA** | ARC/ARC-Compact, cuMAC, Aerial SDK | GPU 加速 RAN, AI 训练/推理 | [详细档案](./nvidia/) |
| **Qualcomm** | FSM, QCS | 基带芯片, 边缘 AI | [详细档案](./qualcomm/) |
| **Intel** | FlexRAN, Xeon | 通用处理器 RAN, vRAN | [详细档案](./intel/) |

### 测试与测量厂商（Test & Measurement）

| 厂商 | 产品线 | 文档链接 |
|------|--------|----------|
| **Viavi Solutions** | TM500, T-BERD, NITRO | [详细档案](./viavi/) |
| **Keysight Technologies** | UXM, PathWave, Open RAN Studio | [详细档案](./keysight/) |

## 选型参考

### 按部署场景选择

| 场景 | 推荐厂商组合 |
|------|--------------|
| **大型运营商（全国网）** | Ericsson/Nokia + NVIDIA + Keysight |
| **中型运营商（区域网）** | Samsung/Mavenir + Intel + Viavi |
| **企业专网** | Mavenir/Parallel Wireless + NVIDIA ARC-Compact |
| **新兴市场** | ZTE/Mavenir + Qualcomm |

### 按技术路线选择

| 技术路线 | 核心厂商 | 适用场景 |
|----------|----------|----------|
| **Cloud-Native RAN** | Mavenir, Samsung | 云原生架构, 弹性扩缩 |
| **GPU-Accelerated RAN** | NVIDIA + Ericsson/Nokia | 高性能, AI 密集型 |
| **传统 RAN 演进** | Ericsson, Nokia, Huawei | 存量网络升级 |
| **Open RAN 绿色部署** | Mavenir, Parallel Wireless | 新建网络, 成本敏感 |

## 学习路径

1. **了解市场格局**: 从 [vendor-solutions-landscape](../31-ai-ran-convergence/product-solutions/) 开始
2. **深入厂商技术**: 按需阅读各厂商详细档案
3. **对比评估**: 参考各厂商的性能基准和成本模型
4. **选型决策**: 结合场景和技术路线选择合适方案

## 相关章节

- [31. AI-RAN 融合](../31-ai-ran-convergence/) - AI-RAN 技术深度
- [20. 生态与合作伙伴](../20-ecosystem-partnership/) - 合作模式
- [18. 成本效益分析](../18-cost-benefit-analysis/) - TCO/ROI 模型

---

*Last Updated: August 2026*
