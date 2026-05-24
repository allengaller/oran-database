# AI-RAN Papers 2026 — Comprehensive Index

> **Updated: 2026-05** | Papers on AI-RAN convergence, 6G AI-native, and agentic RAN

## Overview

This directory indexes the **most significant papers on AI-RAN** published in 2025-2026, organized by technical theme. Each entry includes full citation, abstract, key contributions, and links to deep dives where available.

**Purpose**: Help K8S engineers and researchers navigate the rapidly evolving AI-RAN literature and identify papers relevant to production work.

---

## Table of Contents

1. [Landmark Papers](#landmark-papers)
2. [Agentic AI in RAN](#agentic-ai-in-ran)
3. [Digital Twin](#digital-twin)
4. [6G AI-Native](#6g-ai-native)
5. [DRL for RAN](#drl-for-ran)
6. [Graph Neural Networks](#graph-neural-networks)
7. [LLMs for Telecom](#llms-for-telecom)
8. [Federated Learning](#federated-learning)
9. [Security](#security)
10. [Post-Quantum Cryptography](#post-quantum-cryptography)
11. [Case Studies](#case-studies)

---

## Landmark Papers

### ⭐ Toward Autonomous O-RAN: A Multi-Scale Agentic AI Framework

**Citation**: arXiv:2602.14117v1, February 2026
**Authors**: (Academic consortium)
**Source**: [arxiv.org/html/2602.14117v1](https://arxiv.org/html/2602.14117v1)

**Abstract**: Introduces a three-tier hierarchical framework for deploying agentic AI across O-RAN — Strategic (Non-RT RIC, >1s, LLM), Tactical (Near-RT RIC, 10ms-1s, DRL), Reactive (O-DU, <10ms, cuMAC).

**Why It Matters**: This is the **foundational paper** for agentic AI in O-RAN. The 3-tier architecture is now becoming the reference design for autonomous RAN.

**Deep Dive**: [Read full analysis](../../31-ai-ran-convergence/paper-deep-dive/arxiv-2602-14117.md)

---

### ⭐ AI for Next-Generation 6G Technologies and Networks

**Citation**: Springer Wireless Networks, February 2026
**DOI**: 10.1007/s44354-026-00016-3
**Source**: [Springer](https://link.springer.com/article/10.1007/s44354-026-00016-3)

**Abstract**: Comprehensive survey of AI-native 6G design principles. Argues that 6G is "not a new radio technology; it's a new AI architecture that uses radio as one modality."

**Why It Matters**: Most authoritative 6G AI survey. Covers THz, semantic comm, PINNs, federated intelligence.

**Deep Dive**: [Read full analysis](../../31-ai-ran-convergence/paper-deep-dive/springer-6g-ai.md)

---

### ⭐ AI-RAN: The Pathway to Future Wireless Networks

**Citation**: ICT Express (ScienceDirect), 2026
**DOI**: S2949715926000016
**Source**: [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2949715926000016)

**Abstract**: Establishes the **dual AI paradigm** (AI-for-RAN + AI-on-RAN) and proposes the 4-layer architecture (Reactive/Tactical/Strategic/Service).

**Why It Matters**: First paper to clearly articulate the **business case** for AI-RAN.

**Deep Dive**: [Read full analysis](../../31-ai-ran-convergence/paper-deep-dive/sciencedirect-2026.md)

---

### ⭐ AI-Based Resource Management for O-RAN: A Comprehensive Survey

**Citation**: Ad Hoc Networks (ScienceDirect), April 2026
**DOI**: S1570870526001307
**Source**: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1570870526001307)

**Abstract**: Reviews 300+ papers on AI-based RAN resource management. Provides taxonomy of AI techniques for each resource type.

**Why It Matters**: The **reference survey** for AI resource management. Essential for algorithm selection.

**Deep Dive**: [Read full analysis](../../31-ai-ran-convergence/paper-deep-dive/sciencedirect-survey-2026.md)

---

## Agentic AI in RAN

### LLM-Based Agents for Telecom Networks

**Citation**: IEEE Communications Surveys & Tutorials, Q1 2026
**Authors**: (Various academic + industry)
**Focus**: Survey of LLM applications in telecom operations (intent translation, RCA, planning)

**Key Contributions**:
- Taxonomy of LLM agent architectures (ReAct, tool-use, multi-agent)
- Benchmark comparison of telecom-tuned LLMs
- Safety frameworks for agentic deployment

---

### Safety Guardrails for Autonomous RAN Agents

**Citation**: IEEE CAI 2026 Conference
**Focus**: Multi-layer safety framework for agentic AI (digital twin, rate limiting, kill switches)

**Key Contributions**:
- 5-layer safety architecture (matches Chapter 32 of this knowledge base)
- Empirical evaluation of kill switch strategies
- Real-world incident case studies

---

### Multi-Agent Coordination in RIC

**Citation**: ACM SIGCOMM Workshop on AI-RAN 2026
**Focus**: How multiple xApps/rApps coordinate without conflict

**Key Contributions**:
- Conflict detection via resource graphs
- Coordination protocols between tiers
- Evaluation in 50-cell testbed

---

## Digital Twin

### NVIDIA AI Open Digital Twin (AODT): Architecture and Applications

**Citation**: NVIDIA Technical Report, February 2026
**Source**: [NVIDIA Developer](https://developer.nvidia.com/aodt)

**Abstract**: Introduces AODT architecture, APIs, and integration patterns. Hosted on AWS.

**Key Contributions**:
- Full AODT API reference
- Case studies: 5 operators using AODT
- Performance benchmarks (simulation speed, accuracy)

---

### 6G-TWIN: Physics-Informed Digital Twin for Terahertz Networks

**Citation**: IEEE Transactions on Wireless Communications, 2026
**Focus**: Ray-tracing based THz digital twin with ML residual correction

**Key Contributions**:
- THz channel modeling (100-300 GHz)
- Physics-informed ML for path loss prediction
- 10x faster than pure ray-tracing

---

### Digital Twin Freshness Monitoring

**Citation**: IEEE INFOCOM 2026 Workshop
**Focus**: Detecting when digital twin has drifted from reality

**Key Contributions**:
- Drift detection algorithms
- Auto-calibration techniques
- Real-world validation (3 operators)

---

## 6G AI-Native

### Terahertz Beam Prediction Using Graph Neural Networks

**Citation**: IEEE JSAC (Journal on Selected Areas in Communications), 2026
**Focus**: GNN-based beam prediction for 140 GHz THz channels

**Key Contributions**:
- 30% faster beam alignment vs. classical codebook
- Works with imperfect CSI
- Real-time inference (<1ms)

---

### Semantic Communication for 6G: A Survey

**Citation**: IEEE Communications Surveys & Tutorials, 2026
**Focus**: Transmitting meaning, not bits — for 100x data rate reduction

**Key Contributions**:
- Taxonomy of semantic encoders
- Perceptual quality metrics (LPIPS, FID)
- 10x compression vs. H.265 with comparable quality

---

### Physics-Informed Neural Networks for Wireless Channel Modeling

**Citation**: IEEE Transactions on Antennas and Propagation, 2026
**Focus**: Embedding Maxwell's equations into neural networks

**Key Contributions**:
- 10x less training data required vs. pure ML
- Extrapolates to unseen scenarios
- Interpretable via physics loss decomposition

---

## DRL for RAN

### PPO for Single-Cell Scheduling: A Practical Guide

**Citation**: IEEE OJ-COMM (Open Journal), 2025
**Focus**: Practical implementation of PPO for 5G NR scheduling

**Key Contributions**:
- Hyperparameter tuning guide
- Comparison with classical proportional-fair
- Open-source reference implementation

---

### Multi-Agent DRL for Multi-Cell Interference Coordination

**Citation**: IEEE TWC, 2026
**Focus**: MAPPO for coordinated multi-cell scheduling

**Key Contributions**:
- +22% throughput vs. single-agent DRL
- Scales to 100+ cells
- Communication overhead analysis

---

### Safe DRL with Hard Bounds for Power Control

**Citation**: NeurIPS 2025 Workshop on Safe AI
**Focus**: Constrained PPO with hard safety limits

**Key Contributions**:
- Safety layer that cannot be bypassed
- Empirical validation on 5G power control
- Formal safety guarantees

---

## Graph Neural Networks

### GNN-Based Handover Prediction in Dense Urban

**Citation**: IEEE TMC, 2026
**Focus**: Predicting handover events using graph attention networks

**Key Contributions**:
- -40% ping-pong vs. A3 event
- Real-time inference (<5ms)
- Handles variable topology

---

### Scene-Graph Beam Prediction for mmWave

**Citation**: ACM MobiCom 2025
**Focus**: GNN over scene graph (UE + scatterers + BS) for 28 GHz

**Key Contributions**:
- Works with blocked LoS
- 95% accuracy on top-3 beams
- Robust to environment changes

---

## LLMs for Telecom

### Qwen2.5-7B-Telecom: A Telecom-Tuned SLM

**Citation**: Alibaba Technical Report, 2025
**Source**: [Qwen GitHub](https://github.com/QwenLM/Qwen)

**Abstract**: 7B-parameter SLM fine-tuned on telecom corpus (3GPP specs, operator logs, RAN documentation)

**Key Contributions**:
- 85% accuracy on telecom QA benchmark
- 3x better than base Qwen on RCA tasks
- Open-source (Apache 2.0)

---

### ReAct Agents for Network Operations Center

**Citation**: IEEE NOMS 2026
**Focus**: LLM agents with tool use for NOC automation

**Key Contributions**:
- ReAct pattern applied to RCA
- 8 tool integrations (TimesFM, GNN, E2, etc.)
- Real operator case study

---

### Prompt Engineering for 3GPP Spec Understanding

**Citation**: IEEE ICC 2026 Workshop on LLM for Telecom
**Focus**: How to prompt LLMs to understand 3GPP specifications

**Key Contributions**:
- 3GPP-specific prompting techniques
- RAG over spec corpus
- Evaluation on TS 38.300 questions

---

## Federated Learning

### Flower: A Friendly Federated Learning Framework

**Citation**: MLSys 2025
**Source**: [flower.dev](https://flower.dev/)

**Abstract**: General-purpose FL framework used in telecom research and production

**Key Contributions**:
- 100+ telecom use cases documented
- Supports PyTorch, TensorFlow, JAX
- Cross-silo and cross-device FL

---

### Cross-Operator Handover Model Training

**Citation**: IEEE TMC, 2026
**Focus**: 5 operators jointly train handover prediction without sharing data

**Key Contributions**:
- +40% model quality vs. siloed training
- Privacy analysis (GDPR compliance)
- Communication overhead: 100x less than raw data

---

### NVIDIA FLARE for Secure Federated Learning

**Citation**: NVIDIA Technical Report, 2025
**Focus**: Production-grade FL framework with security features

**Key Contributions**:
- mTLS between FL clients and server
- Secure aggregation (Krum, Bulyan)
- Deployed in 3 operators (production)

---

## Security

### O-RAN WG11 Secure AI Specification (O-R005 v03.00)

**Citation**: O-RAN Alliance, 2026
**Source**: [O-RAN Specs](https://www.o-ran.org/specifications)

**Abstract**: Official specification for securing AI/ML workflows in O-RAN

**Key Contributions**:
- Safety bound enforcement
- Audit logging requirements
- Kill switch guidelines

---

### Adversarial Attacks on DRL-Based RAN Controllers

**Citation**: IEEE S&P (Security and Privacy) 2026
**Focus**: FGSM and PGD attacks on DRL power control

**Key Contributions**:
- Attack success rate analysis
- Defense techniques (adversarial training, input validation)
- Real-world attack demonstration

---

### Zero Trust Architecture for AI-RAN

**Citation**: IEEE CAI 2026 Tutorial
**Source**: [IEEE CAI](https://www.ieeesmc.org/cai-2026/tutorial-1-agentic-ai-ai-ran-ai-core-networks-and-future-6g/)

**Abstract**: Applying NIST SP 800-207 Zero Trust principles to AI-RAN

**Key Contributions**:
- SPIFFE/SPIRE for agent identity
- OPA for policy-as-code
- Real-world deployment case study

---

## Post-Quantum Cryptography

### NIST FIPS 203: ML-KEM (Kyber)

**Citation**: NIST, 2024
**Source**: [NIST](https://csrc.nist.gov/pubs/fips/203/final)

**Abstract**: Post-quantum key encapsulation mechanism

**Key Contributions**:
- Standard for TLS 1.3 hybrid mode
- Performance benchmarks
- Integration guide

---

### NIST FIPS 204: ML-DSA (Dilithium)

**Citation**: NIST, 2024
**Source**: [NIST](https://csrc.nist.gov/pubs/fips/204/final)

**Abstract**: Post-quantum digital signature algorithm

**Key Contributions**:
- Standard for A1 policy signing
- Compact signatures (2.4-4.6 KB)
- Fast verification

---

### O-RAN WG11 Post-Quantum Migration Guide (O-R006 v02.00)

**Citation**: O-RAN Alliance, 2026
**Source**: [O-RAN Specs](https://www.o-ran.org/specifications)

**Abstract**: Migration roadmap from classical to PQC for O-RAN interfaces

**Key Contributions**:
- 4-phase migration (2026-2030)
- Hybrid TLS deployment guide
- Inventory and crypto-agility patterns

---

## Case Studies

### SoftBank AI-RAN Whitepaper

**Citation**: SoftBank, December 2024
**Source**: [SoftBank](https://www.softbank.jp/corp/set/data/technology/research/story-event/ai-ran)

**Abstract**: SoftBank's vision for AI-RAN cell sites as multi-purpose platforms

**Key Contributions**:
- Time-aware GPU partitioning model
- B2B edge AI service pricing
- 2026 commercial launch plan

**Case Study**: [Read full analysis](../../31-ai-ran-convergence/case-studies/softbank.md)

---

### Nokia + NVIDIA MWC 2026 Live Demo

**Citation**: MWC Barcelona 2026
**Source**: [NVIDIA Blog](https://blogs.nvidia.com/blog/software-defined-ai-ran/)

**Abstract**: First public demo of AI-with-RAN (baseband + AI on same GPU)

**Key Contributions**:
- 3 scenarios (normal, traffic spike, off-peak)
- Quantitative results (throughput, latency, power)
- Live operator-like environment

**Case Study**: [Read full analysis](../../31-ai-ran-convergence/case-studies/nokia-nvidia-mwc.md)

---

### Elisa (Finland) AI-RAN Field Trials

**Citation**: Elisa, 2026
**Source**: [Elisa](https://elisa.fi/en/ai-ran)

**Abstract**: Commercial-grade autonomous RAN deployment in Helsinki

**Key Contributions**:
- LLM-based NOC assistant
- 30% energy reduction with AI
- 40% reduction in truck rolls

**Case Study**: [Read full analysis](../../31-ai-ran-convergence/case-studies/elisa.md)

---

### SynaXG + Eridan: 6G AI-Native Radio

**Citation**: SynaXG + Eridan, 2025
**Source**: [SynaXG](https://www.synaxg.com/)

**Abstract**: AI-native PHY for THz (140 GHz) using GNN + Transformer

**Key Contributions**:
- 30% faster beam alignment
- 22% power reduction
- First commercial 6G AI-native radio

**Case Study**: [Read full analysis](../../31-ai-ran-convergence/case-studies/synaxg-eridan.md)

---

### LITEON DGX Spark for Telecom (GTC 2026)

**Citation**: LITEON, GTC 2026
**Source**: [LITEON](https://www.liteon.com/)

**Abstract**: Production-grade AI-RAN edge compute platform

**Key Contributions**:
- NEBS Level 3 certified
- -48V DC, ruggedized
- Pre-validated with multiple O-DU vendors

**Case Study**: [Read full analysis](../../31-ai-ran-convergence/case-studies/liteon-gtc.md)

---

### VIAVI + NVIDIA: Digital Twin Test Integration

**Citation**: VIAVI + NVIDIA, 2025-2026
**Source**: [VIAVI](https://www.viavisolutions.com/)

**Abstract**: Integrated test and digital twin platform for AI-RAN validation

**Key Contributions**:
- TM500 UE emulator + AODT integration
- NITRO test automation
- Compliance artifact generation

**Case Study**: [Read full analysis](../../31-ai-ran-convergence/case-studies/viava-nvidia.md)

---

## Related Resources

- [31-ai-ran-convergence chapter](../../31-ai-ran-convergence/) — Full AI-RAN coverage
- [32-ai-ran-security chapter](../../32-ai-ran-security/) — Security for AI-RAN
- [07-ric-development](../../07-ric-development/) — RIC and xApp/rApp development
- [15-future-development](../../15-future-development/) — 6G future

---

## Contributing

To add new papers to this index:

1. Ensure paper is published in 2025-2026
2. Must be relevant to AI-RAN convergence
3. Prefer peer-reviewed publications (IEEE, ACM, Springer)
4. Include full citation, abstract, and link
5. Add deep dive in `31-ai-ran-convergence/paper-deep-dive/` for landmark papers
6. Update this README with new entry

---

## References

- [arXiv.org](https://arxiv.org/) — Preprints
- [IEEE Xplore](https://ieeexplore.ieee.org/) — IEEE publications
- [ACM Digital Library](https://dl.acm.org/) — ACM publications
- [SpringerLink](https://link.springer.com/) — Springer publications
- [ScienceDirect](https://www.sciencedirect.com/) — Elsevier publications
- [O-RAN Alliance](https://www.o-ran.org/specifications) — Official specs
