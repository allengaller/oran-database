---
title: "O-RAN 解耦选项"
description: "本节介绍 O-RAN 架构的解耦与功能切分选项，包括前传切分、性能影响、部署场景与成本效益分析。"
category: "documentation"
language: "zh-CN"
version: "1.0"
last_updated: "2026-09-03"
keywords: ['O-RAN', '功能切分', '解耦', '前传', '7.2x']
---

# O-RAN 解耦选项

## 概述

O-RAN 的核心特征之一是将 RAN 功能解耦到 O-RU、O-DU 和 O-CU。选择在协议栈的哪个位置进行切分，需要在前传带宽、时延、硬件成本和部署灵活性之间进行权衡。本目录记录可用的切分选项及其实际影响。

## 文档清单

- [功能切分](./functional-splits.md) - 3GPP/O-RAN 功能切分选项（Split 1–8）总览
- [前传切分](./fronthaul-splits.md) - Split 7.2x 及其他前传切分变体的深入解析
- [性能影响](./performance-impact.md) - 各切分方案对时延、带宽和处理能力的影响
- [部署场景](./deployment-scenarios.md) - 宏站、小站、农村及企业部署的切分选择
- [成本效益分析](./cost-benefit-analysis.md) - 不同解耦方案的 TCO 对比

## 切分选项概览

| 切分 | 边界 | 前传带宽（100 MHz, 4T4R） | 时延敏感度 | 池化收益 |
|------|------|--------------------------|------------|----------|
| Split 8 | PHY–RF | 极高（CPRI） | 极高 | 无 |
| Split 7.2x | 低PHY–高PHY | 约 10–25 Gbps | 高（<250 µs） | DU 池化 |
| Split 6 | MAC–PHY | 中等 | 中 | 部分池化 |
| Split 2 | PDCP–RLC | 约 4 Gbps | 低 | CU/DU 完全池化 |

## 关键考量

1. **传输网络能力** - 可用的前传带宽与时延预算
2. **算力部署位置** - 哪些功能最适合云化池化
3. **厂商生态** - O-RU 对所选切分的支持情况（7.2x 为 O-RAN 默认）
4. **频谱与带宽** - 更宽的信道会使前传负载成倍增长

## 与其他章节的关系

- 核心组件：[02-core-components](../02-core-components/)
- O-FH 接口：[03-interface-standards](../03-interface-standards/o-fh-interface.md)
- 云集成：[05-cloud-integration](../05-cloud-integration/)
- 成本分析：[18-cost-benefit-analysis](../18-cost-benefit-analysis/)
