---
title: "O-RAN 核心组件"
description: "本节介绍 O-RAN 架构的核心功能组件，包括 O-CU、O-DU、O-RU、RIC 和 SMO，涵盖其角色、功能与部署考量。"
category: "documentation"
language: "zh-CN"
version: "1.0"
last_updated: "2026-09-03"
keywords: ['O-RAN', 'O-CU', 'O-DU', 'O-RU', 'RIC', 'SMO']
---

# O-RAN 核心组件

## 概述

O-RAN 将传统基站解耦为开放、可互操作的组件。本目录记录 O-RAN 架构中各核心组件的功能范围、内部结构、接口及部署考量。

## 文档清单

- [O-RU（开放射频单元）](./o-ru.md) - 负责射频与低物理层处理的射频单元
- [O-DU（开放分布单元）](./o-du.md) - 负责 RLC、MAC 与高物理层的分布单元
- [O-CU（开放集中单元）](./o-cu.md) - 负责 RRC、SDAP 与 PDCP 的集中单元
- [O-CU-CP / O-CU-UP](./o-cucp-cuup.md) - O-CU 的控制面与用户面分离
- [O-RIC（RAN 智能控制器）](./o-ric.md) - 实现网络智能控制的近实时与非实时 RIC
- [SMO（服务管理与编排）](./smo.md) - 端到端管理、编排与非实时 RIC 承载

## 组件架构总览

```
┌─────────────────────────────────────────────┐
│       SMO（含非实时 RIC / rApps）           │
└───────────────────┬─────────────────────────┘
                    │
            ┌───────▼────────┐
            │   近实时 RIC   │
            │    (xApps)     │
            └───────┬────────┘
                    │
        ┌───────────┼────────────┐
        │           │            │
   ┌────▼────┐ ┌────▼────┐  ┌───▼───┐
   │ O-CU-CP │ │ O-CU-UP │  │ O-DU  │
   └─────────┘ └─────────┘  └───┬───┘
                                │
                            ┌───▼───┐
                            │ O-RU  │
                            └───────┘
```

## 组件概要

| 组件 | 协议层功能 | 关键接口 | 典型部署位置 |
|------|-----------|----------|--------------|
| O-RU | 射频、低物理层 | O-FH | 基站站址 |
| O-DU | RLC、MAC、高物理层 | O-FH、F1、E2 | 边缘/区域云 |
| O-CU-CP | RRC、PDCP-C | F1-C、E1、E2、NG-C | 区域/中心云 |
| O-CU-UP | SDAP、PDCP-U | F1-U、E1、NG-U | 区域/中心云 |
| 近实时 RIC | 10ms–1s 控制环 | E2、A1、O1 | 边缘云 |
| SMO / 非实时 RIC | >1s 编排与策略 | A1、O1、O2 | 中心云 |

## 与其他章节的关系

- 整体架构：[01-architecture-system](../01-architecture-system/)
- 接口规范：[03-interface-standards](../03-interface-standards/)
- 功能切分选项：[04-disaggregation-options](../04-disaggregation-options/)
- RIC 开发：[07-ric-development](../07-ric-development/)
