# Case Study: SoftBank Commercial AI-RAN Launch

> **Status**: Planned commercial launch in 2026 | **Location**: Japan

## Executive Summary

**SoftBank** is the first major operator to announce plans for a **commercial AI-RAN service launch** in 2026. The initiative reimagines cell sites as **multi-purpose AI + RAN + edge compute platforms**, monetizing excess GPU capacity through B2B edge AI services.

## Background

SoftBank published a comprehensive **AI-RAN Whitepaper** (December 2024) that laid the groundwork for its commercial strategy:

### Key Whitepaper Concepts
- **Virtualized RAN** on NVIDIA accelerated computing platforms
- **GPU sharing** between baseband and third-party AI workloads
- **Revenue diversification** through edge AI services
- **Cost efficiency** from unified infrastructure

## Architecture

### The AI-RAN Cell Site

```
┌───────────────────────────────────────────────────────┐
│         SoftBank AI-RAN Cell Site                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │           NVIDIA ARC Platform                    │  │
│  │                                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐              │  │
│  │  │ 5G Baseband  │  │ Edge AI      │              │  │
│  │  │ (cuMAC+cuPHY)│  │ Services     │              │  │
│  │  │              │  │              │              │  │
│  │  │ • cuMAC L2   │  │ • Inference  │              │  │
│  │  │ • cuPHY L1   │  │ • Training   │              │  │
│  │  │              │  │ • Digital    │              │  │
│  │  │              │  │   Twin       │              │  │
│  │  └──────────────┘  └──────────────┘              │  │
│  │           ↕ NVIDIA MIG (GPU partitioning)         │  │
│  │  ┌──────────────────────────────────────────┐    │  │
│  │  │       NVIDIA L4 / Grace Hopper GPU       │    │  │
│  │  └──────────────────────────────────────────┘    │  │
│  └─────────────────────────────────────────────────┘  │
│                         ↕                                │
│  ┌─────────────────────────────────────────────────┐  │
│  │           K8S Control Plane (Grace CPU)          │  │
│  └─────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

### Resource Allocation Model

SoftBank's innovation is the **time-aware GPU partitioning** model:

| Time Window | RAN Allocation | AI Services Allocation |
|:---|:---|:---|
| **Peak traffic** (7-10 AM, 5-8 PM) | 80% | 20% |
| **Business hours** (10 AM-5 PM) | 60% | 40% |
| **Off-peak** (8 PM-7 AM) | 30% | 70% |
| **Weekend overnight** | 20% | 80% |

This ensures **RAN always has guaranteed resources** while **AI services use elastic capacity**.

## Business Model

### Three Revenue Streams

1. **Traditional Connectivity** (existing)
   - 5G data plans for consumers and enterprises
   - SLA-based pricing

2. **Edge AI-as-a-Service** (new)
   - B2B customers deploy AI inference workloads on SoftBank cell sites
   - Pricing: per-GPU-hour + egress
   - Target customers: smart city, autonomous vehicles, industrial IoT

3. **Digital Twin Services** (new)
   - Enterprises subscribe to city-scale digital twin data
   - Used for urban planning, retail analytics, traffic optimization

### Customer Personas

| Customer | Use Case | GPU Requirement |
|:---|:---|:---|
| **Autonomous vehicle startup** | Real-time object detection at intersections | 1 MIG slice per intersection |
| **Smart city operator** | Traffic light optimization | 2-3 MIG slices per district |
| **Retail analytics** | Foot traffic analysis from RF sensing | 1 MIG slice per mall |
| **Industrial IoT** | Predictive maintenance in factories | 1 MIG slice per factory |

## Technical Implementation

### K8S Stack

```yaml
# SoftBank AI-RAN platform stack
Platform:
  kubernetes: v1.29
  gpu_operator: v24.3
  mig_strategy: mixed
  
Orchestration:
  runtime: containerd + nvidia-container-toolkit
  cni: multus + sriov (fronthaul) + calico (management)
  scheduler: custom with real-time awareness

