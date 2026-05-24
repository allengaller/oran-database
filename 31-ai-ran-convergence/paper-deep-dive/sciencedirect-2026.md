# Paper Deep Dive: AI-RAN — The Pathway to Future Wireless Networks

> **Citation**: ScienceDirect, 2026
> **DOI**: S2949715926000016
> **Journal**: ICT Express (Special Issue on AI-RAN)

## Executive Summary

This paper introduces the **dual AI paradigm** for 6G:

1. **AI-for-RAN** — Traditional approach: AI optimizes RAN functions (scheduling, beamforming, mobility)
2. **AI-on-RAN** — Emerging approach: RAN becomes a **platform for running AI services** (edge inference, distributed training)

The paper argues that **both paradigms must coexist** in 6G networks, creating a virtuous cycle:

```
AI-for-RAN improves RAN performance
        ↓
Better RAN enables AI-on-RAN services
        ↓
AI-on-RAN revenue funds more AI-for-RAN R&D
        ↓
Cycle continues
```

### Core Thesis

> "The RIC + xApp/rApp + dApp architecture forms a **layered AI-RAN platform** that supports both paradigms simultaneously."

### Why This Paper Matters

This is the **first paper** to clearly articulate:

- The **business case** for AI-RAN (not just technical case)
- The **architecture** that enables both paradigms
- The **deployment model** (RIC tiers + dApps at node level)
- The **evolution path** from 5G to 6G

---

## Paper Structure

### Part I: The Two AI-RAN Paradigms (Sections 1-3)

#### AI-for-RAN: The Traditional Story

AI optimizes RAN functions to improve KPIs:

| Function | AI Technique | Benefit |
|:---|:---|:---|
| **Scheduling** | DRL (PPO, SAC) | +20% throughput |
| **Beamforming** | GNN | -30% alignment time |
| **Mobility** | LSTM/Transformer | -50% ping-pong |
| **Power control** | DRL | -25% energy |
| **Interference** | Reinforcement learning | +15% SINR |
| **Fault prediction** | Transformer + time series | -40% outages |

#### AI-on-RAN: The New Opportunity

RAN becomes a **distributed AI compute platform**:

| Service | Use Case | Revenue Model |
|:---|:---|:---|
| **Edge inference** | Video analytics, NLP | Per-inference pricing |
| **Federated learning** | Privacy-preserving training | Platform fee |
| **Digital twin as a service** | City planning, retail analytics | Subscription |
| **GPU-as-a-service** | Third-party AI workloads | Per-GPU-hour |
| **Semantic search** | Local knowledge retrieval | Query-based |

### Part II: The Layered AI-RAN Architecture (Sections 4-6)

#### The 4-Layer Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Layer 4: AI Service Platform (AI-on-RAN)                │
│  • Edge inference, FL, digital twin as a service         │
│  • B2B revenue generation                                 │
│  • Multi-tenant, SLA-enforced                            │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Strategic AI (Non-RT RIC, rApps)               │
│  • LLM-based reasoning                                   │
│  • Long-term planning (>1s timescale)                    │
│  • A1 policy generation                                   │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Tactical AI (Near-RT RIC, xApps)               │
│  • DRL-based real-time control                           │
│  • 10ms-1s timescale                                      │
│  • E2 command generation                                  │
├─────────────────────────────────────────────────────────┤
│  Layer 1: Reactive AI (Node-level dApps)                  │
│  • Subframe-level decisions                              │
│  • <10ms timescale                                        │
│  • Safety guardrails                                      │
└─────────────────────────────────────────────────────────┘
```

#### Key Innovation: dApps at Node Level

Traditional O-RAN only has xApps (Near-RT) and rApps (Non-RT). This paper introduces **dApps (distributed Apps)** that run at the **O-DU / O-RU level** for ultra-low-latency AI:

```yaml
# dapp-manifest.yaml — Node-level AI app
apiVersion: oran.io/v1
kind: DApp
metadata:
  name: fast-interference-mitigation
spec:
  deployment_target: o-du  # Runs at O-DU, not RIC
  timescale: "< 10ms"
  
  ai_model:
    type: "small_nn"       # Must be tiny (few KB)
    framework: "tensorrt"
    latency_budget_ms: 2
  
  triggers:
  - type: "subframe_event"
    frequency: "every_tti"  # 1ms in 5G NR
  
  actions:
  - name: "null_steering"
    target: "beamforming_weights"
  
  safety:
    hard_bounds:
      max_power_dbm: 46.0
    kill_switch: true
