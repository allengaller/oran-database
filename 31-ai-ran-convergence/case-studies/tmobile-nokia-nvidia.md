---
title: "Case Study: T-Mobile + Nokia + NVIDIA AI-RAN Trials"
description: "> **Status**: Field trials 2025-2026 | **Location**: United States (Bellevue, WA lab + field sites)"
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-08-25"
keywords: ['AI-RAN', 'RIC', '5G']
---

# Case Study: T-Mobile + Nokia + NVIDIA AI-RAN Trials

> **Status**: Field trials 2025-2026 | **Location**: United States (Bellevue, WA lab + field sites)

## Executive Summary

**T-Mobile**, in partnership with **Nokia** and **NVIDIA**, has been conducting **AI-RAN field trials** since late 2025, exploring how to run AI workloads alongside 5G baseband processing on shared GPU infrastructure. The trials focus on **urban deployment scenarios** — dense cell sites in US metropolitan areas — where power, space, and thermal budgets are tight but AI opportunity is high.

T-Mobile's "Un-carrier" strategy emphasizes **rapid innovation cycles**, and the AI-RAN trials are a proving ground for:

- **Dynamic GPU partitioning** between 5G and edge AI services
- **Real-time video analytics** as a B2B edge AI service
- **Private 5G + AI inference** bundles for enterprise customers

---

## Background: T-Mobile's AI Strategy

T-Mobile has been aggressive about:

1. **5G Standalone (SA)** — Largest SA network in US (2025)
2. **Network AI** — Already using ML for SON (Self-Organizing Networks)
3. **Edge compute** — Exploring MEC partnerships
4. **Enterprise 5G** — Private 5G as a growth vector

AI-RAN fits into all four pillars — it's the **convergence point** of T-Mobile's existing AI, 5G SA, edge, and enterprise strategies.

---

## Trial Architecture

### Hardware Configuration

```
┌─────────────────────────────────────────────────────────┐
│  T-Mobile AI-RAN Trial Cell Site                        │
│                                                           │
│  Compute:                                                │
│  • NVIDIA ARC-Compact (L4 GPU, 72W, Grace CPU)         │
│  • Ruggedized outdoor enclosure (IP65)                  │
│  • Power budget: 300W total                              │
│                                                           │
│  Radio:                                                  │
│  • Nokia AirScale baseband (Aerial SDK)                 │
│  • Nokia AirScale RRH (3.5 GHz, 64T64R)                 │
│  • 5G NR SA, 100 MHz channel                            │
│                                                           │
│  AI Workloads:                                           │
│  • Video analytics (4 camera feeds)                     │
│  • NLP for customer service bot (edge)                  │
│  • Predictive maintenance (cell site telemetry)         │
└─────────────────────────────────────────────────────────┘
```

### GPU Partitioning Strategy

T-Mobile's partitioning is **time-aware + traffic-aware**:

| Condition | RAN Share | AI Share | Rationale |
|:---|:---|:---|:---|
| **Peak urban traffic** (5-8 PM) | 85% | 15% | RAN priority — urban density |
| **Business hours** (9 AM-5 PM) | 65% | 35% | Enterprise AI workloads |
| **Overnight** (12-6 AM) | 40% | 60% | Batch AI training |
| **Event mode** (concerts, sports) | 95% | 5% | AI essentially paused |

---

## Technical Innovations

### 1. Traffic-Aware Dynamic Partitioning

T-Mobile developed a **custom K8S scheduler plugin** that observes RAN load and adjusts AI workload allocation every 30 seconds:

```go
// traffic_aware_scheduler.go (simplified)
func (s *TrafficAwareScheduler) Rebalance() error {
    // Query RAN load from E2 telemetry
    ranLoad := s.e2Client.GetAggregateLoad()  // 0.0-1.0
    
    // Target: RAN always has headroom
    targetRanShare := math.Min(0.95, ranLoad + 0.20)  // +20% headroom
    targetAiShare := 1.0 - targetRanShare
    
    // Apply via GPU Operator's MIG reconfiguration
    return s.gpuOperator.SetPartition(targetRanShare, targetAiShare)
}
```

### 2. AI Workload Graceful Degradation

AI workloads in the trial are designed to **scale down gracefully** when RAN demands more GPU:

