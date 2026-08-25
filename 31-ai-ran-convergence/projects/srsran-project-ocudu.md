---
title: "srsRAN Project (OCUDU) 详细研究文档"
description: "对 srsRAN Project（现为 OCUDU）的全面研究分析，涵盖技术架构、功能特性、开发环境、性能基准等多个维度。"
category: "documentation"
language: "zh-CN"
version: "1.0"
last_updated: "2026-08-25"
keywords: ['srsRAN', 'OCUDU', '5G', 'O-RAN', 'AI-RAN']
---

# srsRAN Project (OCUDU) 详细研究文档

## 文档概述
本文档提供对 srsRAN Project（现为 OCUDU - Open Centralized Unit/Distributed Unit）的全面研究分析，涵盖技术架构、功能特性、开发环境、性能基准、应用场景及未来发展等多个维度。文档基于 srsRAN 官方文档、GitHub 仓库、学术论文及行业分析报告综合整理。

## 目录
1. [项目概述](#1-项目概述)
2. [技术架构](#2-技术架构)
3. [主要功能特性](#3-主要功能特性)
4. [应用场景](#4-应用场景)
5. [开发环境搭建](#5-开发环境搭建)
6. [代码结构分析](#6-代码结构分析)
7. [性能基准测试](#7-性能基准测试)
8. [与竞品对比](#8-与竞品对比)
9. [创业机会分析](#9-创业机会分析)
10. [求职相关技能要求](#10-求职相关技能要求)
11. [学习资源与社区](#11-学习资源与社区)
12. [未来发展方向](#12-未来发展方向)

---

## 1. 项目概述

### 1.1 项目背景
srsRAN Project 是由 Software Radio Systems (SRS) 开发的开源 5G CU/DU 解决方案。2025 年 12 月，项目正式转型为 OCUDU（Open Centralized Unit/Distributed Unit），并在 Linux Foundation 下进行中立治理。这一转型标志着项目从单一厂商主导转向社区驱动的开源生态系统。

### 1.2 项目定位
OCUDU 是一个完整的 RAN 解决方案，符合 3GPP 和 O-RAN Alliance 规范。项目包含完整的 L1/L2/L3 协议栈，具有最少的外部依赖。软件可移植到不同处理器架构，从低功耗嵌入式系统到云 RAN 均可扩展，为移动无线研究和开发提供强大平台。

### 1.3 项目目标
1. **开放性**：基于开放标准，支持多厂商互操作
2. **运营商级**：提供生产就绪的 RAN 解决方案
3. **可扩展性**：从嵌入式设备到云原生部署
4. **模块化**：支持 CU/DU 分离和灵活部署
5. **AI 原生**：为 AI-RAN 优化提供基础平台

### 1.4 项目仓库信息
- **原仓库**：https://github.com/srsran/srsran_project（已存档）
- **新仓库**：https://gitlab.com/ocudu/ocudu
- **许可证**：Apache 2.0（permissive license）
- **主要语言**：C++ (C++17)
- **治理机构**：Linux Foundation OCUDU Ecosystem Foundation
- **贡献者**：全球 21+ 组织成员

### 1.5 版本演进
- **srsRAN 4G**：早期 LTE 实现
- **srsRAN Project v23.x**：5G NR 初始版本
- **srsRAN Project v24.x**：O-RAN CU/DU 分离
- **OCUDU 26.04**：首个 OCUDU 版本，Linux Foundation 治理

---

## 2. 技术架构

### 2.1 整体架构设计

#### 2.1.1 O-RAN gNB 架构
OCUDU 实现了完整的 O-RAN 合规 gNB 架构，采用 Split 7.2x 功能分割：

```
┌─────────────────────────────────────────────────────────────────────┐
│                        nearRT-RIC (E2 接口)                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   CU-CP     │  │   CU-UP     │  │  DU-high    │  │  DU-low     │ │
│  │  (RRC/PDCP) │  │  (SDAP/PDCP)│  │ (RLC/MAC)   │  │  (Low PHY)  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │
│         │                │                │                │         │
│         └──── E1 ────────┘                │                │         │
│                    │                      │                │         │
│                    ├──── F1-c ────────────┤                │         │
│                    ├──── F1-u ────────────┤                │         │
│                                             ├──── FAPI+ ──┘         │
│                                                          │           │
│                                                    O-RU (Split 7.2x)│
└─────────────────────────────────────────────────────────────────────┘
```

#### 2.1.2 CU/DU 分离架构
| 组件 | 包含层 | 主要功能 |
|------|--------|----------|
| **CU-CP** | RRC, PDCP-C | 控制面处理，RRC 连接管理 |
| **CU-UP** | SDAP, PDCP-U | 用户面处理，数据转发 |
| **DU-high** | RLC, MAC | 无线资源管理，调度 |
| **DU-low** | Low PHY | 物理层处理，编码/解码 |

### 2.2 O-RAN 接口实现

#### 2.2.1 E2 接口
- 连接 CU/DU 与 nearRT-RIC
- 支持 E2AP 协议
- 实现 xApp 订阅和指示
- 支持 RAN 功能控制

#### 2.2.2 F1 接口
- **F1-C**：CU-CP 与 DU-high 之间的控制面接口
- **F1-u**：CU-UP 与 DU-high 之间的用户面接口
- 支持 F1AP 协议

#### 2.2.3 E1 接口
- CU-CP 与 CU-UP 之间的接口
- 支持 E1AP 协议
- 管理 Bearer 上下文

#### 2.2.4 其他接口
- **NG 接口**：gNB 与 5G Core 之间的接口
- **Xn 接口**：gNB 之间的接口
- **FAPI+ 接口**：DU-high 与 DU-low 之间的接口

### 2.3 5G NR 协议栈

#### 2.3.1 物理层 (PHY)
- 支持 3GPP Release 17
- FDD/TDD 支持，所有 FR1 频段
- 15/30 kHz 子载波间隔
- 高度优化的 LDPC 和 Polar 编码器/解码器
- 支持 ARM Neon 和 x86 AVX2/AVX512 指令集
- 支持 QAM-256 调制
- 4x4 MIMO 支持

#### 2.3.2 MAC 层
- 所有 MAC 过程实现
- 调度和资源分配
- HARQ 处理
- 动态资源管理

#### 2.3.3 RLC 层
- AM/UM/TM 模式支持
- 分段和重组
- ARQ 机制

#### 2.3.4 PDCP 层
- 完整 PDCP 功能
- 安全性处理（加密和完整性保护）
- 重排序和重复检测

#### 2.3.5 RRC 层
- 所有 RRC 过程实现
- 连接管理
- 移动性管理
- 系统信息广播

---

## 3. 主要功能特性

### 3.1 核心功能
1. **完整的 5G NR 协议栈**：L1/L2/L3 全栈实现
2. **O-RAN 合规**：支持 Split 7.2x 功能分割
3. **CU/DU 分离**：灵活的部署架构
4. **多频段支持**：所有 FR1 频段
5. **带宽灵活性**：100 MHz TDD，50 MHz FDD
6. **MIMO 支持**：4x4 MIMO
7. **高级调制**：QAM-256 支持
8. **网络切片**：5G 网络切片支持
9. **NTN 支持**：非地面网络 GEO 支持

### 3.2 技术亮点
1. **高性能编码**：优化的 LDPC 和 Polar 编码器
2. **跨平台移植**：支持 x86、ARM 等多种架构
3. **最小依赖**：最少的外部依赖
4. **模块化设计**：组件可独立部署和替换
5. **云原生支持**：Kubernetes 容器化部署

### 3.3 开发者友好特性
1. **完善的文档**：详细的安装和使用指南
2. **丰富的教程**：多种部署场景教程
3. **活跃社区**：GitHub Discussions 社区支持
4. **商业支持**：SRS 提供企业级支持

---

## 4. 应用场景

### 4.1 5G 基站开发
#### 4.1.1 私有 5G 网络
- 工业物联网部署
- 校园网络
- 港口和矿山专用网络
- 企业专网

#### 4.1.2 研究和测试
- 5G 技术研究平台
- 协议栈开发和测试
- 性能基准测试
- 新功能验证

#### 4.1.3 教育培训
- 5G 技术教学
- 无线通信实验
- 实验室环境搭建

### 4.2 O-RAN 集成
#### 4.2.1 多厂商互操作
- 与第三方 RIC 集成
- 与不同厂商 RU 对接
- 异构网络部署

#### 4.2.2 O-RAN 测试平台
- O-RAN 合规性测试
- E2 接口验证
- xApp 开发和测试

#### 4.2.3 网络功能虚拟化
- VNF/CNF 部署
- 边缘计算集成
- 云原生 RAN

### 4.3 AI-RAN 优化
#### 4.3.1 智能无线资源管理
- AI 驱动的调度优化
- 频谱效率提升
- 干扰管理

#### 4.3.2 网络自动化
- 自动化配置和优化
- 故障预测和诊断
- 能耗优化

#### 4.3.3 机器学习集成
- 模型训练和推理
- 实时决策支持
- 预测性维护

---

## 5. 开发环境搭建

### 5.1 系统要求
- **操作系统**：Linux（推荐 Ubuntu 22.04 或更高版本）
- **处理器**：x86_64 或 ARM64
- **内存**：建议 8GB+ RAM
- **存储**：至少 20GB 可用空间

### 5.2 依赖安装

#### 5.2.1 Ubuntu/Debian
```bash
# 基本构建工具
sudo apt-get update
sudo apt-get install cmake make gcc g++ pkg-config

# 必需依赖
sudo apt-get install libfftw3-dev libmbedtls-dev libsctp-dev libyaml-cpp-dev libgtest-dev

# 可选依赖（推荐）
sudo apt-get install ccache libzmq3-dev
```

#### 5.2.2 Fedora
```bash
sudo yum install cmake make gcc gcc-c++ fftw-devel lksctp-tools-devel yaml-cpp-devel mbedtls-devel gtest-devel
```

#### 5.2.3 Arch Linux
```bash
sudo pacman -S cmake make base-devel fftw mbedtls yaml-cpp lksctp-tools gtest
```

### 5.3 RF 驱动安装
```bash
# UHD 驱动（用于 Split 8 部署）
sudo apt-get install libuhd-dev uhd-host

# ZMQ 驱动（用于虚拟测试）
sudo apt-get install libzmq3-dev
```

### 5.4 代码克隆和构建
```bash
# 克隆仓库
git clone https://gitlab.com/ocudu/ocudu.git
cd ocudu

# 创建构建目录
mkdir build
cd build

# 配置和构建
cmake ../
make -j $(nproc)

# 运行测试
make test -j $(nproc)

# 安装（可选）
sudo make install
```

### 5.5 特定配置构建
```bash
# 仅 Split 7.2
cmake -DDU_SPLIT_TYPE=SPLIT_7_2 ../

# 仅 Split 8
cmake -DDU_SPLIT_TYPE=SPLIT_8 ../

# 启用 ZMQ
cmake -DENABLE_EXPORT=ON -DENABLE_ZEROMQ=ON ../
```

### 5.6 包管理器安装
```bash
# Ubuntu PPA
sudo add-apt-repository ppa:softwareradiosystems/srsran-project
sudo apt-get update
sudo apt-get install srsran-project

# Arch Linux AUR
yay -Sy srsran-project-git
```

---

## 6. 代码结构分析

### 6.1 顶层目录结构
```
srsRAN_Project/
├── apps/                    # 应用程序
│   ├── gnb/                # gNB 应用
│   ├── ue/                 # UE 应用
│   └── epc/                # EPC 应用
├── lib/                     # 核心库
│   ├── common/             # 公共库
│   ├── phy/                # 物理层
│   ├── mac/                # MAC 层
│   ├── rlc/                # RLC 层
│   ├── pdcp/               # PDCP 层
│   ├── rrc/                # RRC 层
│   ├── ngap/               # NGAP 协议
│   ├── f1ap/               # F1AP 协议
│   ├── e1ap/               # E1AP 协议
│   ├── e2/                 # E2 接口
│   └── ofh/                # Open Fronthaul
├── tests/                   # 测试套件
├── docs/                    # 文档
├── cmake/                   # CMake 配置
└── external/                # 外部依赖
```

### 6.2 核心模块分析

#### 6.2.1 物理层模块
- **lib/phy/**：物理层实现
  - 信道编码（LDPC、Polar）
  - 调制解调
  - MIMO 处理
  - 同步和信道估计

#### 6.2.2 协议栈模块
- **lib/mac/**：MAC 层实现
- **lib/rlc/**：RLC 层实现
- **lib/pdcp/**：PDCP 层实现
- **lib/rrc/**：RRC 层实现

#### 6.2.3 接口模块
- **lib/ngap/**：NGAP 协议实现
- **lib/f1ap/**：F1AP 协议实现
- **lib/e1ap/**：E1AP 协议实现
- **lib/e2/**：E2 接口实现

#### 6.2.4 前传模块
- **lib/ofh/**：Open Fronthaul 库
  - 支持 Split 7.2x
  - eCPRI 协议实现
  - 用户面和控制面处理

### 6.3 应用程序结构
```cpp
// gNB 应用入口
apps/gnb/
├── gnb_appmain.cpp         # 主程序入口
├── gnb_appconfig.h         # 配置解析
├── gnb_worker_threads.h    # 工作线程
└── gnb_app.h               # 应用逻辑
```

### 6.4 关键设计模式
1. **模块化设计**：各层独立实现，接口清晰
2. **生产者-消费者模式**：数据流处理
3. **线程池模式**：高性能并发处理
4. **策略模式**：可配置的算法实现

---

## 7. 性能基准测试

### 7.1 吞吐量性能
#### 7.1.1 实验室环境测试
基于学术研究论文数据：

| 配置 | 带宽 | srsRAN 吞吐量 | OAI 吞吐量 |
|------|------|---------------|------------|
| Config 1 | 40 MHz | ~60 Mbps | ~124 Mbps |
| Config 2 | 20 MHz | ~17 Mbps | ~52 Mbps |

**注**：性能差异主要由于 OAI 支持 256-QAM，而 srsRAN 仅支持 64-QAM。

#### 7.1.2 理论峰值
- **100 MHz TDD**：理论上行/下行峰值可达数 Gbps
- **50 MHz FDD**：适合广域覆盖场景
- **4x4 MIMO**：显著提升频谱效率

### 7.2 延迟性能
- **单向延迟**：可优化至毫秒级
- **往返延迟**：典型值 10-20ms
- **抖动控制**：相对稳定，偶发尖峰

### 7.3 资源占用
- **CPU 使用率**：依赖配置和负载
- **内存占用**：典型 2-4GB
- **存储需求**：基本安装约 1GB

### 7.4 扩展性测试
- **多 UE 支持**：可支持数十个并发 UE
- **多小区**：支持多小区部署
- **云原生扩展**：Kubernetes 水平扩展

---

## 8. 与竞品对比

### 8.1 srsRAN vs OpenAirInterface (OAI)

| 特性 | srsRAN/OCUDU | OpenAirInterface |
|------|--------------|------------------|
| **易用性** | ⭐⭐⭐⭐⭐ 优秀 | ⭐⭐⭐ 中等 |
| **文档质量** | ⭐⭐⭐⭐⭐ 优秀 | ⭐⭐⭐ 中等 |
| **功能完整性** | ⭐⭐⭐⭐ 良好 | ⭐⭐⭐⭐⭐ 优秀 |
| **社区活跃度** | ⭐⭐⭐⭐ 良好 | ⭐⭐⭐⭐⭐ 优秀 |
| **性能** | ⭐⭐⭐⭐ 良好 | ⭐⭐⭐⭐⭐ 优秀 |
| **学习曲线** | 平缓 | 陡峭 |
| **许可证** | Apache 2.0 | OAI License |
| **治理** | Linux Foundation | Eurecom |

### 8.2 srsRAN vs 商业解决方案

| 特性 | srsRAN/OCUDU | 商业解决方案 |
|------|--------------|--------------|
| **成本** | 免费开源 | 高昂许可费 |
| **定制性** | 完全可定制 | 有限定制 |
| **支持** | 社区支持 | 专业支持 |
| **合规性** | O-RAN 合规 | 厂商锁定 |
| **创新速度** | 快速迭代 | 稳定更新 |

### 8.3 选择建议
1. **初学者/研究**：推荐 srsRAN，学习曲线平缓
2. **生产部署**：考虑商业支持版本
3. **O-RAN 集成**：两者都支持，srsRAN 更易集成
4. **高性能需求**：OAI 可能更优
5. **快速原型**：srsRAN 更快上手

---

## 9. 创业机会分析

### 9.1 市场机会
#### 9.1.1 私有 5G 网络市场
- **市场规模**：预计 2027 年达到 100 亿美元
- **增长驱动力**：工业 4.0、物联网、边缘计算
- **客户群体**：制造、能源、交通、医疗

#### 9.1.2 O-RAN 生态系统
- **设备厂商**：小基站、RRU、天线
- **软件厂商**：RIC、xApp、rApp
- **系统集成商**：端到端解决方案

### 9.2 商业模式
#### 9.2.1 技术服务
- **定制开发**：基于 OCUDU 的定制化开发
- **集成服务**：多厂商设备集成
- **培训咨询**：5G/O-RAN 技术培训

#### 9.2.2 产品化
- **企业级解决方案**：私有 5G 网络套件
- **边缘计算平台**：MEC 解决方案
- **AI-RAN 产品**：智能网络优化

#### 9.2.3 SaaS 服务
- **网络即服务**：托管 5G 网络
- **平台即服务**：开发测试平台
- **数据服务**：网络数据分析

### 9.3 竞争优势
1. **开源优势**：无许可费用，快速创新
2. **技术壁垒**：深度技术积累
3. **生态系统**：Linux Foundation 支持
4. **市场需求**：5G 专网需求爆发

### 9.4 风险与挑战
1. **技术风险**：5G 技术复杂性
2. **市场风险**：竞争激烈
3. **人才风险**：专业人才稀缺
4. **合规风险**：频谱和认证

---

## 10. 求职相关技能要求

### 10.1 核心技术技能
#### 10.1.1 编程语言
- **C/C++**：精通，C++17 标准
- **Python**：脚本和自动化
- **Go/Kubernetes**：云原生开发
- **汇编**：性能优化（ARM/x86）

#### 10.1.2 5G 技术
- 3GPP 规范（Release 15-17）
- O-RAN 架构和接口
- 无线协议栈（PHY/MAC/RLC/PDCP/RRC）
- 信令协议（NGAP/F1AP/E1AP/E2AP）

#### 10.1.3 软件工程
- Linux 系统编程
- 多线程和并发
- 性能优化
- 测试和调试

### 10.2 岗位类型
#### 10.2.1 5G RAN 开发工程师
- **职责**：协议栈开发、性能优化
- **技能**：C++、5G PHY/MAC、DSP
- **薪资**：$120,000 - $200,000

#### 10.2.2 O-RAN 集成工程师
- **职责**：多厂商集成、接口开发
- **技能**：O-RAN 接口、系统集成
- **薪资**：$100,000 - $180,000

#### 10.2.3 无线通信工程师
- **职责**：网络规划、优化
- **技能**：无线通信理论、网络优化
- **薪资**：$90,000 - $150,000

#### 10.2.4 云原生 RAN 工程师
- **职责**：容器化部署、微服务架构
- **技能**：Kubernetes、Docker、CI/CD
- **薪资**：$130,000 - $200,000

### 10.3 职业发展路径
```
初级工程师 → 中级工程师 → 高级工程师 → 技术专家/架构师 → 技术总监
```

### 10.4 认证和培训
- **O-RAN Alliance 认证**
- **3GPP 标准培训**
- **Kubernetes 认证 (CKA/CKAD)**
- **SRS 官方培训课程**

---

## 11. 学习资源与社区

### 11.1 官方资源
#### 11.1.1 文档
- **srsRAN Project 文档**：https://docs.srsran.com/projects/project
- **OCUDU 文档**：https://ocudu.org/documentation
- **O-RAN 规范**：https://www.o-ran.org/specifications

#### 11.1.2 代码仓库
- **原 srsRAN**：https://github.com/srsran/srsran_project
- **新 OCUDU**：https://gitlab.com/ocudu/ocudu
- **示例配置**：/usr/share/srsran（安装后）

### 11.2 学习教程
#### 11.2.1 入门教程
- [安装指南](https://docs.srsran.com/projects/project/en/latest/user_manuals/source/installation.html)
- [运行指南](https://docs.srsran.com/projects/project/en/latest/user_manuals/source/running.html)
- [配置参考](https://docs.srsran.com/projects/project/en/latest/user_manuals/source/config_ref.html)

#### 11.2.2 高级教程
- [CU-DU 分离教程](https://docs.srsran.com/projects/project/en/latest/tutorials/source/cu_du_split/source/index.html)
- [O-RAN 7.2 RU 指南](https://docs.srsran.com/projects/project/en/latest/tutorials/source/oranRU/source/index.html)
- [NearRT-RIC 和 xApp](https://docs.srsran.com/projects/project/en/latest/tutorials/source/near-rt-ric/source/index.html)
- [Kubernetes 部署](https://docs.srsran.com/projects/project/en/latest/tutorials/source/k8s/source/index.html)

#### 11.2.3 视频教程
- [srsRAN 官方 YouTube](https://www.youtube.com/@SRSio14)
- [2025 srsRAN Fall Workshop](https://www.youtube.com/watch?v=hZxDqJqve0o)
- [OCUDU & Linux Foundation](https://www.youtube.com/watch?v=DXjXn_NULp0)

### 11.3 社区资源
#### 11.3.1 社区论坛
- **GitHub Discussions**：https://github.com/srsran/srsRAN_Project/discussions
- **OCUDU 社区**：https://ocudu.org/community

#### 11.3.2 学术资源
- [arXiv 论文](https://arxiv.org/search/?query=srsRAN&searchtype=all)
- [IEEE 论文](https://ieeexplore.ieee.org/search/searchresult.jsp?queryText=srsRAN)
- [O-RAN SC 文档](https://docs.o-ran-sc.org/)

#### 11.3.3 开发者资源
- [代码风格指南](https://docs.srsran.com/projects/project/en/latest/dev_guide/source/code_guide/source/index.html)
- [测试策略](https://docs.srsran.com/projects/project/en/latest/dev_guide/source/testing_policy/source/index.html)
- [贡献指南](https://docs.srsran.com/projects/project/en/latest/general/source/3_contributions.html)

### 11.4 培训课程
- **SRS 官方培训**：https://srs.io/training/
- **O-RAN Alliance 培训**：https://www.o-ran.org/education
- **Coursera/edX 5G 课程**

---

## 12. 未来发展方向

### 12.1 技术演进
#### 12.1.1 近期路线图
- **CU-CP/CU-UP 分离**：更细粒度的功能分割
- **FR2 支持**：毫米波频段支持
- **120 kHz 子载波间隔**：更高带宽支持
- **更高阶 MIMO**：Massive MIMO 支持

#### 12.1.2 中期目标
- **6G 预研**：AI 原生 RAN 架构
- **网络智能化**：深度学习集成
- **边缘计算增强**：MEC 深度集成
- **安全增强**：零信任架构

#### 12.1.3 长期愿景
- **AI-Native RAN**：完全智能化的无线接入网
- **自组织网络**：自动化运维
- **绿色通信**：能效优化
- **天地一体化**：NTN 深度集成

### 12.2 生态系统发展
#### 12.2.1 OCUDU Ecosystem Foundation
- **治理结构**：Linux Foundation 中立治理
- **成员扩展**：21+ 全球组织
- **CI/CD/CT 资产**：持续集成/测试基础设施

#### 12.2.2 血统生态系统
- **srsRAN**：技术基础
- **Eurecom**：研究合作
- **行业伙伴**：设备厂商、运营商

#### 12.2.3 标准化进程
- **O-RAN Alliance**：接口标准化
- **3GPP**：协议标准化
- **ETSI**：欧洲标准

### 12.3 市场趋势
#### 12.3.1 5G 专网爆发
- **工业 4.0**：智能制造需求
- **物联网**：海量连接需求
- **边缘计算**：低延迟应用

#### 12.3.2 O-RAN 采用加速
- **运营商转型**：网络虚拟化
- **多厂商策略**：避免供应商锁定
- **创新加速**：开放生态

#### 12.3.3 AI-RAN 融合
- **AI 驱动优化**：网络性能提升
- **自动化运维**：降低运营成本
- **智能服务**：差异化竞争力

### 12.4 挑战与机遇
#### 12.4.1 技术挑战
- **性能优化**：与专用硬件竞争
- **互操作性**：多厂商集成复杂性
- **安全性**：开放架构的安全风险

#### 12.4.2 市场机遇
- **新兴市场**：发展中国家 5G 部署
- **垂直行业**：行业数字化转型
- **创新应用**：AR/VR、自动驾驶

---

## 附录

### A. 术语表
| 术语 | 全称 | 说明 |
|------|------|------|
| OCUDU | Open Centralized Unit/Distributed Unit | 开放式集中/分布式单元 |
| CU | Centralized Unit | 集中单元 |
| DU | Distributed Unit | 分布式单元 |
| RU | Radio Unit | 无线单元 |
| RIC | RAN Intelligent Controller | RAN 智能控制器 |
| xApp | eXecution Application | 执行应用程序 |
| rApp | rApp Application | rApp 应用程序 |
| O-RAN | Open RAN | 开放式无线接入网 |
| 5G NR | 5G New Radio | 5G 新空口 |

### B. 参考资料
1. srsRAN Project 官方文档
2. O-RAN Alliance 规范
3. 3GPP Release 17 规范
4. 学术论文：Experimental comparison of 5G SDR platforms
5. Linux Foundation OCUDU 文档

### C. 相关链接
- srsRAN 官网：https://srs.io
- OCUDU 官网：https://ocudu.org
- O-RAN Alliance：https://www.o-ran.org
- Linux Foundation：https://www.linuxfoundation.org

---

## 文档信息
- **创建日期**：2026 年 8 月
- **最后更新**：2026 年 8 月 25 日
- **版本**：1.0
- **作者**：基于公开资料整理
- **许可证**：知识共享许可协议

---

*本文档基于 srsRAN Project 官方资料、学术论文和行业报告综合整理，旨在提供全面的项目研究分析。如有更新或补充，欢迎社区贡献。*