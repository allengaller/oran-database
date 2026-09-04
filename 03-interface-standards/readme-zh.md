---
title: "O-RAN 接口标准体系"
description: "O-RAN 定义了一整套开放接口，实现解耦后 RAN 组件之间的互操作。本目录记录各主要接口的协议栈、功能范围与部署考量。"
category: "documentation"
language: "zh-CN"
version: "1.0"
last_updated: "2026-09-03"
keywords: ['AI-RAN', 'RIC']
---

# O-RAN 接口标准体系

## 概述

O-RAN 定义了一整套开放接口，使解耦后的 RAN 组件之间能够互操作。本目录记录各主要接口的协议栈、功能范围与部署考量。

## 文档清单

- [F1 接口](./f1-interface.md) - O-CU 与 O-DU 之间的 F1 接口（3GPP TS 38.473）
- [O-FH 接口](./o-fh-interface.md) - O-DU 与 O-RU 之间的开放前传接口（O-RAN WG4）
- [E2 接口](./e2-interface.md) - 近实时 RIC 与 E2 节点之间的 E2 接口（O-RAN WG3）
- [A1 接口](./a1-interface.md) - 非实时 RIC 与近实时 RIC 之间的 A1 接口（O-RAN WG2）
- [O1 接口](./o1-interface.md) - O1 管理接口（O-RAN WG10）
- [O2 接口](./o2-interface.md) - O-Cloud 管理的 O2 接口（O-RAN WG6）
- [OAM 接口](./oam-interface.md) - 运营、管理与维护（OAM）接口

## 接口架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    SMO / 非实时 RIC                         │
│                         │  A1                                │
│                         ▼                                   │
│              ┌──────────────────┐                          │
│              │    近实时 RIC      │                          │
│              │     (xApps)        │                          │
│              └────────┬─────────┘                          │
│                       │ E2                                  │
│         ┌─────────────┼─────────────┐                      │
│         │             │             │                      │
│    ┌────▼───┐    ┌────▼───┐    ┌───▼────┐                 │
│    │ O-CU-CP│    │ O-CU-UP│    │  O-DU  │                 │
│    └────┬───┘    └────────┘    └───┬────┘                 │
│         │ F1                       │ O-FH                  │
│         └──────────►──────────────┘                        │
│                                  ┌───▼────┐                │
│                                  │  O-RU  │                │
│                                  └────────┘                │
│  O1（SMO ↔ 所有受管实体）                                   │
│  O2（SMO ↔ O-Cloud 基础设施）                              │
└─────────────────────────────────────────────────────────────┘
```

## 接口概要

| 接口 | 连接 | 协议 | 关键标准 |
|------|------|------|----------|
| F1 | O-CU ↔ O-DU | SCTP | 3GPP TS 38.473 |
| O-FH | O-DU ↔ O-RU | eCPRI/IEEE 1914.3 | O-RAN WG4 |
| E2 | 近实时 RIC ↔ E2 节点 | SCTP (E2AP) | O-RAN WG3 |
| A1 | 非实时 RIC ↔ 近实时 RIC | REST/HTTP (JSON) | O-RAN WG2 |
| O1 | SMO ↔ 受管实体 | NETCONF/YANG | O-RAN WG10 |
| O2 | SMO ↔ O-Cloud | REST/HTTP (TOSCA) | O-RAN WG6 |

## 与其他章节的关系

- 负责的工作组：[06-working-groups](../06-working-groups/)
- 标准合规：[09-standards-compliance](../09-standards-compliance/)
- 功能切分选项：[04-disaggregation-options](../04-disaggregation-options/)
- 云集成：[05-cloud-integration](../05-cloud-integration/)
