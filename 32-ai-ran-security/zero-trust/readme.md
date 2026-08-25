---
title: "Zero Trust Architecture for AI-RAN"
description: "> **Updated: 2026-05** | O-RAN WG11 ZTA Priority, NIST SP 800-207, SPIFFE/SPIRE, OPA/Cedar"
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-08-25"
keywords: ['O-RAN', 'AI-RAN', 'RIC']
---

# Zero Trust Architecture for AI-RAN

> **Updated: 2026-05** | O-RAN WG11 ZTA Priority, NIST SP 800-207, SPIFFE/SPIRE, OPA/Cedar

## Overview

**Zero Trust** is the foundational security model for AI-RAN. The principle is simple: **never trust, always verify**. In an AI-RAN environment with autonomous agents, multi-tenant edge sites, and cross-tier communication, traditional perimeter security is insufficient. Every agent, every message, every workload must be **continuously authenticated and authorized**.

O-RAN WG11 has made **Zero Trust Architecture (ZTA)** a **top priority for 2026**, recognizing that:

- **AI agents are workloads** that need identity and authorization
- **Cross-vendor components** (RIC, xApps, O-DU, O-RU) cannot implicitly trust each other
- **Edge cell sites** are physically unsecured and must authenticate into the central RIC
- **Autonomous actions** must be policy-gated with explicit allow rules

This chapter applies **NIST SP 800-207 Zero Trust Architecture** principles to AI-RAN, using **SPIFFE/SPIRE for workload identity**, **OPA/Cedar for policy-as-code**, and **K8S-native primitives** for enforcement.

---

## Zero Trust Principles for AI-RAN

### The Seven NIST Tenets (Applied to RAN)

| NIST Tenet | AI-RAN Application |
|:---|:---|
| **1. All data sources and computing services are considered resources** | Every agent, RIC component, O-DU, Kafka topic |
| **2. All communication is secured regardless of network location** | mTLS on E2, A1, O1, O2 — even within cluster |
| **3. Access to individual resources is granted per-session** | Agent auth is per-action, not per-deployment |
| **4. Resource access is determined by dynamic policy** | Policy-as-code (OPA) evaluates every request |
| **5. The enterprise monitors and measures the integrity and security posture** | Continuous verification of agent behavior |
| **6. All resource authentication and authorization are dynamic and strictly enforced** | SPIFFE identity + OPA policy = enforce |
| **7. The enterprise collects as much information as possible** | Audit every agent action, every policy evaluation |

---

## Identity Layer: SPIFFE/SPIRE

### What Is SPIFFE?

**SPIFFE** (Secure Production Identity Framework for Everyone) is a **CNCF-graduated project** that provides **cryptographically-verifiable workload identity** across heterogeneous environments. It issues **SVIDs** (SPIFFE Verifiable Identity Documents) — X.509 certificates or JWT tokens — to workloads.

### Why SPIFFE for AI-RAN?

- **K8S pods get identity automatically** — No manual certificate management
- **Cross-cluster identity** — Edge cell site pods authenticate into central RIC
- **Short-lived credentials** — SVIDs rotate every 1 hour (configurable)
- **mTLS everywhere** — SPIRE agents automatically negotiate mTLS between workloads
- **Multi-vendor trust** — xApps from different vendors can mutually authenticate

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  SPIRE Server (per region)                               │
│  • Issues SVIDs to workloads                             │
│  • Federates with other SPIRE servers                    │
│  • Stores trust bundles                                  │
└─────────────────────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────────────────────┐
│  SPIRE Agent (DaemonSet per node)                        │
│  • Node attestation (TPM, cloud metadata)                │
│  • Workload attestation (K8S pod identity, selectors)   │
│  • Issues SVIDs to local pods via Unix socket            │
└─────────────────────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────────────────────┐
│  Workload (e.g., tactical-agent pod)                    │
│  • Fetches SVID from SPIRE Agent                         │
│  • Uses SVID to mTLS-connect to Near-RT RIC API         │
│  • SVID rotates automatically                            │
└─────────────────────────────────────────────────────────┘
```

### SPIRE Registration Entries for AI-RAN

```yaml
# spire-registration.yaml — Identity rules for RAN workloads
entries:
# Tier 1 Strategic Agent (Non-RT RIC)
- spiffe_id: spiffe://operator.com/non-rt-ric/strategic-agent
  parent_id: spiffe://operator.com/ns/non-rt-ric/sa/strategic-agent
  selectors:
  - k8s:ns:non-rt-ric
  - k8s:sa:strategic-agent
  - k8s:pod-label:app.kubernetes.io/component:agentic-ai
  - k8s:pod-label:app.kubernetes.io/tier:tier1
  ttl: 3600

