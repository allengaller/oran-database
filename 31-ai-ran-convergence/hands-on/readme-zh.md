# 实战实验：AI-RAN 实现

> **更新：2026-05** | 可运行的代码、K8S manifest 和实验室设置

## 概述

本目录为 K8S 工程师提供**可立即运行的实战实验**，实现 2026 AI-RAN 收敛的关键组件。每个实验室都提供：

- **完整、可运行的代码**（非伪代码）
- **K8S manifest**（Deployment、CRD、ConfigMap）
- **验证脚本**（curl 命令、Prometheus 查询）
- **预期输出**（你应该看到什么）
- **故障排除指南**（常见问题及修复）

---

## 实验室目录

### 实验 1：[构建 Agentic AI 代理](./agentic-agent-code.md)
**难度**：⭐⭐⭐（中等）
**时间**：4-6 小时

**内容**：
- 完整的 `NetworkAgent` Python 类（带 LLM 推理）
- 3 层 `SafetyChecker`（边界检查、速率限制、孪生验证）
- 工具实现（DigitalTwinTool、A1PolicyPublisher、E2CommandExecutor）
- 带 MIG 分区的 K8S Deployment YAML
- 示例观察/响应 JSON

**你将学到**：
- Agentic AI 中的 ReAct（推理+行动）模式
- 如何为 AI 代理实现工具调用
- 自治网络中的安全模式
- 使用 vLLM 服务化电信调优 LLM

---

### 实验 2：[部署 NVIDIA ARC + K8S](./k8s-arc-deployment.md)
**难度**：⭐⭐⭐⭐（高）
**时间**：6-8 小时

**内容**：
- 实时内核设置（PREEMPT_RT 补丁）
- PTP 时间同步（IEEE 1588v2）
- CPU 隔离（`isolcpus`、`taskset`）
- 带 MIG 配置的 NVIDIA GPU Operator
- Multus CNI + SR-IOV 用于前传
- cuMAC 基带 Pod YAML
- Triton 边缘 AI Pod YAML
- DCGM Exporter 告警
- 功率封顶 DaemonSet

**你将学到**：
- 如何设置实时 K8S 节点
- MIG 在 GPU 工作负载间分区
- 5G NR 前传的 SR-IOV
- 边缘 AI-RAN 的 GPU 可观测性

---

### 实验 3：[部署电信 LLM](./telecom-llm-deployment.md)
**难度**：⭐⭐⭐（中等）
**时间**：3-4 小时

**内容**：
- vLLM + Qwen2.5-7B-Telecom 部署
- KServe InferenceService YAML
- FastAPI IntentTranslator 服务
- 带 3GPP 知识的 FastAPI RCA 分析器

**你将学到**：
- 如何服务化电信调优 LLM
- 意图转译模式（自然语言 → A1 策略）
- 基于 LLM 的自动根因分析
- KServe 用于模型管理和金丝雀部署

---

### 实验 4：[数字孪生同步](./digital-twin-sync.md)
**难度**：⭐⭐⭐⭐（高）
**时间**：5-7 小时

**内容**：
- Strimzi Kafka 用于遥测流
- E2 遥测生产者
- Flink 流作业（Java 草图）
- AODT 客户端集成
- TimescaleDB 超表 schema
- DriftDetector Python 类
- Prometheus 告警

**你将学到**：
- 如何从 E2 接口流式传输遥测数据
- Flink 用于实时数据处理
- AODT 集成模式
- 检测数字孪生与现实的漂移
- 基于 Prometheus 的告警

---

## 先决条件

### 硬件

| 组件 | 最小值 | 推荐 |
|:---|:---|:---|
| **CPU** | 8 核 | 16+ 核 |
| **内存** | 32 GB | 64+ GB |
| **GPU** | L4 (24GB) | L40S (48GB) |
| **存储** | 500 GB SSD | 1 TB NVMe |
| **网络** | 1 GbE | 10/25 GbE |

### 软件

- **Ubuntu 22.04 LTS**（或 24.04）
- **K8S 1.28+**（K3s 用于边缘、Kubeadm 用于中心）
- **NVIDIA 驱动** 535+
- **NVIDIA GPU Operator** v24.3+
- **Helm 3**
- **kubectl**