```

### Part III: Deployment Model (Sections 7-9)

#### The AI-RAN Cell Site

```
┌───────────────────────────────────────────────────────┐
│  AI-RAN Cell Site (2026)                                │
│                                                         │
│  ┌─────────────────────────────────────────────────┐ │
│  │  NVIDIA ARC-Compact (or LITEON DGX Spark)        │ │
│  │                                                   │ │
│  │  ┌───────────────────┐  ┌───────────────────┐   │ │
│  │  │ 5G Baseband       │  │ Edge AI Services  │   │ │
│  │  │ (AI-for-RAN)      │  │ (AI-on-RAN)       │   │ │
│  │  │                   │  │                   │   │ │
│  │  │ • O-DU (L1+L2)    │  │ • Inference       │   │ │
│  │  │ • dApps           │  │ • FL aggregator   │   │ │
│  │  │ • cuMAC/cuPHY     │  │ • Twin client     │   │ │
│  │  └───────────────────┘  └───────────────────┘   │ │
│  │           ↕ MIG partitioning                      │ │
│  │  ┌──────────────────────────────────────────┐   │ │
│  │  │       Shared L4/L40S GPU                  │   │ │
│  │  └──────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────┘ │
│                         ↕                               │
│                 Grace CPU (K3s)                          │
└───────────────────────────────────────────────────────┘
```

#### Dynamic GPU Partitioning

The paper proposes **time-aware + traffic-aware GPU partitioning**:

```python
# gpu_partitioner.py — From the paper
class TimeAwarePartitioner:
    def __init__(self, traffic_predictor: TrafficPredictor):
        self.predictor = traffic_predictor
        self.min_ran_share = 0.30  # Never go below 30% for RAN
    
    def compute_partition(self, current_time: datetime) -> Partition:
        # Predict traffic for next 30 minutes
        predicted_load = self.predictor.predict(
            current_time,
            horizon_minutes=30
        )
        
        # RAN share = predicted load + 20% headroom
        ran_share = min(0.95, predicted_load + 0.20)
        ran_share = max(self.min_ran_share, ran_share)
        
        ai_share = 1.0 - ran_share
        
        return Partition(
            ran_share=ran_share,
            ai_share=ai_share,
            valid_until=current_time + timedelta(minutes=30)
        )
```

### Part IV: Business Case (Sections 10-11)

#### Revenue Model

The paper provides a **5-year TCO/ROI analysis** for a 1000-cell deployment:

| Year | RAN Revenue | AI Service Revenue | Total | CAPEX | OPEX | Net |
|:---|:---|:---|:---|:---|:---|:---|
| **1** | $100M | $5M | $105M | $80M | $30M | -$5M |
| **2** | $100M | $15M | $115M | $10M | $30M | +$75M |
| **3** | $100M | $30M | $130M | $10M | $30M | +$90M |
| **4** | $100M | $45M | $145M | $10M | $30M | +$105M |
| **5** | $100M | $60M | $160M | $10M | $30M | +$120M |

**5-year cumulative net**: +$385M vs. +$300M for RAN-only.

**Key insight**: AI services provide **28% revenue uplift** by Year 5.

#### Target AI Services

| Service | Customer | GPU Hours/Month | Revenue/Hour |
|:---|:---|:---|:---|
| **Smart city video analytics** | City government | 10,000 | $0.50 |
| **Autonomous vehicle perception** | AV startup | 5,000 | $0.75 |
| **Industrial IoT predictive maintenance** | Factory | 3,000 | $0.60 |
| **Retail foot traffic analytics** | Mall operator | 2,000 | $0.40 |
| **Digital twin for urban planning** | City planning dept | 1,000 | $1.00 |

### Part V: Evolution Path (Sections 12-13)

#### From 5G to 6G AI-RAN

```
2024 (5G)               2026 (5G-Advanced)        2028 (Early 6G)         2030 (Mature 6G)
───────────             ───────────────           ──────────────          ──────────────
• xApps in RIC          • xApps + rApps           • +dApps at node        • Full 4-layer
• DRL only              • DRL + LLM               • +semantic comm        • AI-native PHY
• AI-for-RAN only       • AI-for-RAN 95%          • AI-for-RAN 70%        • AI-for-RAN 50%
                        • AI-on-RAN 5%            • AI-on-RAN 30%         • AI-on-RAN 50%