# Tier 2 Tactical Agent (Near-RT RIC)
- spiffe_id: spiffe://operator.com/near-rt-ric/tactical-agent
  parent_id: spiffe://operator.com/ns/near-rt-ric/sa/tactical-agent
  selectors:
  - k8s:ns:near-rt-ric
  - k8s:sa:tactical-agent
  - k8s:pod-label:app.kubernetes.io/component:agentic-ai
  - k8s:pod-label:app.kubernetes.io/tier:tier2
  ttl: 1800  # Shorter TTL for real-time tier

# xApp from vendor X
- spiffe_id: spiffe://operator.com/near-rt-ric/xapp/vendor-x/energy-saver
  parent_id: spiffe://operator.com/ns/near-rt-ric/sa/xapp-runner
  selectors:
  - k8s:ns:near-rt-ric
  - k8s:pod-label:oran.org/xapp-name:energy-saver
  - k8s:pod-label:oran.org/xapp-vendor:vendor-x
  ttl: 3600

# O-DU at edge cell site
- spiffe_id: spiffe://operator.com/edge/cell-007/o-du
  parent_id: spiffe://operator.com/edge/cell-007/node
  selectors:
  - k8s:ns:o-du
  - k8s:pod-label:oran.org/component:o-du
  - k8s:pod-label:oran.org/cell-id:cell-007
  ttl: 3600
```

### SPIRE Server Deployment (K8S)

```yaml
# spire-server.yaml — SPIRE server for a region
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: spire-server
  namespace: spire
spec:
  replicas: 3  # HA
  serviceName: spire-server
  selector:
    matchLabels:
      app: spire-server
  template:
    metadata:
      labels:
        app: spire-server
    spec:
      serviceAccountName: spire-server
      containers:
      - name: spire-server
        image: ghcr.io/spiffe/spire-server:1.10.0
        args:
        - -config=/run/spire/config/server.conf
        ports:
        - containerPort: 8081
        volumeMounts:
        - name: spire-config
          mountPath: /run/spire/config
        - name: spire-data
          mountPath: /run/spire/data
      volumes:
      - name: spire-config
        configMap:
          name: spire-server-config
  volumeClaimTemplates:
  - metadata:
      name: spire-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: spire-server-config
  namespace: spire
data:
  server.conf: |
    server {
      bind_address = "0.0.0.0"
      bind_port = "8081"
      trust_domain = "operator.com"
      data_dir = "/run/spire/data"
      log_level = "INFO"
      ca_key_type = "rsa-2048"
      default_x509_svid_ttl = "1h"
      default_jwt_svid_ttl = "5m"
    }
    
    plugins {
      DataStore "sql" {
        plugin_data {
          database_type = "sqlite3"
          connection_string = "/run/spire/data/datastore.sqlite3"
        }
      }
      
      NodeAttestor "k8s_psat" {
        plugin_data {
          clusters = {
            "central-cloud" = {
              service_account_allow_list = ["spire:spire-agent"]
            }
            "edge-cell-007" = {
              service_account_allow_list = ["spire:spire-agent"]
            }
          }
        }
      }
      
      KeyManager "disk" {
        plugin_data {
          keys_path = "/run/spire/data/keys.json"
        }
      }
    }
```

---

## Authorization Layer: Policy-as-Code (OPA)

### What Is OPA?

**Open Policy Agent** is a CNCF-graduated project that provides a **declarative policy language (Rego)** for evaluating authorization decisions. It's used extensively in K8S for admission control (Gatekeeper) and can be embedded in services for runtime authorization.

### Why OPA for AI-RAN?

- **Declarative** — Policies are code, version-controlled in Git
- **Decoupled** — Policy logic separate from application logic
- **Auditable** — Every policy decision is logged with inputs
- **Performance** — Sub-millisecond evaluation
- **Ecosystem** — Integrates with Istio, Envoy, K8S admission

### Policy Example: A1 Policy Authorization

```rego
# a1_policy_authz.rego — Who can publish which A1 policies?
package oran.a1.policy

