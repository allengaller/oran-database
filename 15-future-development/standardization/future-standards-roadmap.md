# O-RAN 标准化演进路线图

## 概述

本文档梳理 O-RAN 相关标准体系的未来演进路径，涵盖 O-RAN Alliance、3GPP、ETSI 等核心标准组织的工作计划与里程碑，分析标准演进对产品开发与商业部署的影响，并给出行业协作框架建议。

## 1. O-RAN Alliance 规范演进

### 1.1 规范版本与发布节奏

O-RAN Alliance 采用双年大版本 + 持续补充规范（CSG - Continuous Stream of Guidelines）模式：

- **Release 1（2020）**：基本架构、E2/A1/O1/O2 接口规范初稿
- **Release 2（2022）**：Near-RT RIC、Non-RT RIC 完善，O-Cloud 体系成型
- **Release 3（2024）**：WG3 E2SM 服务模型扩展（NI、MAC/RLC/PDCP）、WG11 安全增强
- **Release 4（2025-2026，进行中）**：AI/ML 管理编排（WG6）、RIC 应用安全保障（WG11）、5G-Advanced 接口增强
- **Release 5（2027 预计）**：6G 预研方向、语义通信接口、太赫兹前传规范预研

### 1.2 各工作组近期重点

| 工作组 | 关键规范 | Release 4 进展 | Release 5 预研方向 |
|-------|---------|---------------|------------------|
| WG1（用例与需求） | O-RAN Use Cases & Requirements | AI-RAN Use Case v2（Agentic AI）、网络能效用例 | 6G AI-Native Use Cases |
| WG2（非实时 RIC） | Non-RT RIC 架构、rApp 接口、A1 接口 | A1-Policy 新增 AI 模型管理策略类型、跨域协同策略 | 意图驱动接口（Intent-based A1）|
| WG3（Near-RT RIC 与 E2） | E2AP、E2SM（KPM/RC/NI/MAC 等） | E2AP v4：新增 E2 Control、Insert 新过程；E2SM-MRO 新服务模型 | E2SM 语义通信服务模型（SCSM）预研 |
| WG4（前传） | O-FH 控制/用户/同步平面、O-FH CUS-plane | O-FH CUS-plane M-plane 增强、下行 7.2x 方案增强、上行协作多点传输 | 太赫兹 O-FH 7.3/7.5 高层分割方案研究 |
| WG5（开放前传硬件） | O-RU 能力与接口规范 | O-RU M-plane 增强、多 RU 协作、天线阵列建模增强 | O-RU 新频段（> 6 GHz、> 52.6 GHz）适配 |
| WG6（O-Cloud） | O-Cloud 体系架构、AI/ML 编排 | AI/ML 生命周期管理规范初稿、GPU 资源暴露接口、O-Cloud 孪生接口 | 6G-Native AI Cloud 基础设施规范 |
| WG7（白盒硬件） | 白盒硬件规范、参考设计 | 通用服务器硬件规范更新、加速器卡（DPU/FPGA）接口 | 开放 RAN 处理器架构增强 |
| WG8（协议栈） | L1/L2/L3 协议栈功能规范 | NR L1/L2 高层协议栈规范更新、E1 接口增强 | 6G 空口协议栈预研 |
| WG9（O-RAN 大规模 MIMO） | 大规模 MIMO 前传性能需求与测试方法 | 多频段 MIMO 前传、码本增强、TDD 帧结构优化 | Sub-THz MIMO 前传预研 |
| WG10（OAM） | O1 接口、O-RAN OAM 体系 | O1 数据模型增强、故障管理自治、性能监控细粒度增强 | 语义级 OAM（Intent-based OAM）|
| WG11（安全） | O-RAN 安全威胁模型、接口安全规范 | AI/ML 安全框架规范、后量子密码迁移指南、零信任 O-RAN 体系 | 安全 AI（AI4Security）规范、AI 训练数据保护 |

