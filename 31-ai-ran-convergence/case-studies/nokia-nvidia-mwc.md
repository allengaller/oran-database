# Case Study: Nokia + NVIDIA MWC 2026 Live Demonstration

> **Status**: Live demonstration at MWC Barcelona | **Date**: March 2026

## Executive Summary

At **MWC Barcelona 2026**, **Nokia** and **NVIDIA** delivered the first public demonstration of **AI-with-RAN** — running 5G baseband processing and AI inference workloads **simultaneously on the same GPU** in a live operator-like environment. This demonstration proved the technical feasibility of dynamic GPU partitioning and validated the AI-RAN business model.

## Demonstration Overview

### What Was Shown

The demo featured:
- **Live 5G NR traffic** running on Nokia AirScale baseband (powered by NVIDIA Aerial SDK)
- **Concurrent AI inference** workloads (video analytics, NLP) on the same GPU
- **Dynamic resource allocation** shifting GPU capacity between RAN and AI based on traffic patterns
- **Real-time monitoring** showing zero impact on RAN latency SLOs during AI workload spikes

### Live Environment Specs

```
┌─────────────────────────────────────────────────┐
│  MWC 2026 Nokia Booth - Live Demo                 │
│                                                   │
│  Hardware:                                        │
│  • NVIDIA ARC-Compact (L4 GPU + Grace CPU)       │
│  • Nokia AirScale baseband software              │
│  • 3 UEs generating live 5G traffic              │
│                                                   │
│  Software:                                        │
│  • NVIDIA Aerial SDK (cuMAC + cuPHY)            │
│  • Triton Inference Server (B2B AI workloads)   │
│  • K8S orchestration with GPU Operator          │
│                                                   │
│  Scenarios demonstrated:                          │
│  • Normal operation (60% RAN, 40% AI)           │
│  • Traffic spike (85% RAN, 15% AI)              │
│  • Off-peak (30% RAN, 70% AI)                   │
└─────────────────────────────────────────────────┘
```

## Technical Architecture

### Shared GPU Infrastructure

The core innovation demonstrated was **dynamic GPU resource sharing**:

```
Time    │ RAN Share │ AI Share │ Traffic Load
────────┼───────────┼──────────┼─────────────
10:00   │    60%    │   40%    │ Moderate
10:15   │    85%    │   15%    │ Spike (simulated event)
10:30   │    60%    │   40%    │ Moderate
10:45   │    30%    │   70%    │ Low (off-peak)
```

### Key Components

| Component | Role | Technology |
|:---|:---|:---|
| **NVIDIA ARC-Compact** | Hardware platform | L4 GPU (72W) + Grace CPU |
| **cuMAC** | GPU L2 scheduler | NVIDIA Aerial SDK |
| **cuPHY** | GPU physical layer | CUDA kernels |
| **Triton Server** | AI inference | TensorRT optimized models |
| **MIG** | GPU partitioning | 1g.6gb slices |
| **K8S** | Orchestration | GPU Operator + custom scheduler |

### K8S Manifest (Simplified)

```yaml
# mwc-demo/baseband-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: cumac-baseband-demo
  annotations:
    nvidia.com/mig-profile: "1g.6gb"
spec:
  runtimeClassName: nvidia-rt
  containers:
  - name: cumac
    image: nvcr.io/nvidia/aerial/cumac:24.07
    resources:
      limits:
        nvidia.com/mig-1g.6gb: 1
        cpu: "8"
        memory: "12Gi"
    env:
    - name: GPU_PARTITION_MODE
      value: "dynamic"  # Key innovation
    - name: MIN_RAN_GPU_SHARE
      value: "30"       # Guaranteed minimum
```

```yaml
# mwc-demo/ai-workload-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: ai-inference-demo
spec:
  containers:
  - name: triton
    image: nvcr.io/nvidia/tritonserver:24.05-py3
    resources:
      limits:
        nvidia.com/mig-1g.6gb: 1
    env:
    - name: GPU_PARTITION_MODE
      value: "elastic"   # Can scale down under RAN pressure
```

## Demonstration Scenarios

### Scenario 1: Normal Operation
**Setup**:
- 3 UEs streaming 4K video (downlink-heavy)
- 2 B2B AI workloads: video analytics + NLP sentiment analysis
- GPU partitioning: 60% RAN, 40% AI

**Observed**:
- RAN latency: 2.1ms (target: <5ms) ✓
- AI inference latency: 45ms average
- GPU utilization: 78%
- No dropped packets, stable video quality