import future.keywords.if
import future.keywords.in

default allow := false

# Allow strategic-agent to publish any A1 policy
allow if {
    input.subject.spiffe_id == "spiffe://operator.com/non-rt-ric/strategic-agent"
    input.action == "publish"
}

# Allow tactical-agent to publish ONLY to its assigned cells
allow if {
    input.subject.spiffe_id == "spiffe://operator.com/near-rt-ric/tactical-agent"
    input.action == "publish"
    input.policy.target_cell_id in input.subject.assigned_cells
}

# Allow oncall engineer (human) to override in emergency
allow if {
    input.subject.role == "oncall-engineer"
    input.action == "publish"
    input.emergency_override == true
    input.reason != ""
}

# Deny all other publishers
# (xApps cannot publish A1 policies — they consume them)

# Additional checks — policy content validation
deny[msg] if {
    input.policy.max_power_dbm > 46.0
    msg := sprintf("power exceeds regulatory limit: %v dBm", [input.policy.max_power_dbm])
}

deny[msg] if {
    input.policy.forbidden_bands != []
    msg := sprintf("policy touches forbidden bands: %v", [input.policy.forbidden_bands])
}
```

### Policy Example: Agent-to-Agent Communication

```rego
# agent_communication.rego — Who can talk to whom?
package oran.agent.communication

import future.keywords.if

default allow := false

# Tier 1 can send policies to Tier 2 (downstream)
allow if {
    input.source.tier == "tier1"
    input.target.tier == "tier2"
    input.message_type == "a1_policy"
}

# Tier 2 can send telemetry aggregates to Tier 1 (upstream)
allow if {
    input.source.tier == "tier2"
    input.target.tier == "tier1"
    input.message_type == "telemetry_aggregate"
}

# Tier 2 can send control commands to Tier 3 (downstream)
allow if {
    input.source.tier == "tier2"
    input.target.tier == "tier3"
    input.message_type == "e2_control"
}

# Tier 3 can send safety alerts to Tier 2 (upstream)
allow if {
    input.source.tier == "tier3"
    input.target.tier == "tier2"
    input.message_type == "safety_alert"
}

# DENY: Tier 3 cannot talk to Tier 1 (must go through Tier 2)
# This prevents Tier 3 from being used as a bypass

# DENY: Tier 1 cannot send control commands directly to Tier 3
deny[msg] if {
    input.source.tier == "tier1"
    input.target.tier == "tier3"
    input.message_type == "e2_control"
    msg := "Tier 1 cannot directly control Tier 3 — must cascade through Tier 2"
}
```

### OPA Sidecar for xApps

```yaml
# xapp-with-opa.yaml — xApp pod with OPA sidecar
apiVersion: apps/v1
kind: Deployment
metadata:
  name: energy-saver-xapp
  namespace: near-rt-ric
spec:
  replicas: 1
  selector:
    matchLabels:
      app: energy-saver-xapp
  template:
    metadata:
      labels:
        app: energy-saver-xapp
        oran.org/xapp-name: energy-saver
    spec:
      serviceAccountName: xapp-runner
      containers:
      # Main xApp container
      - name: xapp
        image: vendor-x/energy-saver:2026.1
        env:
        - name: OPA_ENDPOINT
          value: "http://localhost:8181/v1/data/oran/xapp"
        volumeMounts:
        - name: spire-agent-socket
          mountPath: /run/spire/sockets
          readOnly: true
      
      # OPA sidecar
      - name: opa
        image: openpolicyagent/opa:0.67.0
        args:
        - "run"
        - "--server"
        - "--addr=0.0.0.0:8181"
        - "--log-level=info"
        - "--decision-logs=true"  # Log every decision
        - "/policies"
        ports:
        - containerPort: 8181
        volumeMounts:
        - name: opa-policies
          mountPath: /policies
      
      volumes:
      - name: spire-agent-socket
        hostPath:
          path: /run/spire/sockets
          type: Directory
      - name: opa-policies
        configMap:
          name: xapp-opa-policies
