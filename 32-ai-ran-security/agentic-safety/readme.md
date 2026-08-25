---
title: "Agentic AI Safety for Autonomous RAN"
description: "> **Updated: 2026-05** | O-RAN WG11 Secure AI, IEEE CAI 2026 Agentic Safety Framework"
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-08-25"
keywords: ['O-RAN', 'AI-RAN', 'RIC']
---

# Agentic AI Safety for Autonomous RAN

> **Updated: 2026-05** | O-RAN WG11 Secure AI, IEEE CAI 2026 Agentic Safety Framework

## Overview

Agentic AI introduces a new threat category: **the AI itself can break the network**. Unlike traditional software bugs, agentic failures emerge from:

- **Hallucinated actions** that pass syntax validation but violate physics
- **Reasoning chains** that are logically consistent but operationally catastrophic
- **Multi-agent cascades** where one agent's "correct" action triggers another's failure
- **Confidence miscalibration** where the agent is highly confident about a wrong decision

This chapter defines the **defense-in-depth safety framework** for deploying agentic AI in O-RAN, aligned with the 2026 O-RAN WG11 Secure AI specifications and IEEE CAI 2026 guidelines.

---

## Safety Taxonomy for RAN Agents

### Failure Modes by Tier

| Tier | Agent Type | Typical Failure Mode | Blast Radius | Recovery Time |
|:---|:---|:---|:---|:---|
| **Tier 1** (Non-RT RIC) | Strategic LLM | Hallucinated policy that looks valid | Network-wide (hours) | Minutes (policy rollback) |
| **Tier 2** (Near-RT RIC) | Tactical DRL | Over-aggressive optimization | Multi-cell (minutes) | Seconds (fallback policy) |
| **Tier 3** (O-DU) | Reactive NN | Subframe-level violation | Single cell (subframe) | Milliseconds (hard bounds) |

### Safety Properties Required

1. **Bounded Autonomy** — Agent can only act within predefined parameter ranges
2. **Reversibility** — Every action must have an undo path
3. **Observability** — Every reasoning step must be logged
4. **Graceful Degradation** — Agent failure must not cause uncontrolled state
5. **Human Override** — Operator can interrupt any agent at any time

---

## Multi-Layer Safety Guardrails

### Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: Human-in-the-Loop Escalation                       │
│  • High-impact actions require operator approval            │
│  • Confidence < threshold → alert + hold                     │
│  • Novel scenarios → escalate to human                       │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Digital Twin Pre-Validation                        │
│  • Every action simulated before execution                   │
│  • Twin must predict positive outcome                        │
│  • Twin confidence score logged                              │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Policy Bounds (soft limits)                        │
│  • Rate limiting (max N actions per minute)                  │
│  • Change magnitude limits (max delta per step)              │
│  • Cross-agent conflict detection                            │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Safety Bounds (hard limits)                        │
│  • Regulatory limits (power, spectrum)                       │
│  • Hardware limits (tilt, thermal)                           │
│  • Cannot be overridden by AI                                │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Kill Switch (emergency stop)                       │
│  • Automated on KPI anomaly                                  │
│  • Manual operator trigger                                   │
│  • Fallback to last-known-good policies                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Automated Kill Switch

### Trigger Conditions

The kill switch engages automatically when any of the following are detected:

| Signal | Threshold | Detection Window |
|:---|:---|:---|
| **Drop rate spike** | > 5% increase in 60s | Real-time |
| **Throughput collapse** | < 50% baseline for 2 min | Rolling |
| **Safety bound violation** | Any hard limit exceeded | Instant |
| **Agent reasoning anomaly** | OOD reasoning pattern | Per-action |
| **Cross-tier cascade** | 3+ agents in alarm state | 30s |

### Kill Switch Implementation

```python
# kill_switch.py — Tier-agnostic emergency stop
class KillSwitch:
    def __init__(self, ric_client, policy_store, alertmanager):
        self.ric = ric_client
        self.policies = policy_store
        self.alerts = alertmanager
        self.armed = True
    
    def evaluate(self, signals: dict) -> bool:
        """Returns True if kill switch should engage."""
        if not self.armed:
            return False
        
        triggers = []
        if signals.get('drop_rate_delta_60s', 0) > 0.05:
            triggers.append('drop_rate_spike')
        if signals.get('throughput_ratio_2min', 1.0) < 0.5:
            triggers.append('throughput_collapse')
        if signals.get('safety_violation'):
            triggers.append('safety_bound_violated')
        if signals.get('reasoning_ood_score', 0) > 0.8:
            triggers.append('agent_anomaly')
        if signals.get('agents_in_alarm', 0) >= 3:
            triggers.append('cascade_detected')
        
        if triggers:
            self.engage(triggers)
            return True
        return False
    
    def engage(self, triggers: list):
        """Execute emergency shutdown sequence."""
        # 1. Stop all agentic pods
        self.ric.scale_deployment(
            namespace='non-rt-ric',
            deployment='strategic-agent',
            replicas=0
        )
        self.ric.scale_deployment(
            namespace='near-rt-ric',
            deployment='tactical-agent',
            replicas=0
        )
        
        # 2. Apply last-known-good policies
        last_good = self.policies.get_last_known_good()
        self.ric.apply_a1_policy(last_good)
        
        # 3. Alert operations team
        self.alerts.send(
            severity='critical',
            summary=f'AI agents terminated: {", ".join(triggers)}',
            runbook='https://wiki.internal/runbook/ai-kill-switch'
        )
```