### 1.3 O-RAN 技术规范 (TS) 与技术报告 (TR) 数量增长

- 2021：TS 12 篇，TR 5 篇
- 2023：TS 35 篇，TR 18 篇
- 2025（截至 2025 Q4）：TS 60+ 篇，TR 30+ 篇
- 趋势：安全规范与 AI/ML 相关规范增长最快，2024-2025 增长均超 50%

## 2. 3GPP 与 O-RAN 的协同演进

### 2.1 3GPP Release 演进时间线

| Release | 时间 | O-RAN 相关重点 |
|---------|------|--------------|
| R18（5G-Advanced Phase 1） | 冻结 2024 Q1 | NR 增强、网络能效、XR 增强、AI/ML for NG-RAN 用例研究 |
| R19（5G-Advanced Phase 2） | 冻结 2025 Q3 | AI/ML 模型生命周期管理、网络能效增强、通感一体（ISAC）立项、NR C-IoT 增强 |
| R20（6G 预研） | 立项 2025，预计冻结 2028 | AI-Native 空口、语义通信框架、太赫兹信道模型、沉浸式通信 |
| R21（6G Phase 1） | 预计冻结 2030 | 6G 系统框架、AI 原生协议栈、语义传输标准化 |

### 2.2 3GPP-O-RAN 规范映射与衔接

3GPP 定义 RAN 功能规格，O-RAN 定义解聚后的接口与管理规范。关键衔接点：

- **3GPP NR L1/L2 协议** → O-RAN WG8（协议栈功能拆分实现规范）
- **3GPP NG-RAN 架构（38.401）** → O-RAN 架构对齐（分层与接口映射）
- **3GPP FCAPS（OAM）** → O-RAN WG10/O1 数据模型
- **3GPP AI/ML for NG-RAN** → O-RAN WG6 AI/ML 编排规范、WG2 A1 AI 策略
- **3GPP RAN 增强（SON、MDT）** → O-RAN RIC/RAN 的智能控制实现

### 2.3 Release 19 关键议题的 O-RAN 影响

- **AI/ML 模型生命周期管理（TR 38.843）**：定义模型注册、激活、监控、回退流程 → 直接影响 O-RAN A1 接口的 AI 模型策略设计
- **通感一体（ISAC）**：3GPP 信令模型定义 → 影响 O-RAN E2SM 新服务模型设计
- **网络能效增强**：终端辅助休眠、基站能效 KPI → 影响 O-RAN 节能 xApp/rApp 设计
- **NTN 非地面网络增强**：卫星与地面 RAN 融合 → O-RAN 需支持 NTN CU/DU 架构适配

## 3. ETSI O-RAN 相关标准

### 3.1 ETSI NFV 与 O-Cloud

- **ETSI NFV-MANO（Management and Orchestration）**：O-Cloud 的虚拟化基础设施管理可基于 NFV-MANO 架构
- **ETSI NFV TOSCA 数据模型**：O-RAN O2 接口的资源描述格式对齐 NFV TOSCA YAML 规范
- **进展**：O-RAN O2 接口与 ETSI NFV SOL001/SOL005 的映射工作持续推进

### 3.2 ETSI MEC（Multi-access Edge Computing）

- ETSI MEC 平台与 O-RAN 的结合：MEC 应用可作为 xApp 的非 RAN 服务类型被管理
- ETSI GS MEC 011/012 与 O-RAN A1 接口的协同设计方向
- 低延迟 RAN 功能下沉与 MEC 本地卸载的架构协同

### 3.3 ETSI O-RAN 相关技术规范

- **ETSI TS 103 859**：O-RAN 架构与总体描述
- **ETSI TS 103 983/986/987**：O-RAN 接口测试规范
- **ETSI GS ORAN-005**：O-RAN 安全指南

## 4. 认证体系演进

### 4.1 O-RAN 认证体系