```

---

## Micro-Segmentation: K8S Network Policies

### Principle

By default, **no agent can talk to anything**. Explicit allow rules open specific paths.

### Network Policy for AI-RAN

```yaml
# network-policy-non-rt-ric.yaml — Default deny + explicit allow
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: non-rt-ric-default-deny
  namespace: non-rt-ric
spec:
  podSelector: {}  # Applies to all pods in namespace
  policyTypes:
  - Ingress
  - Egress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: strategic-agent-allow
  namespace: non-rt-ric
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: strategic-agent
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow from oncall engineers (via jump host)
  - from:
    - namespaceSelector:
        matchLabels:
          name: oncall-jumphost
    - podSelector:
        matchLabels:
          app: oncall-console
    ports:
    - port: 8443
      protocol: TCP
  
  # Allow from vLLM (for LLM inference)
  - from:
    - podSelector:
        matchLabels:
          app: vllm-telecom
    ports:
    - port: 8000
  
  egress:
  # Allow to Kafka (for publishing A1 policies)
  - to:
    - namespaceSelector:
        matchLabels:
          name: strimzi
    - podSelector:
        matchLabels:
          app: kafka
    ports:
    - port: 9092
  
  # Allow to AODT (digital twin)
  - to:
    - podSelector:
        matchLabels:
          app: aodt-client
    ports:
    - port: 443
  
  # Allow DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - port: 53
      protocol: UDP
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: a1-policy-kafka-topic
  namespace: strimzi
spec:
  podSelector:
    matchLabels:
      strimzi.io/name: kafka
  policyTypes:
  - Ingress
  ingress:
  # Only strategic-agent can write to strategic-policies topic
  - from:
    - namespaceSelector:
        matchLabels:
          name: non-rt-ric
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: strategic-agent
    ports:
    - port: 9092
  
  # Only tactical-agent can read from strategic-policies topic
  - from:
    - namespaceSelector:
        matchLabels:
          name: near-rt-ric
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: tactical-agent
    ports:
    - port: 9092
```

---

## Continuous Verification: Agent Behavior Monitoring

### Principle

Authentication is **point-in-time**. Authorization is **per-request**. But neither catches a **compromised agent that is correctly authenticated but behaving abnormally**.

### Behavior Baselines

Build a baseline of **normal agent behavior** and alert on deviation.

```python
# agent_behavior_monitor.py
class AgentBehaviorMonitor:
    def __init__(self, agent_id: str, baseline: BehaviorBaseline):
        self.agent_id = agent_id
        self.baseline = baseline
        self.anomaly_threshold = 0.7
    
    def observe_action(self, action: AgentAction):
        """Score action against baseline."""
        anomalies = []
        
        # Anomaly 1: Action frequency outside baseline
        rate = self._actions_per_minute(action.action_type)
        baseline_rate = self.baseline.get_rate(action.action_type)
        if rate > baseline_rate * 3:
            anomalies.append(f"rate_anomaly: {rate} vs baseline {baseline_rate}")
        
        # Anomaly 2: Unusual target cells
        if action.target_cell_id not in self.baseline.get_typical_cells():
            anomalies.append(f"unusual_target: {action.target_cell_id}")
        
        # Anomaly 3: Unusual time of day
        hour = action.timestamp.hour
        if hour not in self.baseline.get_active_hours(action.action_type):
            anomalies.append(f"unusual_time: {hour}:00")
        
        # Anomaly 4: Action magnitude outside baseline
        magnitude = action.magnitude()
        baseline_mag = self.baseline.get_magnitude(action.action_type)
        if magnitude > baseline_mag * 2:
            anomalies.append(f"magnitude_anomaly: {magnitude} vs {baseline_mag}")
        
        # Aggregate anomaly score
        score = min(1.0, len(anomalies) * 0.25)
        
        if score > self.anomaly_threshold:
            self._alert(
                severity='high',
                agent_id=self.agent_id,
                score=score,
                anomalies=anomalies,
                action=action
            )
```

### Behavior Monitoring Pipeline

```
Agent Pod
    ↓ (audit log stream)
Kafka Topic: agent-audit-logs
    ↓
