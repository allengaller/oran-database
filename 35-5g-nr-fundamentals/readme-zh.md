---
title: "5G NR 基础知识"
description: "本节涵盖 5G NR（新空口）系统的基本概念与技术概览，包括架构、性能、频谱、部署、演进等内容。"
category: "documentation"
language: "zh-CN"
version: "1.0"
last_updated: "2026-09-03"
keywords: ['5G', 'NR', '新空口', 'NG-RAN', '5GC', 'eMBB', 'URLLC', 'mMTC']
---

# 5G NR 基础知识

## 概述
本节提供 5G NR（新空口）系统的全面技术概览，面向云平台运维专业人员，涵盖从 1G 到 5G 的演进、系统架构、关键性能指标、频谱利用、部署策略与未来演进路径。内容基于 3GPP 规范和行业最佳实践，兼顾理论基础与实践经验。

## 关键主题

### 1. 5G 概述与演进
- **定义与目标**: 理解 IMT-2020 标准与 5G 目标
- **技术演进**: 从 1G 模拟到 5G NR 的数字化转型
- **三大场景**: eMBB、URLLC 和 mMTC 应用
- **标准化进展**: 3GPP R15/16/17/18 特性与时间线

### 2. 5G NR 架构
- **5G 系统架构（5GS）**: UE、NG-RAN 与 5GC 组成
- **NG-RAN 架构**: gNB 功能、接口与部署选项
- **核心网（5GC）**: 服务化架构与网络功能
- **CU-DU 分离**: 集中单元与分布单元配置

### 3. 关键性能指标
- **峰值速率**: 下行 20 Gbps、上行 10 Gbps
- **时延**: 用户面 1-4ms，URLLC <1ms
- **连接密度**: 每平方公里 100 万设备
- **移动性**: 支持高达 500 km/h
- **能效**: 较 4G 提升 100 倍

### 4. 5G NR 频谱
- **FR1（Sub-6 GHz）**: 广覆盖主要频段
- **FR2（毫米波）**: 大容量高频段
- **频谱共享**: 载波聚合、双连接
- **动态频谱共享（DSS）**: 4G/5G 共存

### 5. 与 4G LTE 的对比
- **技术差异**: OFDMA、灵活 numerology、波束赋形
- **性能提升**: 峰值速率提升 20 倍、时延降低 10 倍
- **架构演进**: 从 EPC 到 5GC 服务化架构
- **部署模式**: NSA 与 SA 策略及权衡

## 文档清单

- [5G NR 系统概述](./5g-nr-system-overview.md) - 5G NR 系统综合概览
- [5G NR 物理层](./5g-nr-physical-layer.md) - 物理层技术详解
- [5G NR 协议栈](./5g-nr-protocol-stack.md) - MAC、RLC、PDCP、RRC 协议详解
- [5G NR 关键技术](./5g-nr-key-technologies.md) - 大规模 MIMO、波束赋形、网络切片等
- [5G NR 与 O-RAN 集成](./5g-nr-o-ran-integration.md) - 5G NR 与 O-RAN 架构的融合
- [5G NR 学习指南](./5g-nr-learning-guide.md) - 系统化的学习路径与资源

## 目标读者
- 云平台运维专业人员
- 网络工程师与架构师
- 5G 系统集成商
- 技术经理与决策者
- 电信专业的学生与研究人员

## 相关章节
- **01-architecture-system/**: O-RAN 架构基础
- **02-core-components/**: O-RAN 组件说明
- **03-interface-standards/**: O-RAN 接口规范
- **31-ai-ran-convergence/**: AI 与 RAN 融合技术