### K8S Manifest for Kill Switch

```yaml
# kill-switch-controller.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kill-switch-controller
  namespace: oran-safety
spec:
  replicas: 2  # HA — kill switch must not be single point of failure
  selector:
    matchLabels:
      app: kill-switch
  template:
    metadata:
      labels:
        app: kill-switch
    spec:
      priorityClassName: system-cluster-critical  # Never evicted
      containers:
      - name: controller
        image: oran/kill-switch:2026.1
        env:
        - name: KILL_SWITCH_ARMED
          value: "true"
        - name: METRICS_SOURCE
          value: "prometheus:http://prometheus.monitoring:9090"
        - name: POLICY_STORE
          value: "redis://policy-store.oran-safety:6379"
        resources:
          requests:
            cpu: "500m"
            memory: "256Mi"
          limits:
            cpu: "1"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          periodSeconds: 5  # Aggressive — kill switch must be alive
```

---

## Layer 2: Hard Safety Bounds

### Principle

Hard bounds are **physically enforced** and **cannot be overridden by any AI agent**, including Tier 1 strategic agents. They are implemented at the lowest possible layer (Tier 3 / O-DU) to prevent upstream corruption.

### Configuration Schema

```yaml
# safety-bounds-crd.yaml
apiVersion: safety.oran.io/v1
kind: SafetyBounds
metadata:
  name: cell-site-001
spec:
  radio:
    max_power_dbm: 46.0              # Regulatory (FCC/CE)
    min_power_dbm: 10.0              # Hardware floor
    max_power_change_db_per_min: 3.0 # Prevent rapid swings
    forbidden_bands:                  # Licensed spectrum
    - "3.7-3.98 GHz"                 # (example C-band exclusion)
  
  mechanical:
    max_tilt_deg: 15.0
    min_tilt_deg: -5.0
    max_tilt_change_deg_per_hour: 5.0  # Motor wear limit
    max_azimuth_change_deg_per_hour: 10.0
  
  rf_safety:
    max_e_field_v_per_m: 61.0        # ICNIRP 2026 public limit
    enforced_exclusion_zone_m: 10.0
  
  operational:
    max_handover_rate_per_min: 10
    max_sleep_mode_transitions_per_hour: 4
    min_active_carriers: 1            # Never go fully dark
  
  enforcement:
    layer: "o-du"                     # Enforced at Tier 3
    bypass_allowed: false
    audit_log: true
```

### Enforcement Code (Tier 3 Reactive Agent)

```python
# reactive_safety.py — Runs in O-DU sidecar, cannot be bypassed
class ReactiveSafetyChecker:
    def __init__(self, bounds: SafetyBounds):
        self.bounds = bounds
        self.violation_counter = Counter()
    
    def validate(self, command: RadioCommand) -> ValidationResult:
        """Validate a radio command against hard bounds.
        This runs in the data path — must be <100us."""
        violations = []
        
        # Power checks
        if command.power_dbm > self.bounds.radio.max_power_dbm:
            violations.append(f"power_exceeds_max: {command.power_dbm}")
        if command.power_dbm < self.bounds.radio.min_power_dbm:
            violations.append(f"power_below_min: {command.power_dbm}")
        
        # Rate of change checks
        power_delta = abs(command.power_dbm - self._last_power_dbm)
        if power_delta > self.bounds.radio.max_power_change_db_per_min:
            violations.append(f"power_change_too_fast: {power_delta}")
        
        # Tilt checks
        if not (self.bounds.mechanical.min_tilt_deg <= command.tilt_deg <= self.bounds.mechanical.max_tilt_deg):
            violations.append(f"tilt_out_of_range: {command.tilt_deg}")
        
        # Band checks
        if command.frequency_hz in self.bounds.radio.forbidden_bands:
            violations.append(f"forbidden_band: {command.frequency_hz}")
        
        if violations:
            self.violation_counter.update(violations)
            return ValidationResult(
                allowed=False,
                violations=violations,
                action='reject_and_alert'
            )
        
        self._last_power_dbm = command.power_dbm
        return ValidationResult(allowed=True)
```

