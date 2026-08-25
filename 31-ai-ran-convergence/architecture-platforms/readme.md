---
title: "AI-RAN Architecture & Platforms (2026)"
description: "> **Updated: 2026-05** | Sources: NVIDIA Developer, Nokia MWC 2026, GTC 2026"
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-08-25"
keywords: ['AI-RAN', 'RIC', '5G']
---

# AI-RAN Architecture & Platforms (2026)

> **Updated: 2026-05** | Sources: NVIDIA Developer, Nokia MWC 2026, GTC 2026

## 1. The AI-RAN Hardware Revolution

### From ASIC/FPGA to GPU: Why the Shift?

Traditional baseband processing relied on custom ASICs or FPGAs. The shift to GPU-based processing is driven by:

1. **Flexibility**: GPU can run both baseband (5G NR PHY/MAC) and AI workloads on the same silicon
2. **AI-native**: GPU is the native platform for ML inference and training
3. **Software-defined**: CUDA ecosystem enables rapid algorithm updates vs. fixed-function hardware
4. **Economics**: Shared infrastructure reduces total cost of ownership

### The AI-RAN Compute Stack

```
┌────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ xApp     │ │ AI Model │ │ Digital  │ │ Edge AI  │ │
│  │ Control  │ │ Inference│ │ Twin     │ │ Service  │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
├────────────────────────────────────────────────────────┤
│                   Platform Layer                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ NVIDIA Aerial SDK                                 │  │
│  │  ├── cuMAC (GPU-accelerated L2 MAC Scheduler)    │  │
│  │  ├── cuPHY (GPU-accelerated Physical Layer)      │  │
│  │  ├── pyAerial (Python API bindings)              │  │
│  │  └── Aerial Framework (end-to-end RAN pipeline)  │  │
│  └──────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────┤
│                   Hardware Layer                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ NVIDIA ARC / ARC-Compact                         │  │
│  │  ├── Grace CPU (ARM-based, high-throughput)      │  │
│  │  ├── L4/L40S/Grace Hopper GPU                   │  │
│  │  ├── NVLink (CPU-GPU high-bandwidth)             │  │
│  │  └── BlueField DPU (network acceleration)        │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 2. NVIDIA ARC Platform Family

### NVIDIA ARC (Aerial RAN Computer)

The full-scale platform for high-capacity cell sites:

| Component | Specification | Purpose |
|:---|:---|:---|
| **CPU** | NVIDIA Grace (ARM v9, 72 cores) | Control plane, OS, container runtime |
| **GPU** | L40S / H100-class | Baseband processing + AI inference |
| **DPU** | BlueField-3 | Network offload, security, storage |
| **Power** | 300-500W | Macro cell site with multiple sectors |
| **Form Factor** | 2U rack-mount | Standard telecom rack |
| **5G Capacity** | Up to 100 MHz × 4 sectors | High-capacity urban deployment |

### NVIDIA ARC-Compact

The power-optimized platform for typical cell sites:

| Component | Specification | Purpose |
|:---|:---|:---|
| **CPU** | NVIDIA Grace (ARM v9) | Control plane, orchestration |
| **GPU** | L4 (72W TDP) | Baseband + edge AI inference |
| **Power** | 72W GPU + ~150W total | Fits within cell site power budget |
| **Form Factor** | Compact/ruggedized | Outdoor cabinet, street pole |
| **5G Capacity** | Up to 40 MHz × 3 sectors | Standard suburban/rural |

**Key insight for K8S engineers**: ARC-Compact's 72W L4 GPU is specifically designed to fit within the typical 300W cell-site power envelope while leaving headroom for AI workloads.

### Comparison: Traditional vs. AI-RAN Hardware

| Dimension | Traditional RAN | AI-RAN (NVIDIA ARC) |
|:---|:---|:---|
| **Processor** | Custom ASIC / FPGA | NVIDIA GPU + Grace CPU |
| **Baseband** | Fixed-function hardware | Software-defined (CUDA) |
| **AI Capability** | None or external | Native (on-chip) |
| **Upgrade Path** | Hardware swap | Software update |
| **Edge AI Revenue** | Not possible | GPU sharing with B2B AI |
| **Power** | 200-500W | 150-500W (comparable) |
| **Vendor Lock-in** | High (proprietary) | Low (open CUDA APIs) |

---

## 3. GPU-Accelerated Baseband: NVIDIA Aerial SDK

### Architecture

```
┌─────────────────────────────────────────┐
│          Aerial Framework                │
│  ┌──────────────────────────────────┐   │
│  │      5G NR Protocol Stack        │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐       │   │
│  │  │ L3  │ │ L2  │ │ L1  │       │   │
│  │  │RRC/ │ │MAC/ │ │PHY  │       │   │
│  │  │PDCP │ │RLC  │ │     │       │   │
│  │  └─────┘ └─────┘ └─────┘       │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │      GPU Acceleration Libraries   │   │
│  │  ┌────────┐ ┌────────┐          │   │
│  │  │ cuMAC  │ │ cuPHY  │          │   │
│  │  │Scheduler│ │Signal  │          │   │
│  │  │        │ │Process │          │   │
│  │  └────────┘ └────────┘          │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │      Developer APIs               │   │
│  │  ┌────────┐ ┌────────┐          │   │
│  │  │pyAerial│ │ CUDA   │          │   │
│  │  │(Python)│ │(C/C++) │          │   │
│  │  └────────┘ └────────┘          │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### cuMAC: GPU-Accelerated MAC Scheduler
- **Function**: L2 scheduler for resource allocation and scheduling in the baseband
- **Performance**: Sub-millisecond scheduling decisions for hundreds of UEs
- **AI Integration**: ML models can be embedded directly in the scheduling loop
- **Open Source**: Available on [GitHub: NVIDIA/aerial-cuda-accelerated-ran](https://github.com/NVIDIA/aerial-cuda-accelerated-ran)

### cuPHY: GPU-Accelerated Physical Layer
- **Function**: 5G NR physical layer processing (FFT/IFFT, channel coding, modulation)
- **Performance**: Real-time processing on L4 GPU for standard carrier configurations
- **Flexibility**: Algorithm updates via CUDA code changes (no hardware redesign)

### pyAerial: Python API Bindings
- **Purpose**: Enable Python-based development for RAN algorithms
- **Use Case**: Rapid prototyping of ML-enhanced baseband algorithms
- **Integration**: Direct connection to PyTorch/TensorFlow for ML pipelines

---

## 4. AI-RAN Reference Architecture (2026)

### Full Stack Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     SMO (Service Management & Orchestration)     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Non-RT RIC   │  │ Digital Twin │  │ AI Model Registry    │ │
│  │  ┌────────┐  │  │  Platform    │  │  ┌────────────────┐  │ │
│  │  │ rApps  │  │  │              │  │  │ Telecom LLM    │  │ │
│  │  │ (AI    │  │  │  City-scale  │  │  │ DRL Models     │  │ │
│  │  │ Agents)│  │  │  simulation  │  │  │ GNN Models      │  │ │
│  │  └────────┘  │  │              │  │  └────────────────┘  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘ │
│         │ A1               │ Twin Sync           │ Model Deploy │
├─────────┼──────────────────┼─────────────────────┼─────────────┤
│         ▼                  ▼                     ▼             │
│              Near-RT RIC (Edge Cloud / K8S)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ xApps        │  │ Agentic AI   │  │ ML Inference         │ │
│  │  ┌────────┐  │  │  ┌────────┐  │  │  ┌────────────────┐  │ │
│  │  │Energy  │  │  │  │Network │  │  │  │ONNX Runtime    │  │ │
│  │  │Saving  │  │  │  │Agent   │  │  │  │OpenVINO        │  │ │
│  │  ├────────┤  │  │  │(LLM)   │  │  │  │TensorRT        │  │ │
│  │  │Mobility│  │  │  └────────┘  │  │  └────────────────┘  │ │
│  │  └────────┘  │  │              │  │                       │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘ │
│         │ E2               │                     │             │
├─────────┼──────────────────┼─────────────────────┼─────────────┤
│         ▼                  ▼                     ▼             │
│              AI-RAN Cell Site (NVIDIA ARC)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    GPU Compute Plane                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │  │
│  │  │ Baseband     │  │ Edge AI      │  │ Digital Twin   │ │  │
│  │  │ Processing   │  │ Inference    │  │ Agent          │ │  │
│  │  │ (cuMAC+cuPHY)│  │ (B2B Service)│  │ (Local Sync)   │ │  │
│  │  └──────┬───────┘  └──────┬───────┘  └───────┬────────┘ │  │
│  │         │                  │                   │          │  │
│  │  ┌──────┴──────────────────┴───────────────────┴───────┐ │  │
│  │  │         NVIDIA GPU Resource Manager                   │ │  │
│  │  │  (Dynamic partitioning: RAN ↔ AI ↔ Twin)             │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────┬────────────────────────────────┘  │
│                              │ eCPRI (O-RAN Fronthaul)           │
├──────────────────────────────┼───────────────────────────────────┤
│                              ▼                                   │
│                    O-RU (Radio Unit)                             │
│               Antenna + RF Frontend                             │
└──────────────────────────────────────────────────────────────────┘
```

### GPU Resource Partitioning (AI-with-RAN)

The key innovation in 2026 is **dynamic GPU resource sharing** between RAN and AI:

```
Time:   ┌──────────────────────────────────────────────┐
        │  Peak Traffic (08:00-20:00)                   │
GPU:    │  [████████ RAN 80% ████] [██ AI 20% ██]      │
        │                                               │
        │  Off-Peak (20:00-08:00)                       │
GPU:    │  [████ RAN 30% ████] [████████ AI 70% ████████]│
        └──────────────────────────────────────────────┘
```

- **Priority**: RAN always gets guaranteed minimum resources
- **Elasticity**: AI workloads use available GPU capacity dynamically
- **Isolation**: Hardware-level isolation ensures RAN latency SLOs are met
- **Revenue**: Off-peak AI inference serves B2B customers (e.g., smart city, autonomous vehicles)

---

## 5. LITEON DGX Spark O-RAN (GTC 2026)

At GTC 2026, LITEON demonstrated an O-RAN solution compatible with **NVIDIA DGX Spark**:

### Key Features
- **Form Factor**: Desktop-sized edge AI + RAN platform
- **GPU**: NVIDIA Grace Blackwell architecture
- **Use Case**: Small cell / enterprise 5G + edge AI
- **Significance**: Demonstrates that AI-RAN can scale down to enterprise deployments

### Architecture
- DGX Spark runs both 5G vRAN (via Aerial SDK) and edge AI applications
- Enterprises can deploy private 5G + on-premise AI on a single platform
- Ideal for factories, hospitals, and campuses requiring both low-latency connectivity and AI

---

## 6. Edge Computing Integration Patterns

### Pattern 1: Co-located AI + RAN (AI-with-RAN)
```
NVIDIA ARC at Cell Site
├── RAN: cuMAC + cuPHY (baseband)
├── AI: Inference engine (TensorRT)
└── Shared: GPU memory, NVLink bandwidth
```
**Pros**: Lowest latency, highest efficiency
**Cons**: Complex resource management, RAN-first constraints

### Pattern 2: Adjacent AI Cluster (AI-on-RAN)
```
Cell Site Rack
├── NVIDIA ARC (RAN only)
├── Separate GPU server (AI only)
└── Connected: 25GbE / NVLink bridge
```
**Pros**: Simpler management, independent scaling
**Cons**: Higher latency for AI-RAN interaction, more hardware

### Pattern 3: Regional Edge AI (AI-for-RAN)
```
Regional Edge Data Center
├── Near-RT RIC (xApps + ML inference)
├── AI training cluster (GPUs)
└── Connected to cell sites via E2 interface
```
**Pros**: Centralized management, full GPU power for training
**Cons**: Higher latency (10ms-1s), limited to Non-RT/Near-RT use cases

---

## 7. K8S Engineering Considerations for AI-RAN

### GPU Scheduling on K8S
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ai-ran-workload
spec:
  containers:
  - name: baseband
    image: nvidia/aerial-cuMAC:latest
    resources:
      limits:
        nvidia.com/gpu: 1
        nvidia.com/mig-1g.10gb: 1  # MIG partition for baseband
  - name: ai-inference
    image: custom/edge-ai:latest
    resources:
      limits:
        nvidia.com/mig-1g.10gb: 1  # MIG partition for AI
```

### Key Challenges
1. **Real-time guarantees**: Baseband processing must meet strict timing SLOs
2. **GPU partitioning**: NVIDIA MIG (Multi-Instance GPU) for workload isolation
3. **Network topology**: Multi-homed pods (management, fronthaul, midhaul)
4. **Power management**: GPU power capping to stay within cell-site budget
5. **Thermal management**: Ruggedized enclosures for outdoor deployment

### Recommended K8S Stack for AI-RAN
- **Runtime**: Containerd with NVIDIA Container Toolkit
- **CNI**: Multus CNI + SR-IOV for fronthaul
- **GPU**: NVIDIA GPU Operator + MIG Manager
- **Scheduling**: Custom scheduler with real-time awareness
- **Observability**: DCGM Exporter + Prometheus + Grafana

---

## References

- [NVIDIA ARC-Compact Deployment Guide](https://developer.nvidia.com/blog/deploy-ai-ran-at-cell-sites-with-nvidia-arc-compact/)
- [NVIDIA Aerial CUDA-Accelerated RAN (GitHub)](https://github.com/NVIDIA/aerial-cuda-accelerated-ran)
- [NVIDIA Software-Defined AI-RAN (Feb 2026)](https://blogs.nvidia.com/blog/software-defined-ai-ran/)
- [Nokia AI-RAN MWC 2026](https://www.nokia.com/newsroom/nokia-accelerates-ai-ran-momentum-with-new-partnerships-driving-path-to-ai-native-6g-mwc26/)
- [LITEON DGX Spark O-RAN (GTC 2026)](https://www.liteon.com/en/news/press-center/content/liteon-gtc-2026-ai-ran)
- [NVIDIA AI-RAN Solutions](https://www.nvidia.com/en-us/industries/telecommunications/ai-ran/)
- [Nokia Full AI-RAN GPU Play (The Mobile Network)](https://the-mobile-network.com/2025/10/nokia-commits-to-full-ai-ran-gpu-play-on-new-nvidia-ran-compute-platform/)
- [6G Legend: NVIDIA Leads (36Kr)](https://eu.36kr.com/en/p/3542374903017600)