Flink Job: Real-time Behavior Analysis
    ↓
┌──────────────┬──────────────────┬─────────────────┐
│ TimescaleDB  │ Prometheus       │ AlertManager      │
│ (historical) │ (current state)  │ (alerting)        │
└──────────────┴──────────────────┴─────────────────┘
    ↓
If anomaly score > threshold:
  → Alert oncall
  → Increase audit log verbosity
  → Optionally trigger kill switch
```

---

## Cedar: Alternative to OPA

**Cedar** (by AWS, open source) is a newer policy language that's simpler than Rego for many use cases. O-RAN operators are evaluating Cedar for agent authorization.

### Cedar Example

```cedar
// agent_authz.cedar — Who can invoke which tools?

// Strategic agent can call query_kpis and predict_traffic
permit(
    principal == oran::Agent::"strategic-agent",
    action in [oran::Action::"query_kpis", oran::Action::"predict_traffic"],
    resource
);

// Strategic agent cannot call execute_e2 directly
forbid(
    principal == oran::Agent::"strategic-agent",
    action == oran::Action::"execute_e2",
    resource
);

// Tactical agent can call execute_e2 only on its assigned cells
permit(
    principal == oran::Agent::"tactical-agent",
    action == oran::Action::"execute_e2",
    resource in oran::Agent::"tactical-agent".assigned_cells
);

// Kill switch controller can scale any deployment
permit(
    principal == oran::Agent::"kill-switch-controller",
    action == oran::Action::"scale_deployment",
    resource
);
```

---

## Zero Trust Deployment Checklist

### Implement Today

- [ ] **Deploy SPIRE** — Server + DaemonSet agents on all nodes
- [ ] **Register all workloads** — Strategic, tactical, reactive agents, xApps
- [ ] **Enable mTLS via SPIFFE** — On all agent-to-agent communication
- [ ] **Default deny network policies** — In every RIC namespace
- [ ] **Deploy OPA Gatekeeper** — K8S admission control

### Implement This Quarter

- [ ] **OPA sidecar in xApps** — Runtime authorization
- [ ] **Rego policies for agent communication** — Version-controlled in Git
- [ ] **Agent behavior monitoring** — Baseline + anomaly detection
- [ ] **Audit log pipeline** — Kafka → Flink → TimescaleDB

### Plan for Next Quarter

- [ ] **Evaluate Cedar** — For simpler policy authoring
- [ ] **Federation across clusters** — SPIRE federation for multi-region RIC
- [ ] **Behavioral drift alerts** — Continuous baseline retraining
- [ ] **Zero trust red-team exercise** — Simulate compromised agent

---

## Case Study: Zero Trust at Operator Y (Hypothetical)

### Scenario: Compromised xApp

**Timeline**:
- **Day 0**: Operator Y deploys new xApp from Vendor Z (third-party)
- **Day 14**: xApp is compromised via supply chain attack (malicious dependency)
- **Day 14, 14:00**: Compromised xApp attempts to publish A1 policies
- **Day 14, 14:00:01**: OPA denies — xApp SPIFFE identity not in allow list
- **Day 14, 14:01**: xApp attempts to scan other namespaces
- **Day 14, 14:01:02**: K8S NetworkPolicy drops — default deny
- **Day 14, 14:02**: xApp attempts to exfiltrate telemetry via HTTPS to external server
- **Day 14, 14:02:03**: Egress policy drops — only allow-listed egress
- **Day 14, 14:05**: Security team alerted by anomaly detector (xApp behavior deviation)
- **Day 14, 14:10**: xApp pod terminated, investigation begins

**Lesson**: Zero trust **contained the blast radius** to a single pod. No network compromise, no data exfiltration.

---

## References

- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final)
- [SPIFFE/SPIRE Project](https://spiffe.io/)
- [Open Policy Agent](https://www.openpolicyagent.org/)
- [Cedar Policy Language](https://www.cedarpolicy.com/)
- [O-RAN WG11 O-R003 v07.00: Security Requirements](https://www.o-ran.org/specifications)
- [Istio mTLS with SPIFFE](https://istio.io/latest/docs/tasks/security/authentication/)
- [AWS Verified Permissions (Cedar)](https://aws.amazon.com/verified-permissions/)
