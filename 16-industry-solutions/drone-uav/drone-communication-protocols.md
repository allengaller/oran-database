---
title: "无人机通信协议与接口详解"
description: "详解无人机通信协议栈：5G NR 空中接口、O-RAN 接口在无人机场景的应用、C2 控制链路、视频回传、遥测与监管协议、PC5 Sidelink 编队协议。"
category: "documentation"
language: "zh-CN"
version: "1.0"
last_updated: "2026-08-25"
keywords: ['无人机', '通信协议', 'C2', '5G', 'O-RAN', 'Sidelink', 'UAV']
---

# 无人机通信协议与接口详解

> **定位**：梳理无人机通信涉及的全部协议栈，为开发者提供协议选型与集成参考

---

## 目录

1. [协议栈总览](#1-协议栈总览)
2. [5G NR 空中接口（Uu）](#2-5g-nr-空中接口uu)
3. [O-RAN 接口在无人机中的应用](#3-o-ran-接口在无人机中的应用)
4. [C2 控制链路协议](#4-c2-控制链路协议)
5. [视频回传协议](#5-视频回传协议)
6. [遥测与监管协议](#6-遥测与监管协议)
7. [PC5 Sidelink 编队协议](#7-pc5-sidelink-编队协议)
8. [多链路融合与冗余](#8-多链路融合与冗余)
9. [协议栈实现参考](#9-协议栈实现参考)
10. [标准化进展](#10-标准化进展)

---

## 1. 协议栈总览

```
┌─────────────────────────────────────────────────────────┐
│ 应用层                                                   │
│  MAVLink │ DJI Cloud API │ RTMP/GB28181 │ MQTT          │
├─────────────────────────────────────────────────────────┤
│ 传输层                                                   │
│  QUIC │ UDP(C2) │ TCP │ RTP/RTCP                        │
├─────────────────────────────────────────────────────────┤
│ 网络层                                                   │
│  5G PDU Session │ IPv6 │ SD-WAN 多链路                   │
├─────────────────────────────────────────────────────────┤
│ 接入层                                                   │
│  5G NR Uu │ PC5 Sidelink │ 私有图传(2.4/5.8G) │ 卫星     │
├─────────────────────────────────────────────────────────┤
│ RAN 内部接口                                             │
│  O-FH(O-RU↔O-DU) │ F1(O-DU↔O-CU) │ E2(→RIC) │ A1/O1    │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 5G NR 空中接口（Uu）

### 2.1 空中 UE 的 NR 协议要点

| 协议层 | 无人机适配要点 |
|:---|:---|
| **物理层（L1）** | 视距信道下高阶调制（256QAM）；大频偏补偿（高速机动） |
| **MAC（L2）** | CG（Configured Grant）预配置授权保障 C2 低时延 |
| **RLC/PDCP** | C2 使用 UM 模式降低时延；视频使用 AM 保证完整性 |
| **RRC** | 空中 UE 专用测量配置（上报更多邻区，应对高空可见小区多） |
| **NAS** | UAV 鉴权（UAS NF 交互，3GPP TS 24.556） |

### 2.2 UAS 专用信令（3GPP Rel-16+）

- **UAV 鉴权与授权**：UE 携带 UAV 标识，AMF 与 UAS NF（UAV 服务网络功能）交互完成飞行授权
- **UAS 流量管理**：网络向 UTM 报告 UAV 位置（TS 23.256）
- **远程 ID 广播**：支持监管方获取无人机身份（对标 FAA Remote ID / 中国 UOM）

### 2.3 QoS 与切片映射

| 业务流 | 5QI | 切片（S-NSSAI） | 关键参数 |
|:---|:---|:---|:---|
| C2 控制 | 85（URLLC） | UAV-C2 | 10ms / 99.999% |
| 视频回传 | 2（会话视频） | UAV-VIDEO | 20-100Mbps / 100ms |
| 遥测上报 | 79 | UAV-TELEMETRY | KB 级周期 |
| 编队指令（组播） | MBS QoS | UAV-SWARM | <20ms |

---

## 3. O-RAN 接口在无人机中的应用

| 接口 | 常规用途 | 无人机场景用途 |
|:---|:---|:---|
| **E2** | RIC↔CU/DU 控制 | 空中 UE 测量上报→切换/波束 xApp 决策 |
| **A1** | Non-RT↔Near-RT RIC | 航路策略、切片 SLA 策略下发 |
| **O1** | SMO 管理 | 低空小区配置、FCAPS |
| **O2** | 云编排 | 边缘 AI 算力编排（与基带共池） |
| **O-FH** | O-RU↔O-DU | 应急场景无人机挂载 O-RU 经卫星回传接 O-DU |
| **F1** | O-DU↔O-CU | 分离部署时的低时延承载 |

### E2 服务模型（SM）扩展建议

现有 E2SM 未针对空中 UE 优化，创业机会：**定义 UAV 专用 E2SM**：

```protobuf
// UAV-E2SM 扩展字段示例
message UAVMeasurement {
  string ue_id = 1;
  float altitude_m = 2;          // 高度
  float velocity_3d = 3;         // 三维速度
  repeated CellRSRP visible_cells = 4;  // 可见小区列表（空中UE特有）
  TrajectoryPoint predicted_path = 5;   // 预测轨迹
}
```

---

## 4. C2 控制链路协议

### 4.1 MAVLink（开源生态通用）

- **定位**：轻量级机器人/无人机遥测与控制协议，ArduPilot/PX4 生态标准
- **版本**：MAVLink 2，消息头 14 字节，支持 25 条消息/类型
- **传输**：常跑在 UDP/串口之上；5G 场景封装于 UDP over PDU Session
- **关键消息**：HEARTBEAT（心跳）、COMMAND_LONG（指令）、GLOBAL_POSITION_INT（位置）
- **安全**：MAVLink 2 支持签名（link signing）

### 4.2 厂商私有 C2（DJI OcuSync 等）

- 闭源协议，C2 + 视频复用私有链路
- 集成商通过 DJI Cloud API / MSDK 间接对接，不直接处理私有协议

### 4.3 C2 over 5G 的设计原则

1. **双链路冗余**：私有链路（低时延近距）+ 5G（远距兜底），链路质量 AI 预测自动切换
2. **指令优先级**：安全类指令（返航/悬停）抢占最高优先级 QoS 流
3. **端到端时延预算**：遥控器→网络→飞机 <100ms（人工操控可接受上限）

---

## 5. 视频回传协议

| 协议 | 时延 | 适用场景 |
|:---|:---|:---|
| **RTMP** | 1-3s | 云平台直播分发（DJI Cloud API 常用） |
| **GB28181** | 1-2s | 国内安防/政府平台对接标准 |
| **RTSP/RTP** | 200-500ms | 专网内低时延拉流 |
| **WebRTC** | 100-300ms | 实时操控类画面 |
| **SRT** | 可配 | 弱网抗丢包回传 |
| **私有图传** | <100ms | 近距 FPV 操控 |

### 5.1 AI 编码优化

- 机载端：H.265 + ROI 编码（感兴趣区域高质量）
- AI 语义编码探索：边缘端语义提取 + 重建，带宽省 40%（实验阶段）
- 智能码率：基于 5G 链路质量预测的 ABR（AI-driven Adaptive Bitrate）

---

## 6. 遥测与监管协议

### 6.1 遥测上行

- **MQTT**：机载→平台遥测上报主流协议（QoS 1，TLS 加密）
- **DJI Cloud API Things 通道**：基于 MQTT 的属性/事件上报

### 6.2 监管对接

| 体系 | 协议/接口 |
|:---|:---|
| 中国民航局 UOM | 无人驾驶航空器一体化综合监管服务平台接口 |
| 美国 FAA Remote ID | ASTM F3411（广播式远程识别） |
| 欧洲 EASA U-space | U1/U2 服务接口（网络式远程识别） |
| 3GPP UTM | TS 23.256 UAV 流量管理接口 |

**AI-RAN 角色**：通过遥测切片 + UAS NF 位置报告，为监管方提供网络级无人机感知。

---

## 7. PC5 Sidelink 编队协议

### 7.1 NR Sidelink 要点（3GPP Rel-16/17）

- 终端直通，无需基站中转，机间时延 <10ms
- 通信范围：视距数百米至数公里
- 资源分配模式：Mode 1（基站调度）/ Mode 2（自主感知选择）

### 7.2 编队应用

| 用途 | 消息类型 | 周期 |
|:---|:---|:---|
| 编队状态同步 | 位置/速度/姿态广播 | 10-50ms |
| 避障告警 | 紧急制动/绕行广播 | 事件触发 |
| 协同感知共享 | 传感器目标列表 | 100ms |
| 编队指令 | 组播控制（结合 MBS） | 事件触发 |

### 7.3 与 Uu 的协同

```
Uu（5G）：长距 C2、视频、任务级指令
PC5（Sidelink）：编队内实时同步、避障、失散保护
AI-RAN：RIC xApp 统一协调两种链路的资源与切换策略
```

---

## 8. 多链路融合与冗余

### 8.1 典型冗余组合

| 组合 | 适用场景 | 切换机制 |
|:---|:---|:---|
| 私有图传 + 5G | 行业作业主流 | 链路质量预测，无缝切换 |
| 5G + 卫星（NTN） | 偏远/应急 | 5G 失联自动切卫星 |
| 双运营商 5G | 高可靠要求 | 双 SIM 双活 |
| 5G + PC5 | 编队作业 | 编队内始终 PC5，任务级走 5G |

### 8.2 AI 链路决策

- 输入：RSRP/SINR 序列、飞行轨迹、历史链路中断模式
- 模型：时序分类（LSTM）预测未来 2s 链路可用性
- 输出：提前切换指令（避免闪断），下发至机载链路管理器

---

## 9. 协议栈实现参考

| 层次 | 开源实现 |
|:---|:---|
| 5G 核心网 | Open5GS、free5GC（含 UAS 演进中） |
| RAN | srsRAN Project（OCUDU）、OpenAirInterface |
| RIC | O-RAN SC RIC + xApp Framework |
| MAVLink | pymavlink / mavlink C 库 |
| 飞控生态 | PX4、ArduPilot（原生 MAVLink） |
| 视频 | GStreamer + SRT/WebRTC |
| 遥测 | EMQX（MQTT Broker） |

### 9.1 PoC 参考拓扑

```
PX4 无人机(SITL仿真) ──MAVLink/UDP──► QGroundControl
        │
        │ srsRAN UE 模拟
        ▼
srsRAN gNB ◄──O-FH──► [可选硬件O-RU]
        │ F1
        ▼
Open5GS 5GC ◄──► UTM 模拟服务
        │
        └──► O-RAN SC RIC（AerialHandoverXApp 验证）
```

---

## 10. 标准化进展

| 标准/版本 | 内容 | 状态 |
|:---|:---|:---|
| 3GPP Rel-15 | TR 36.777 LTE 空中 UE 研究 | 完成 |
| 3GPP Rel-16 | TS 22.125 / TS 23.256 UAS 支持 | 完成 |
| 3GPP Rel-17 | RedCap、NTN、UAV 增强 | 完成 |
| 3GPP Rel-18 (5G-A) | 通感一体（ISAC）研究、NTN 增强 | 进行中 |
| O-RAN WG3 | E2SM 扩展（UAV 专用待提案） | 机会点 |
| ASTM F3411 | Remote ID 广播标准 | 已发布 |
| 中国 CCSA | 5G 网联无人机系列行标 | 推进中 |

---

## 相关文档

- [无人机 AI-RAN 技术架构](./drone-ai-ran-architecture.md)
- [DJI 定制化 AI-RAN 解决方案](./dji-custom-ai-ran-solution.md)
- [无人机应用场景与案例](./drone-application-scenarios.md)
