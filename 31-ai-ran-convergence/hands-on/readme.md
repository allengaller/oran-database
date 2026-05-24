# AI-RAN Hands-On Labs (2026)

> **Updated: 2026-05** | For K8S Engineers building real AI-RAN systems

## Overview

This directory contains **production-ready code examples, deployment manifests, and configuration templates** for engineers building AI-RAN systems in 2026. All examples are Kubernetes-native and reflect the latest Agentic AI, NVIDIA ARC, and Digital Twin patterns.

### Prerequisites
- Kubernetes cluster 1.28+ with NVIDIA GPU Operator installed
- Access to NVIDIA ARC or L4 GPU nodes (for baseband workloads)
- Familiarity with O-RAN RIC platform (see [07-ric-development](../../07-ric-development/))
- Python 3.11+, Helm 3, kubectl

---

## Lab Catalog

### 1. [Agentic AI Agent Code](./agentic-agent-code.md)
Build a production-grade **LLM-powered network agent** for the Non-RT RIC:
- Python class with tool-use pattern
- Integration with TimesFM, PPO, GNN, NVIDIA AODT
- Safety guardrails and rollback logic
- Natural language reasoning chains
- Prometheus metrics export

### 2. [NVIDIA ARC K8S Deployment](./k8s-arc-deployment.md)
Deploy GPU-accelerated baseband workloads on Kubernetes:
- MIG partitioning for RAN + AI coexistence
- Real-time kernel node configuration
- SR-IOV + DPDK for fronthaul networking
- DCGM Exporter for GPU observability
- Power capping and thermal management

### 3. [Telecom-LLM Deployment](./telecom-llm-deployment.md)
Deploy a **telecom-tuned SLM** as a Non-RT RIC rApp service:
- vLLM serving with quantized Qwen2.5-7B-Telecom
- KServe integration for canary releases
- LoRA adapter management for domain specialization
- Intent translation API (NL → policy YAML)
- Root cause analysis from alarm logs

### 4. [Digital Twin Sync Agent](./digital-twin-sync.md)
Build a real-time **twin synchronization agent** running on K8S:
- E2 interface subscriber for RIC telemetry
- Kafka + Flink streaming pipeline
- NVIDIA AODT REST API integration
- Out-of-sync detection and alerting
- Historical twin state storage (TimescaleDB)

---

## Quick Start

```bash
# Clone the hands-on materials
cd 31-ai-ran-convergence/hands-on

# Verify cluster readiness
kubectl get nodes -l nvidia.com/gpu.product -o wide

# Start with Lab 1 (Agentic Agent)
cat agentic-agent-code.md

# Deploy the agent to Non-RT RIC namespace
kubectl apply -f manifests/agentic-agent-deployment.yaml
```

---

## Architecture Reference

```
┌─────────────────────────────────────────────────────────────┐
│                 Non-RT RIC (Central K8S)                      │
│                                                               │
│  Lab 3: Telecom-LLM           Lab 1: Agentic Agent           │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │ vLLM + Qwen2.5   │◄────────│ Python Agent     │          │
│  │ (Intent + RCA)   │         │ (Tool-use + LLM) │          │
│  └──────────────────┘         └────────┬─────────┘          │
│                                        │ Tool calls          │
│                               ┌────────▼─────────┐          │
│                               │ Lab 4: Twin Sync │          │
│                               │ (Kafka + AODT)   │          │
│                               └────────┬─────────┘          │
└────────────────────────────────────────┼────────────────────┘
                                         │ A1 policies
┌────────────────────────────────────────┼────────────────────┐
│                 Near-RT RIC (Edge K8S) │                      │
│                                         ▼                     │
│                               ┌──────────────────┐          │
│                               │ xApps (DRL/GNN)  │          │
│                               └────────┬─────────┘          │
└────────────────────────────────────────┼────────────────────┘
                                         │ E2
┌────────────────────────────────────────┼────────────────────┐
│        AI-RAN Cell Site (NVIDIA ARC)   ▼                      │
│                                                               │
│  Lab 2: ARC K8S Deployment                                    │
│  ┌──────────────────────────────────────────────────┐        │
│  │  MIG 1g.10gb: cuMAC baseband  (RAN)              │        │
│  │  MIG 1g.10gb: TensorRT inference (AI service)    │        │
│  └──────────────────────────────────────────────────┘        │
└──────────────────────────────────────────────────────────────┘
```

---

## Safety First

All labs include safety guardrails following WG11 Secure AI specifications:

1. **Hard-coded bounds** on all actuator commands
2. **Digital twin pre-validation** before any network action
3. **Rate limiting** on action execution frequency
4. **Audit logging** with full reasoning chains
5. **Kill switch** for immediate manual override
6. **Gradual rollout** patterns (5% → 25% → 100%)

---

## Related Resources

- [Agentic AI Theory](../agentic-ai/readme.md) — conceptual background
- [Architecture & Platforms](../architecture-platforms/readme.md) — NVIDIA ARC details
- [Digital Twin](../digital-twin/readme.md) — AODT concepts
- [07-ric-development](../../07-ric-development/) — RIC platform fundamentals

---

## Contributing

These labs are production-tested starting points. Adapt to your operator's:
- Security policies (mTLS, OAuth, PKI)
- Observability stack (OpenTelemetry vs. Prometheus)
- CI/CD pipelines (ArgoCD, Flux, Tekton)
- Network topology (multi-cluster, hybrid cloud)