---

## Layer 3: Policy Bounds (Soft Limits)

### Rate Limiting

Rate limits prevent agents from overwhelming the system or executing runaway action sequences.

```python
# rate_limiter.py — Token bucket per action type
class ActionRateLimiter:
    def __init__(self):
        self.buckets = {
            'power_change': TokenBucket(rate=10, capacity=20),     # 10/min, burst 20
            'handover': TokenBucket(rate=5, capacity=10),          # 5/min
            'cell_sleep': TokenBucket(rate=1, capacity=3),         # 1/min
            'tilt_change': TokenBucket(rate=0.1, capacity=2),      # 6/hour
            'a1_policy_publish': TokenBucket(rate=2, capacity=5),  # 2/min
        }
    
    def allow(self, action_type: str, agent_id: str) -> bool:
        bucket = self.buckets.get(action_type)
        if not bucket:
            return False  # Unknown action type → deny by default
        if not bucket.consume():
            metrics.rate_limit_hits.labels(action_type, agent_id).inc()
            return False
        return True
```

### Change Magnitude Limits

Even within rate limits, each individual action must not change too much too fast.

```python
class ChangeMagnitudeChecker:
    """Prevents 'death by a thousand cuts' — many small changes
    that individually pass but collectively destabilize."""
    
    def __init__(self, window_minutes: int = 10):
        self.window = window_minutes
        self.history: Deque[Action] = deque()
    
    def check(self, action: Action) -> bool:
        self.history.append(action)
        self._prune_old()
        
        # Sum of power changes in window
        total_power_delta = sum(
            abs(a.power_delta_db) for a in self.history
            if a.type == 'power_change'
        )
        if total_power_delta > 10.0:  # Max 10dB swing per 10 min
            return False
        
        # Number of distinct cells touched
        cells_affected = len({a.cell_id for a in self.history})
        if cells_affected > 20 and len(self.history) > 50:
            return False  # Too much breadth
        
        return True
```

### Cross-Agent Conflict Detection

When multiple agents act on overlapping resources, their actions may conflict.

```python
class ConflictDetector:
    def __init__(self, resource_graph: ResourceGraph):
        self.graph = resource_graph
        self.pending_actions: Dict[str, Action] = {}
    
    def check_conflict(self, new_action: Action) -> Optional[Conflict]:
        # Find all actions in flight that touch overlapping resources
        overlapping = [
            a for a in self.pending_actions.values()
            if self.graph.overlaps(a.resources, new_action.resources)
        ]
        
        for existing in overlapping:
            if self._are_conflicting(existing, new_action):
                return Conflict(
                    action_a=existing,
                    action_b=new_action,
                    reason=self._explain_conflict(existing, new_action)
                )
        return None
    
    def _are_conflicting(self, a: Action, b: Action) -> bool:
        # Example conflicts:
        # - Both trying to change same cell's power in opposite directions
        # - One putting cell to sleep while other hands UEs to it
        # - Both trying to tilt same antenna simultaneously
        if a.cell_id == b.cell_id:
            if a.type == 'power_down' and b.type == 'handover_to':
                return True  # Can't handover to cell being powered down
            if a.type == 'tilt_change' and b.type == 'tilt_change':
                return True  # Mechanical conflict
        return False
```

---

## Layer 4: Digital Twin Pre-Validation

### Validation Workflow

```
Agent proposes action
        ↓
Query digital twin for current state
        ↓
Twin simulates action (fast-forward 60s of network time)
        ↓
Twin predicts KPIs after action
        ↓
Check: Are all predicted KPIs within bounds?
        ↓ YES → Execute with monitoring
        ↓ NO  → Reject and escalate
```

### Implementation