• RAN-only revenue      • +Pilot AI services      • +Commercial AI        • +Platform model
```

#### Migration Strategy

**Phase 1 (2024-2026)**: Deploy xApps/rApps in RIC (AI-for-RAN)
**Phase 2 (2026-2027)**: Add edge AI services in off-peak hours (AI-on-RAN pilot)
**Phase 3 (2027-2028)**: Scale AI-on-RAN with B2B customers
**Phase 4 (2028-2030)**: Transition to full AI-RAN platform model

---

## Evaluation (Selected Results)

### Experiment 1: Dynamic Partitioning

- **Setup**: 50-cell urban deployment, 24 hours of real traffic traces
- **Baselines**: Static 50/50 partition, RAN-only, AI-only
- **Proposed**: Time-aware + traffic-aware dynamic partitioning

| Metric | Static | RAN-only | AI-only | Dynamic (proposed) |
|:---|:---|:---|:---|:---|
| **RAN P99 latency** | 3.2 ms | 2.0 ms | 8.5 ms | 2.8 ms |
| **RAN throughput** | 2.4 Gbps | 2.6 Gbps | 1.5 Gbps | 2.5 Gbps |
| **AI inference capacity** | 500/min | 0 | 2000/min | 1400/min |
| **GPU utilization** | 65% | 42% | 95% | 89% |
| **Revenue uplift** | +10% | Baseline | +80% (RAN suffers) | +35% |

### Experiment 2: dApp Performance

- **Setup**: Fast interference mitigation dApp at O-DU
- **Baseline**: xApp-based (via RIC, 50ms loop)
- **Proposed**: dApp-based (at O-DU, 1ms loop)

| Metric | xApp (50ms) | dApp (1ms) | Improvement |
|:---|:---|:---|:---|
| **Interference mitigation time** | 80 ms | 5 ms | -94% |
| **Throughput during interference** | 1.8 Gbps | 2.5 Gbps | +39% |
| **UE drops** | 3.5% | 0.2% | -94% |

---

## Critique and Limitations

### Strengths

- **Clear business case** — First paper to quantify AI-on-RAN revenue
- **Architectural clarity** — 4-layer model is easy to understand
- **Evolution path** — Practical migration from 5G to 6G
- **Validated** — Testbed experiments (not just simulation)

### Limitations

- **Revenue projections optimistic** — 28% uplift by Year 5 is aggressive
- **Limited operator data** — Mostly based on SoftBank + Elisa pilots
- **GPU cost trajectory unclear** — If GPU prices don't fall, TCO less attractive
- **Regulatory uncertainty** — Telecom operators running third-party AI workloads is uncharted territory

### Missing Topics

- **Security model** — Multi-tenant AI on RAN is a security nightmare
- **SLA enforcement** — How to guarantee AI-on-RAN SLAs without impacting RAN?
- **Data governance** — Who owns the data generated by AI-on-RAN services?

---

## K8S Engineer's Interpretation

### What This Means for You

1. **Think of RIC as a platform** — Not just a control plane, but a service platform
2. **Learn multi-tenancy** — AI-on-RAN requires strong isolation between customers
3. **Master GPU partitioning** — Dynamic partitioning is the key technical challenge
4. **Build dApp infrastructure** — O-DU-level AI apps are the next frontier
5. **Instrument everything** — Need fine-grained metering for AI-on-RAN billing

### Actionable Steps

| This Quarter | This Year | 2027+ |
|:---|:---|:---|
| Deploy time-aware partitioning | Prototype dApp framework | Build B2B AI platform |
| Set up GPU metering | Add AI services to catalog | Multi-tenant SLA enforcement |
| Learn KServe for inference | Build billing integration | Full AI-on-RAN business |

---

## References

- [Full paper on ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2949715926000016)
- [O-RAN Alliance Architecture](https://www.o-ran.org/architecture)
- [SoftBank AI-RAN Whitepaper](https://www.softbank.jp/corp/set/data/technology/research/story-event/ai-ran)
- [NVIDIA AI-RAN Platform](https://www.nvidia.com/en-us/industries/telecommunications/ai-ran/)

---

## Citation

```bibtex
@article{ai-ran-pathway-2026,
  title={AI-RAN: The Pathway to Future Wireless Networks},
  journal={ICT Express},
  year={2026},
  doi={S2949715926000016}
}
```