Observability:
  gpu_monitoring: DCGM Exporter
  metrics: Prometheus + Grafana
  tracing: Jaeger
  logging: Fluentd → Elasticsearch

AI Platform:
  inference: NVIDIA Triton Inference Server
  training: PyTorch + NVIDIA NeMo
  registry: Harbor (private)
```

### Multi-Tenancy Model

```
K8S Cluster (per region)
├── Namespace: softbank-ran         # SoftBank 5G RAN
├── Namespace: customer-av-startup  # AV customer workloads
├── Namespace: customer-smart-city  # Smart city workloads
├── Namespace: customer-retail      # Retail analytics
└── Namespace: softbank-twin        # Digital twin services
```

Each customer namespace has:
- **Network policies** isolating from other tenants
- **Resource quotas** limiting GPU, CPU, memory
- **Audit logging** for compliance

## Timeline

| Date | Milestone |
|:---|:---|
| **Dec 2024** | AI-RAN Whitepaper published |
| **H1 2025** | Lab trials with NVIDIA |
| **H2 2025** | Field trials in Tokyo |
| **Q1 2026** | Commercial launch (initial 50 cell sites) |
| **H2 2026** | Scale to 500+ cell sites |
| **2027** | Nationwide rollout planned |

## Challenges and Mitigations

### Technical Challenges

| Challenge | Impact | Mitigation |
|:---|:---|:---|
| **RAN latency SLOs** | Missed deadlines = poor user experience | MIG isolation + real-time kernel |
| **Power budget** | Cell sites have 300-500W envelope | 72W L4 GPU + power capping |
| **Thermal management** | Outdoor cabinets in Japanese summer | Liquid cooling + ruggedized enclosure |
| **Network slicing** | AI workloads must not impact RAN SLA | Strict network policies + QoS |

### Business Challenges

| Challenge | Impact | Mitigation |
|:---|:---|:---|
| **Customer acquisition** | New market, unproven model | Partner with system integrators |
| **Regulatory** | Telecom + AI crosses regulatory boundaries | Early engagement with MIC Japan |
| **SLA enforcement** | Multi-tenant SLAs complex | Tiered SLA model with clear boundaries |
| **Security** | Multi-tenant security concerns | Zero-trust architecture + tenant isolation |

## Lessons Learned

### For Engineers

1. **MIG is essential** — Without it, noisy neighbor effects break RAN SLOs
2. **Real-time kernel is non-negotiable** — Standard kernels can't meet baseband deadlines
3. **Power capping must be hardware-enforced** — Software limits are insufficient
4. **Observability from day 1** — GPU metrics are critical for capacity planning

### For Business Leaders

1. **Start with anchor customers** — 2-3 reference customers validate the model
2. **Tiered pricing** — Simple GPU-hour pricing is easier than complex models
3. **Partner ecosystem** — SI partners drive customer acquisition
4. **Regulatory early engagement** — Don't wait for issues; shape the rules

## K8S Engineer Action Items

If you're building similar infrastructure:

1. **Install NVIDIA GPU Operator with MIG**
2. **Deploy custom scheduler with real-time awareness**
3. **Configure Multus + SR-IOV for fronthaul**
4. **Set up DCGM Exporter for GPU observability**
5. **Implement network policies for tenant isolation**
6. **Use KServe for AI model serving**

## References

- [SoftBank AI-RAN Whitepaper (Dec 2024)](https://www.softbank.jp/corp/set/data/technology/research/story-event/Whitepaper_Download_Location/pdf/SoftBank_AI_RAN_Whitepaper_December2024.pdf)
- [Juniper Research: What's Next for AI-RAN?](https://www.juniperresearch.com/resources/blog/nvidia-just-revealed-what-s-next-for-ai-ran-will-operators-buy-in/)
- [AI-RAN Alliance](https://ai-ran.org/)
- [NVIDIA AI-RAN Solutions](https://www.nvidia.com/en-us/industries/telecommunications/ai-ran/)