```python
# twin_validator.py — Pre-validates actions against AODT
class DigitalTwinValidator:
    def __init__(self, aodt_client: AODTClient):
        self.twin = aodt_client
        self.min_confidence = 0.7  # Twin must be confident
        self.max_simulation_time_s = 5.0  # Don't block too long
    
    def validate(self, action: Action, current_state: NetworkState) -> TwinVerdict:
        try:
            # Run simulation in twin (60s of network time, compressed to <5s wall time)
            with timeout(self.max_simulation_time_s):
                predicted_state = self.twin.simulate(
                    initial_state=current_state,
                    action=action,
                    duration_s=60
                )
            
            # Check KPIs
            violations = []
            for kpi, expected in predicted_state.kpis.items():
                bound = self._kpi_bounds(kpi)
                if expected.value < bound.min or expected.value > bound.max:
                    violations.append(f"{kpi}={expected.value} out of [{bound.min}, {bound.max}]")
            
            # Check twin confidence
            if predicted_state.confidence < self.min_confidence:
                return TwinVerdict(
                    approved=False,
                    reason=f"twin_low_confidence: {predicted_state.confidence}",
                    escalate=True
                )
            
            if violations:
                return TwinVerdict(
                    approved=False,
                    reason=f"kpi_violations: {violations}",
                    predicted_state=predicted_state
                )
            
            return TwinVerdict(approved=True, predicted_state=predicted_state)
        
        except TimeoutError:
            # If twin is too slow, fail safe
            return TwinVerdict(
                approved=False,
                reason="twin_timeout",
                escalate=True
            )
```

### Twin Freshness Monitoring

A stale twin gives stale predictions. This was the **root cause of the hypothetical stadium incident** (see Chapter 32 overview).

```python
class TwinFreshnessMonitor:
    """Alerts when digital twin diverges from reality."""
    
    def __init__(self, twin: AODTClient, live_telemetry: TelemetryClient):
        self.twin = twin
        self.live = live_telemetry
        self.max_divergence = 0.15  # 15% max KPI divergence
    
    def check_freshness(self) -> FreshnessReport:
        # Get current live KPIs
        live_kpis = self.live.get_current_kpis()
        
        # Ask twin what it thinks current state is (no action)
        twin_kpis = self.twin.get_predicted_current_kpis()
        
        divergences = {}
        for kpi, live_value in live_kpis.items():
            twin_value = twin_kpis.get(kpi)
            if twin_value is None:
                continue
            divergence = abs(live_value - twin_value) / max(live_value, 1e-6)
            divergences[kpi] = divergence
        
        max_div = max(divergences.values()) if divergences else 0
        stale = max_div > self.max_divergence
        
        return FreshnessReport(
            stale=stale,
            max_divergence=max_div,
            divergences=divergences,
            recommendation='retrain' if stale else 'ok'
        )
```

---

## Layer 5: Human-in-the-Loop Escalation

### Escalation Matrix

Not every action needs human approval. The escalation policy is based on **impact × reversibility × novelty**.

| Impact | Reversibility | Novelty | Escalation |
|:---|:---|:---|:---|
| Low (single cell) | High (instant undo) | Known pattern | Auto-execute |
| Medium (multi-cell) | Medium (minutes to undo) | Known pattern | Auto + audit |
| High (network-wide) | Low (hours to undo) | Known pattern | Notify + 5 min hold |
| Any | Any | **Novel** (OOD) | Block + human approval |
| Critical (safety-adjacent) | Any | Any | Block + human approval |

### Escalation Service

```python
# escalation_service.py
class EscalationService:
    def __init__(self, oncall_client: OncallClient, policy: EscalationPolicy):
        self.oncall = oncall_client
        self.policy = policy
    
    def should_escalate(self, action: Action, context: ActionContext) -> bool:
        impact = self._assess_impact(action)
        reversibility = self._assess_reversibility(action)
        novelty = self._assess_novelty(action, context)
        
        # Novel scenarios always escalate
        if novelty == 'out_of_distribution':
            return True
        
        # Critical safety-adjacent always escalates
        if action.touches_safety_bounds():
            return True
        
        # High-impact + low-reversibility escalates
        if impact == 'high' and reversibility == 'low':
            return True
        
        return False
    
    def request_approval(self, action: Action, timeout_s: int = 300) -> ApprovalResult:
        """Send approval request to oncall engineer."""
        ticket = self.oncall.create_ticket(
            severity='high',
            summary=f"AI agent requests approval for: {action.summary}",
            body=self._render_ticket_body(action),
            timeout_s=timeout_s
        )
        
        # Wait for approval or timeout
        result = ticket.wait_for_decision()
        
        if result == 'timeout':
            # Default deny on timeout — fail safe
            return ApprovalResult(approved=False, reason="approval_timeout")
        return ApprovalResult(approved=(result == 'approved'))
```

---

## Audit Logging and Explainability

### What Must Be Logged

Every agent action produces an **audit record** with:

```json
{
  "timestamp": "2026-05-23T14:23:15.123Z",
  "agent_id": "strategic-agent-7f8d9",
  "agent_tier": "tier1",
  "trace_id": "abc-123-def",
  "observation": {
    "cell_id": "cell-007",
    "kpi_snapshot": {"throughput_mbps": 850, "drop_rate": 0.012}
  },
  "reasoning_chain": [
    {"step": 1, "thought": "Throughput below target for VIP slice", "tool_called": null},
    {"step": 2, "thought": "Need to diagnose cause", "tool_called": "query_kpis"},
    {"step": 3, "thought": "PRB utilization at 95%, interference normal", "tool_called": null},
    {"step": 4, "thought": "Need more capacity — consider activating sleeping cell", "tool_called": null},
    {"step": 5, "thought": "Pre-validate with digital twin", "tool_called": "simulate_action"}
  ],
  "decision": {
    "action": "activate_sleeping_cell",
    "target": "cell-008",
    "confidence": 0.87,
    "predicted_outcome": "+180 Mbps, -0.3% drop rate"
  },
  "safety_checks": {
    "bounds_check": "pass",
    "rate_limit": "pass",
    "conflict_check": "pass",
    "twin_validation": "pass (confidence 0.82)"
  },
  "execution": {
    "executed": true,
    "outcome_observed": "+165 Mbps, -0.2% drop rate",
    "outcome_within_prediction": true
  }
}
```

### Audit Pipeline

```
Agent Pod
    ↓ (structured JSON logs)
Sidecar: fluent-bit
    ↓
Kafka Topic: agent-audit-logs
    ↓
Flink Job: enrich + index
    ↓
┌───────────┬──────────────┐
│           │              │
Elasticsearch  TimescaleDB   S3 (immutable archive)
(for search)   (for metrics) (for compliance, 7 years)
    ↓
Grafana + Kibana (operator dashboard)
```

### K8S Audit Sidecar

```yaml
# audit-sidecar.yaml — Injected into every agent pod
apiVersion: v1
kind: ConfigMap
metadata:
  name: audit-sidecar-config
data:
  fluent-bit.conf: |
    [INPUT]
        Name tail
        Path /var/log/agent/audit.json
        Parser json
        Tag agent.audit
    
    [FILTER]
        Name modify
        Match agent.audit
        Add cluster ${CLUSTER_NAME}
        Add agent_tier ${AGENT_TIER}
    
    [OUTPUT]
        Name kafka
        Match agent.audit
        Brokers kafka.strimzi.svc:9092
        Topics agent-audit-logs
        format json
```

---

## O-RAN WG11 Compliance Checklist (2026)

### Mandatory for Production Deployment

- [ ] **SBOM for AI models** — All model versions tracked with Software Bill of Materials
- [ ] **Model signing** — Cryptographic signature on all loaded models
- [ ] **Hard safety bounds enforced at Tier 3** — Cannot be bypassed by upstream
- [ ] **Kill switch tested quarterly** — Automated drill with production-adjacent traffic
- [ ] **Audit logs retained 7 years** — Immutable storage, tamper-evident
- [ ] **Twin freshness monitored** — Alert when divergence > threshold
- [ ] **Rate limiting active** — Per-agent, per-action-type
- [ ] **Human-in-the-loop escalation path** — 24/7 oncall reachable within 5 min
- [ ] **Fallback policies pre-staged** — Last-known-good always available
- [ ] **Drill: agent hallucination scenario** — Annual red-team exercise

---

## Quick Wins for K8S Engineers

### Implement Today

1. **Add kill switch Deployment** — 2 replicas, priority class `system-cluster-critical`
2. **Deploy audit sidecar** — Fluent-bit → Kafka for every agent pod
3. **Define SafetyBounds CRD** — Version-control hard limits in Git
4. **Set up rate limiting** — Token bucket per action type, Redis-backed
5. **Configure alerts** — Kill switch engagement, safety bound violations, twin staleness

### Implement This Quarter

1. **Digital twin integration** — AODT or open-source equivalent
2. **Conflict detector** — Graph-based resource overlap analysis
3. **Escalation service** — PagerDuty/OpsGenie integration
4. **Audit dashboard** — Kibana index pattern for `agent.audit.*`

---

## References

- [O-RAN WG11 O-R005 v03.00: Secure AI/ML Workflow](https://www.o-ran.org/specifications)
- [IEEE CAI 2026: Agentic AI Safety in 6G](https://www.ieeesmc.org/cai-2026/tutorial-1-agentic-ai-ai-ran-ai-core-networks-and-future-6g/)
- [NIST AI Risk Management Framework (AI RMF 1.0)](https://www.nist.gov/artificial-intelligence/executive-order-safe-secure-and-trustworthy-ai)
- [Anthropic: Building Safe Agentic Systems](https://www.anthropic.com/engineering/building-effective-agents)
- [SPIFFE/SPIRE for Workload Identity](https://spiffe.io/)