- **O-RAN 认证（O-RAN Conformance Certification）**：O-RAN Alliance 授权测试实验室进行规范符合性认证
- **测试内容**：接口一致性（E2/A1/O1/O2）、安全性、性能基线
- **认证实验室**：目前 10+ 家授权实验室（欧洲、北美、亚太均有覆盖）

### 4.2 TIP（Telecom Infra Project）认证

- **TIP Open RAN 认证**：TIP 推出针对商用产品的认证计划
- **测试内容**：互操作性测试（IoT）、性能基准测试（Benchmarking）
- **更新趋势**：TIP 认证逐步扩展至 AI-RAN 应用（rApp/xApp 认证预研中）

### 4.3 GCF（Global Certification Forum）

- GCF 是移动终端与网络设备认证的主要国际平台
- O-RAN 设备 GCF 认证发展动向：GCF 已启动 O-RAN 设备认证工作组
- 目标：实现 O-RAN 设备认证结果的国际互认

### 4.4 认证演进趋势

- 从基础符合性到性能认证：O-RAN 认证从"能否工作"向"工作得怎样"延伸
- 安全认证权重提升：WG11 安全规范纳入认证门槛
- AI-RAN 认证新维度：AI 模型的公平性、可解释性认证探索中

## 5. 行业联盟与协作机制

### 5.1 AI-RAN Alliance（2024 成立）

- **成员**：NVIDIA、SoftBank、T-Mobile、爱立信、三星等 50+ 家企业
- **目标**：加速 AI 与 RAN 的深度融合，推动 AI-RAN 产业生态成熟
- **标准角色**：AI-RAN Alliance 不直接制定规范，而是向 O-RAN Alliance 和 3GPP 输送用例与需求提案

### 5.2 TIP Open RAN 项目

- **重点**：多厂商互操作性测试、商用验证（CIP - Commercial Infrastructure Project）
- **与 O-RAN 的关系**：TIP 是 O-RAN 规范的落地验证平台，测试反馈驱动规范修订

### 5.3 O-RAN Software Community (OSC)

- **定位**：O-RAN 规范的开源参考实现
- **代码库**：github.com/o-ran-sc
- **协作机制**：O-RAN Alliance 定义规范 → OSC 实现参考代码 → 厂商基于参考代码开发商业产品

### 5.4 3GPP SA5 与 O-RAN 联合工作组

- 3GPP SA5（系统管理）与 O-RAN WG10 的 OAM 规范协同工作组
- 目标：减少 3GPP OAM 与 O-RAN O1 接口规范的重复与冲突

## 6. 标准演进对产业的影响

### 6.1 对产品开发

- **Release 4 产品化窗口**（2026-2027）：AI/ML 编排规范生效后，厂商需同步升级 SMO、RIC 平台
- **E2AP v4 迁移**：新增 Control/Insert 过程，Near-RT RIC 与 xApp 需适配新版本
- **安全合规成本上升**：WG11 安全规范成为合规门槛，安全测试投入增加

### 6.2 对运营商采购

- 采购规范引用 O-RAN TS/TR 版本号作为技术要求基准
- 多厂商集成的测试用例将参考 O-RAN 认证测试规范
- 6G 网络建设规划需关注 Release 5 的规范方向

### 6.3 对研究者

- 标准化空白领域是学术研究的高价值课题（RIS、语义通信接口、ISAC E2SM 等）
- 参与 O-RAN Alliance 开放研究提案（Open Call）是学术成果向标准化转化的有效路径

## 7. 与其他章节的关联

- 现有规范体系详解：[09-standards-compliance](../../09-standards-compliance/readme.md)
- 工作组职能与组成：[06-working-groups](../../06-working-groups/readme.md)
- 接口标准细节：[03-interface-standards](../../03-interface-standards/readme.md)
- 研究前沿方向：[research-frontiers](../research-frontiers/research-directions.md)
- AI-RAN 落地进展：[31-ai-ran-convergence](../../31-ai-ran-convergence/readme.md)