### Scenario 2: Traffic Spike
**Setup**:
- Simulated stadium-like event: 20 additional UEs join simultaneously
- RAN demands more GPU cycles for scheduling

**Observed**:
- GPU scheduler **automatically** shifted allocation to 85% RAN, 15% AI
- AI workloads **gracefully degraded** (inference latency increased to 120ms)
- RAN latency stayed at 2.8ms (still within SLO)
- Zero UE drops during spike
- **Recovery**: After 5 minutes, allocation returned to normal

### Scenario 3: Off-Peak AI Maximization
**Setup**:
- Reduced traffic to 1 UE
- Maximize AI workload utilization

**Observed**:
- GPU allocation: 30% RAN, 70% AI
- AI throughput increased 3.5x vs. normal operation
- RAN latency unchanged (still meeting SLO)
- Demonstrated the **revenue opportunity** for off-peak AI services

## Results and Metrics

### Quantitative Results

| Metric | RAN Only | AI-RAN Shared | Delta |
|:---|:---|:---|:---|
| **RAN latency (P99)** | 2.0ms | 2.8ms | +40% (still within SLO) |
| **RAN throughput** | 2.4 Gbps | 2.3 Gbps | -4% (negligible) |
| **GPU utilization** | 45% | 92% | +104% |
| **Power per bit** | 1.0x | 0.7x | -30% improvement |
| **Revenue potential** | 1.0x | 2.3x | +130% (with AI services) |

### Key Validations

1. ✅ **RAN SLOs maintained** under all AI workload scenarios
2. ✅ **Dynamic GPU partitioning** works without manual intervention
3. ✅ **Revenue uplift** from AI services validated
4. ✅ **Power efficiency** improved through higher GPU utilization

## Business Impact

### For Nokia
- Validated their **AI-RAN product strategy** with NVIDIA
- Demonstrated **AirScale evolution path** from ASIC to GPU
- Positioned Nokia as **AI-RAN leader** for operator RFPs

### For NVIDIA
- Validated **ARC platform** in real-world operator scenario
- Showcased **Aerial SDK** maturity
- Drove **$1B Nokia investment** narrative

### For Operators (Attendees)
- Proved **technical feasibility** of AI-with-RAN
- Demonstrated **clear business case** (130% revenue uplift potential)
- Reduced **perceived risk** of GPU-based RAN

## Lessons Learned

### Technical
1. **Dynamic partitioning requires smart scheduler** — Default K8S scheduler can't balance RAN+AI
2. **AI workload must be "shrinkable"** — Not all AI workloads can gracefully scale down
3. **Monitoring is crucial** — Without real-time GPU metrics, partitioning decisions fail
4. **Pre-validated workloads only** — Unknown AI workloads can still surprise the scheduler

### Demonstration Execution
1. **Rehearse failure scenarios** — Demo team practiced traffic spike response 50+ times
2. **Isolate demo network** — MWC show floor RF environment is noisy; isolated lab used
3. **Have backup scenarios** — Three demo variants for different audience technical levels
4. **Live telemetry dashboard** — Grafana dashboard made the partitioning visible to audience

## Replicating This Demo

For K8S engineers wanting to replicate in their own lab:

### Minimum Requirements
- 1x NVIDIA ARC-Compact (or any L4 GPU server)
- Ubuntu 22.04 with RT kernel
- K8S 1.28+ with NVIDIA GPU Operator
- NVIDIA Aerial SDK access (requires NDA)

### Approximate Cost
- Hardware: ~$25,000 (ARC-Compact)
- Software: Aerial SDK (NDA), Triton (free)
- Lab time: 2-3 weeks for setup and validation

### Open-Source Alternative
For learning without Aerial SDK:
- Use **srsRAN** (open-source 5G RAN) on GPU
- Combine with **Triton Inference Server**
- Demonstrates the same architectural patterns

## References

- [Nokia MWC 2026 Press Release](https://www.nokia.com/newsroom/nokia-accelerates-ai-ran-momentum-with-new-partnerships-driving-path-to-ai-native-6g-mwc26/)
- [NVIDIA Software-Defined AI-RAN (Feb 2026)](https://blogs.nvidia.com/blog/software-defined-ai-ran/)
- [NVIDIA ARC-Compact](https://developer.nvidia.com/blog/deploy-ai-ran-at-cell-sites-with-nvidia-arc-compact/)
- [AI-RAN Alliance Demonstrations](https://ai-ran.org/demonstrations)
- [6G Flagship: AI-RAN Momentum](https://www.6gflagship.com/news/ai-ran-momentum-builds-and-it-might-be-time-to-pay-attention/)