### 访问权限

- **NVIDIA Aerial SDK**（需 NDA，用于 cuMAC/cuPHY）
- **NVIDIA AODT**（可在 AWS 上访问，用于数字孪生）
- **Hugging Face**（用于电信 LLM 模型）

---

## 学习路径

### 新手路径（4 周）

**第 1 周**：实验 3（电信 LLM 部署）— 最简单的起点
**第 2 周**：实验 1（Agentic AI 代理）— 构建你的第一个代理
**第 3 周**：实验 4（数字孪生同步）— 添加预验证
**第 4 周**：实验 2（K8S ARC 部署）— 完整硬件设置

### 进阶路径（2 周）

**第 1 周**：实验 2（K8S ARC 部署）— 设置生产级基础设施
**第 2 周**：实验 1+3+4（结合所有三个）— 完整 AI-RAN 平台

---

## 故障排除

### 常见问题

#### 问题 1：GPU 内存不足
**症状**：Pod 卡在 `Pending`，事件显示 `Insufficient nvidia.com/gpu`
**修复**：
- 验证 MIG 配置：`nvidia-smi mig -l`
- 检查 GPU Operator 状态：`kubectl get pods -n gpu-operator`
- 减少 MIG 切片大小（从 `1g.6gb` 到 `1g.5gb`）

#### 问题 2：实时内核未启动
**症状**：节点卡在 `NotReady`，PREEMPT_RT 未激活
**修复**：
- 验证 GRUB 参数：`cat /proc/cmdline`
- 检查 `isolcpus` 语法（必须与 `nohz_full` 匹配）
- 重新构建 initramfs：`update-initramfs -u`

#### 问题 3：E2 遥测未流动
**症状**：Kafka topic 为空
**修复**：
- 验证 E2 终止 Pod 正在运行：`kubectl get pods -n near-rt-ric -l app=e2-term`
- 检查到 O-DU 的网络连接：`curl http://o-du:3801/healthz`
- 检查 E2 订阅 ID（必须与 xApp 注册匹配）

#### 问题 4：vLLM 加载模型缓慢
**症状**：vLLM Pod 花费 5+ 分钟启动
**修复**：
- 使用模型量化（AWQ、GPTQ）减少内存占用
- 增加 `startupProbe.initialDelaySeconds` 到 300
- 预下载模型到 PVC（避免每次启动拉取）

---

## 额外资源

### 视频演练

- [YouTube: 30 分钟构建 AI-RAN 代理](https://youtube.com/placeholder)
- [YouTube: 部署 NVIDIA ARC 和 K8S](https://youtube.com/placeholder)
- [YouTube: 数字孪生集成](https://youtube.com/placeholder)

### 社区

- [O-RAN 软件社区 Slack](https://slack.o-ran-sc.org/)
- [NVIDIA AI-RAN 论坛](https://forums.developer.nvidia.com/ai-ran)
- [K8S 电信 SIG](https://github.com/kubernetes/community/tree/master/sig-telecom)

### 参考实现

- [srsRAN](https://www.srsran.com/) — 开源 5G RAN
- [O-RAN SC RIC](https://o-ran-sc.org/) — O-RAN 软件社区 RIC
- [NVIDIA Aerial SDK 示例](https://developer.nvidia.com/aerial) — 官方示例代码

---

## 贡献

要添加新实验室：

1. 创建 markdown 文件：`<topic-name>.md`
2. 包括：概述、先决条件、步骤、验证、故障排除
3. 提供完整、可运行的代码（非片段）
4. 在本地环境测试（验证命令有效）
5. 用交叉引用更新本 README

---

## 参考文献

- [O-RAN 软件社区](https://o-ran-sc.org/)
- [NVIDIA Aerial SDK 文档](https://docs.nvidia.com/aerial/)
- [vLLM 文档](https://docs.vllm.ai/)
- [KServe 文档](https://kserve.github.io/)
- [Strimzi Kafka 文档](https://strimzi.io/)