```python
# video_analytics.py — Adaptive workload
class VideoAnalyticsWorkload:
    def __init__(self, camera_feeds: List[CameraFeed]):
        self.feeds = camera_feeds
        self.current_fps = 30
        self.min_fps = 5  # Never drop below this
    
    def adapt_to_gpu_pressure(self, available_gpu_share: float):
        """Reduce workload proportionally to GPU availability."""
        if available_gpu_share > 0.35:
            # Full fidelity
            self.current_fps = 30
            self.process_all_cameras = True
        elif available_gpu_share > 0.20:
            # Reduced fidelity
            self.current_fps = 15
            self.process_all_cameras = True
        elif available_gpu_share > 0.10:
            # Minimal — only key cameras
            self.current_fps = 5
            self.process_all_cameras = False  # Only priority cameras
        else:
            # Pause
            self.current_fps = 0
```

### 3. B2B Edge AI as a Service

T-Mobile is testing a **new revenue model**: selling edge AI inference to nearby enterprise customers.

**Pilot customers**:
- **Retail mall** — Foot traffic analytics from outdoor cameras
- **Parking operator** — License plate recognition at street level
- **Construction site** — Safety monitoring (PPE detection)

**Pricing model** (trial):
- Per-GPU-hour: $0.50
- Egress: $0.05/GB
- SLA tiers: Best-effort (cheapest) vs. Guaranteed (premium)

---

## Results (Preliminary, 2026)

### Technical Metrics

| Metric | Baseline (RAN Only) | AI-RAN Shared | Delta |
|:---|:---|:---|:---|
| **RAN P99 latency** | 2.5 ms | 3.1 ms | +24% (within SLO) |
| **RAN throughput** | 2.8 Gbps | 2.7 Gbps | -3.5% |
| **GPU utilization** | 42% | 89% | +112% |
| **Power per bit** | 1.0x | 0.75x | -25% |
| **AI inference capacity** | N/A | 1400 inferences/min | New capability |

### Business Metrics

| Metric | Observation |
|:---|:---|
| **Pilot customer signups** | 7 enterprise customers in Bellevue trial |
| **Revenue uplift (pilot)** | 18% incremental revenue from AI services |
| **Customer NPS** | 68 (B2B customers report value) |
| **Churn** | 0% (all pilot customers extended) |

---

## Challenges Encountered

### Technical

1. **Power budget** — 300W cell site envelope limits GPU choice. L4 (72W) is tight when CPU, radio, cooling included.
2. **Thermal** — Seattle summer temps (35°C) pushed enclosure to thermal limits. Required fan upgrades.
3. **Network slicing** — B2B AI traffic must not compete with 5G user plane. Required strict SR-IOV QoS.
4. **Multi-tenancy** — Isolation between T-Mobile RAN, T-Mobile AI services, and third-party B2B workloads.

### Operational

1. **On-call model** — RAN NOC not trained on GPU issues; AI team not trained on RAN. Required cross-training.
2. **SLA definition** — "Best-effort" AI SLA confused B2B customers; needed clearer tiers.
3. **Data sovereignty** — B2B AI workloads processing sensitive video raised privacy questions.

---

## K8S Engineer Takeaways

If you're replicating this architecture:

1. **Start with static partitioning** — Dynamic is complex; validate static first
2. **Choose workloads carefully** — Only "shrinkable" AI workloads work well
3. **Invest in GPU observability** — DCGM Exporter + custom dashboards essential
4. **Define SLA tiers early** — Business model depends on clear SLAs
5. **Cross-train teams** — RAN and AI teams must understand each other's domain

---

## Timeline

| Date | Milestone |
|:---|:---|
| **Q3 2025** | Lab trials begin in Bellevue |
| **Q4 2025** | First field site deployed |
| **Q1 2026** | Pilot B2B customers onboarded |
| **Q2 2026** | 10 field sites active, 7 B2B customers |
| **H2 2026** | Planned commercial launch (TBD) |

---

## References

- [T-Mobile Un-carrier AI Strategy (2026)](https://www.t-mobile.com/news/)
- [Nokia + T-Mobile AI-RAN Collaboration](https://www.nokia.com/networks/our-customers/t-mobile/)
- [NVIDIA ARC for US Market](https://www.nvidia.com/en-us/industries/telecommunications/ai-ran/)
- [AI-RAN Alliance](https://ai-ran.org/)
