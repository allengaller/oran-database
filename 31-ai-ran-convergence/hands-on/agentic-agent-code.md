# Lab 1: Building an Agentic AI Network Agent

> Build a production-grade LLM-powered network agent for the Non-RT RIC

## Overview

This lab implements the **Tier 1 Strategic Agent** from the Multi-Scale Agentic AI Framework (arXiv 2602.14117). The agent:

- Uses a telecom-tuned SLM for reasoning
- Calls specialized tools (DRL, GNN, TimesFM, Digital Twin)
- Enforces safety guardrails before any action
- Exports reasoning chains for audit

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                 NetworkAgent (Non-RT RIC)                  │
│                                                            │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────┐ │
│  │ Perception     │  │ LLM Reasoning  │  │ Tool Router │ │
│  │ (E2 + KPI)     │─►│ (Qwen2.5-7B)   │─►│ (8 tools)   │ │
│  └────────────────┘  └────────────────┘  └──────┬──────┘ │
│                                                   │        │
│  ┌────────────────┐  ┌────────────────┐  ┌───────▼──────┐│
│  │ Audit Logger   │◄─│ Safety Checker │◄─│ Executor     ││
│  │ (Reasoning     │  │ (Bounds +      │  │ (E2 / A1 /   ││
│  │  Chains)       │  │  Twin Valid.)  │  │  Twin APIs)  ││
│  └────────────────┘  └────────────────┘  └──────────────┘│
└──────────────────────────────────────────────────────────┘
```

## Implementation

### 1. Base Agent Class

```python
# agent/network_agent.py
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json
import time
from enum import Enum

from vllm import LLM, SamplingParams
import prometheus_client

# Prometheus metrics
AGENT_ACTIONS_TOTAL = prometheus_client.Counter(
    'agent_actions_total', 'Total actions taken', ['tool', 'result']
)
AGENT_REASONING_SECONDS = prometheus_client.Histogram(
    'agent_reasoning_seconds', 'Time spent in LLM reasoning'
)
AGENT_SAFETY_REJECTS = prometheus_client.Counter(
    'agent_safety_rejects_total', 'Actions rejected by safety checker'
)


class SafetyVerdict(Enum):
    ALLOW = "allow"
    REJECT_BOUNDS = "reject_bounds"
    REJECT_TWIN = "reject_twin"
    REJECT_RATE = "reject_rate_limit"


@dataclass
class AgentAction:
    tool: str
    params: Dict[str, Any]
    reasoning: str
    confidence: float
    twin_prediction: Optional[Dict] = None
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class NetworkAgent:
    """
    Tier 1 Strategic Agent for Non-RT RIC.

    Uses a telecom-tuned SLM to reason about network state and
    orchestrate specialized ML tools for optimization actions.
    """

    SYSTEM_PROMPT = """You are a Tier 1 RAN optimization agent running
in the Non-RT RIC of an O-RAN network. Your job:

1. Analyze network observations (KPIs, alerts, E2 telemetry)
2. Decide what diagnostic tools to call to understand the situation
3. Formulate a multi-step optimization plan
4. For each step, specify the tool and parameters

Available tools:
- predict_traffic(area, horizon_hours): Forecast traffic using TimesFM
- optimize_power(cell_ids, objective): Run PPO policy for power control
- check_interference(cell_ids): Run GNN to analyze interference graph
- simulate_action(action_spec): Pre-validate in digital twin (REQUIRED for any network change)
- query_kpis(promql): Query Prometheus for current/past KPIs
- execute_e2(cell_id, command, params): Send E2 command to Near-RT RIC
- publish_a1_policy(policy_yaml): Publish policy to A1 interface
- alert_operator(severity, message): Escalate to human operator

Constraints:
- NEVER call execute_e2 without a prior simulate_action that returned "ok"
- Maximum 3 network changes per reasoning cycle
- All power changes must stay within [min_power_dbm, max_power_dbm]
- If unsure about impact, call alert_operator instead of acting

Respond in JSON:
{
  "situation_summary": "...",
  "diagnostics": [{"tool": "...", "params": {...}}],
  "plan": [
    {"tool": "...", "params": {...}, "reason": "..."}
  ],
  "confidence": 0.0-1.0,
  "escalate_to_human": false,
  "escalation_reason": "..."
}
"""

    def __init__(
        self,
        llm_endpoint: str,
        tools: Dict[str, Any],
        safety_config: Dict[str, Any],
        audit_logger: Any,
    ):
        self.llm = LLM(model=llm_endpoint, tensor_parallel_size=1)
        self.sampling = SamplingParams(
            temperature=0.2,
            top_p=0.95,
            max_tokens=2048,
            stop=["</s>"],
        )
        self.tools = tools
        self.safety = SafetyChecker(safety_config)
        self.audit = audit_logger
        self.action_history: List[AgentAction] = []
        self.rate_limiter = RateLimiter(max_actions_per_hour=50)

    def reason_and_act(self, observation: Dict) -> List[AgentAction]:
        """Main loop: observe -> reason -> act."""
        start = time.time()

        # 1. LLM reasoning
        prompt = self._build_prompt(observation)
        response = self.llm.generate([prompt], self.sampling)[0].outputs[0].text

        AGENT_REASONING_SECONDS.observe(time.time() - start)

        # 2. Parse JSON response
        plan = self._parse_response(response)
        self.audit.log_reasoning(
            observation=observation,
            reasoning_chain=response,
            plan=plan,
        )

        # 3. Execute diagnostics first (read-only, safe)
        diagnostic_results = []
        for step in plan.get("diagnostics", []):
            result = self.tools[step["tool"]].execute(step["params"])
            diagnostic_results.append({"tool": step["tool"], "result": result})

        # 4. Re-reason with diagnostic results (optional refinement)
        if diagnostic_results:
            refined_plan = self._refine_plan(plan, diagnostic_results)
        else:
            refined_plan = plan

        # 5. Execute action plan with safety checks
        executed: List[AgentAction] = []
        for step in refined_plan.get("plan", []):
            action = AgentAction(
                tool=step["tool"],
                params=step["params"],
                reasoning=step.get("reason", ""),
                confidence=refined_plan.get("confidence", 0.5),
            )

            verdict = self.safety.check(action, self.action_history)
            if verdict != SafetyVerdict.ALLOW:
                AGENT_SAFETY_REJECTS.inc()
                self.audit.log_rejection(action, verdict)
                continue

            try:
                result = self.tools[action.tool].execute(action.params)
                AGENT_ACTIONS_TOTAL.labels(
                    tool=action.tool, result="success"
                ).inc()
                self.action_history.append(action)
                executed.append(action)
            except Exception as e:
                AGENT_ACTIONS_TOTAL.labels(
                    tool=action.tool, result="error"
                ).inc()
                self.audit.log_error(action, e)

        # 6. Escalate if needed
        if refined_plan.get("escalate_to_human"):
            self.tools["alert_operator"].execute({
                "severity": "warning",
                "message": refined_plan.get("escalation_reason", "Agent uncertain"),
            })

        return executed

    def _build_prompt(self, observation: Dict) -> str:
        return (
            f"<|system|>{self.SYSTEM_PROMPT}</s>"
            f"<|user|>Current observation:\n"
            f"{json.dumps(observation, indent=2)}\n\n"
            f"Recent action history (last 5):\n"
            f"{json.dumps([a.__dict__ for a in self.action_history[-5:]], indent=2)}"
            f"</s>"
            f"<|assistant|>"
        )

    def _parse_response(self, text: str) -> Dict:
        # Extract JSON block from response
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except (ValueError, json.JSONDecodeError) as e:
            self.audit.log_parse_error(text, e)
            return {"plan": [], "diagnostics": [], "confidence": 0.0}

    def _refine_plan(self, initial: Dict, diagnostics: List[Dict]) -> Dict:
        # Optional second LLM call with diagnostic results
        refine_prompt = (
            f"Initial plan: {json.dumps(initial)}\n"
            f"Diagnostic results: {json.dumps(diagnostics)}\n"
            f"Revise the plan if diagnostics suggest changes."
        )
        response = self.llm.generate([refine_prompt], self.sampling)[0].outputs[0].text
        return self._parse_response(response)
```

### 2. Safety Checker

```python
# agent/safety.py
from typing import List
from agent.network_agent import AgentAction, SafetyVerdict


class SafetyChecker:
    """
    Multi-layer safety guardrails per WG11 Secure AI specs.

    Layer 1: Hard-coded physical bounds
    Layer 2: Rate limiting
    Layer 3: Digital twin pre-validation
    """

    def __init__(self, config: dict):
        self.bounds = config["physical_bounds"]
        self.rate_limit = config["max_actions_per_hour"]
        self.twin_client = config["twin_client"]
        self.action_window: List[float] = []

    def check(self, action: AgentAction, history: List[AgentAction]) -> SafetyVerdict:
        # Layer 1: Physical bounds
        if not self._check_bounds(action):
            return SafetyVerdict.REJECT_BOUNDS

        # Layer 2: Rate limiting
        if not self._check_rate():
            return SafetyVerdict.REJECT_RATE

        # Layer 3: Digital twin pre-validation (for network-changing actions)
        if action.tool in {"execute_e2", "publish_a1_policy"}:
            if not self._check_twin(action):
                return SafetyVerdict.REJECT_TWIN

        return SafetyVerdict.ALLOW

    def _check_bounds(self, action: AgentAction) -> bool:
        if action.tool == "optimize_power":
            for cell_id, power in action.params.get("power_dbm", {}).items():
                if not (self.bounds["min_power_dbm"] <= power <= self.bounds["max_power_dbm"]):
                    return False
        if action.tool == "execute_e2":
            if action.params.get("command") == "set_antenna_tilt":
                tilt = action.params.get("tilt_degrees", 0)
                if not (-15 <= tilt <= 15):
                    return False
        return True

    def _check_rate(self) -> bool:
        now = time.time()
        self.action_window = [t for t in self.action_window if now - t < 3600]
        return len(self.action_window) < self.rate_limit

    def _check_twin(self, action: AgentAction) -> bool:
        """Pre-validate action in digital twin. Block if predicted KPI degradation > 10%."""
        prediction = self.twin_client.simulate(action.__dict__)
        action.twin_prediction = prediction
        if prediction.get("predicted_kpi_degradation_pct", 0) > 10:
            return False
        return True
```

### 3. Tool Implementations

```python
# agent/tools.py
import requests
import yaml


class DigitalTwinTool:
    """Calls NVIDIA AODT API for action pre-validation."""

    def __init__(self, aodt_endpoint: str, api_key: str):
        self.endpoint = aodt_endpoint
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def execute(self, params: dict) -> dict:
        resp = requests.post(
            f"{self.endpoint}/v1/simulate",
            json={"action_spec": params["action_spec"]},
            headers=self.headers,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()


class A1PolicyPublisher:
    """Publishes policies to Non-RT RIC A1 interface."""

    def __init__(self, a1_endpoint: str):
        self.endpoint = a1_endpoint

    def execute(self, params: dict) -> dict:
        policy_yaml = yaml.safe_dump(params["policy"])
        resp = requests.put(
            f"{self.endpoint}/a1-policies/v1",
            data=policy_yaml,
            headers={"Content-Type": "application/yaml"},
            timeout=10,
        )
        return {"status": resp.status_code, "policy_id": params.get("policy_id")}


class E2CommandExecutor:
    """Sends control commands to Near-RT RIC via E2 interface."""

    def __init__(self, e2_endpoint: str):
        self.endpoint = e2_endpoint

    def execute(self, params: dict) -> dict:
        payload = {
            "cell_id": params["cell_id"],
            "command": params["command"],
            "params": params["params"],
        }
        resp = requests.post(
            f"{self.endpoint}/e2/v1/control",
            json=payload,
            timeout=5,  # Tight timeout for Near-RT
        )
        return resp.json()
```

### 4. Deployment Manifest

```yaml
# manifests/agentic-agent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentic-network-agent
  namespace: non-rt-ric
  labels:
    app: agentic-agent
    oran.org/tier: "1"  # Strategic agent
spec:
  replicas: 1  # Single active with leader election
  selector:
    matchLabels:
      app: agentic-agent
  template:
    metadata:
      labels:
        app: agentic-agent
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
    spec:
      serviceAccountName: agentic-agent
      containers:
      - name: agent
        image: oran/agentic-agent:2026.1
        ports:
        - containerPort: 8080
          name: metrics
        env:
        - name: LLM_ENDPOINT
          value: "http://vllm-telecom.non-rt-ric:8000"
        - name: AODT_ENDPOINT
          value: "https://aodt.aws.nvidia.com"
        - name: AODT_API_KEY
          valueFrom:
            secretKeyRef:
              name: aodt-credentials
              key: api-key
        - name: E2_ENDPOINT
          value: "http://e2term.near-rt-ric:36421"
        - name: A1_ENDPOINT
          value: "http://a1mediator.non-rt-ric:9090"
        - name: SAFETY_MAX_POWER_DBM
          value: "46"
        - name: SAFETY_MIN_POWER_DBM
          value: "10"
        - name: SAFETY_MAX_ACTIONS_PER_HOUR
          value: "50"
        resources:
          requests:
            cpu: "2"
            memory: "8Gi"
            nvidia.com/gpu: "1"
          limits:
            cpu: "4"
            memory: "16Gi"
            nvidia.com/gpu: "1"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
      - name: audit-sidecar
        image: oran/audit-logger:2026.1
        volumeMounts:
        - name: audit-logs
          mountPath: /var/log/agent-audit
        env:
        - name: KAFKA_BOOTSTRAP
          value: "kafka.event-bus:9092"
      volumes:
      - name: audit-logs
        emptyDir: {}
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: agentic-agent
  namespace: non-rt-ric
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: agentic-agent-role
  namespace: non-rt-ric
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
- apiGroups: ["coordination.k8s.io"]
  resources: ["leases"]
  verbs: ["get", "create", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: agentic-agent-binding
  namespace: non-rt-ric
subjects:
- kind: ServiceAccount
  name: agentic-agent
roleRef:
  kind: Role
  name: agentic-agent-role
  apiGroup: rbac.authorization.k8s.io
```

### 5. Example Observation and Agent Output

**Input Observation** (from E2 telemetry):
```json
{
  "timestamp": "2026-03-15T14:30:00Z",
  "cell_id": "Cell_Stadium_01",
  "alerts": [
    {"type": "traffic_spike", "severity": "warning", "delta_pct": 300},
    {"type": "prb_utilization", "value": 92, "threshold": 85}
  ],
  "kpis": {
    "throughput_mbps": 1250,
    "connected_ues": 4872,
    "drop_rate_pct": 2.3,
    "avg_sinr_db": 8.2
  },
  "context": {
    "time_of_day": "14:30",
    "day_of_week": "Friday",
    "local_events": [
      {"type": "concert", "venue": "National Stadium", "start": "19:00", "expected_attendance": 50000}
    ]
  }
}
```

**Agent Reasoning Chain** (LLM output):
```json
{
  "situation_summary": "Stadium cell is experiencing a 300% traffic spike 4.5 hours before a scheduled concert. Current PRB utilization at 92% indicates capacity stress. Drop rate elevated at 2.3%.",
  "diagnostics": [
    {"tool": "predict_traffic", "params": {"area": "stadium_district", "horizon_hours": 6}},
    {"tool": "query_kpis", "params": {"promql": "prb_utilization{cell=~\"Stadium_.*\"}[1h]"}}
  ],
  "plan": [
    {
      "tool": "simulate_action",
      "params": {"action_spec": {"type": "activate_sleeping_cells", "cells": ["Stadium_02", "Stadium_03", "Stadium_04"]}},
      "reason": "Pre-validate activating 3 sleeping cells to offload traffic"
    },
    {
      "tool": "execute_e2",
      "params": {"cell_id": "Stadium_02", "command": "activate_cell", "params": {}},
      "reason": "Activate first sleeping cell (twin validated)"
    },
    {
      "tool": "publish_a1_policy",
      "params": {
        "policy_id": "vip-slice-concert-20260315",
        "policy": {
          "target": "stadium_cells",
          "time_window": "18:00-23:00",
          "action": "prioritize_vip_slice",
          "min_throughput_mbps": 50
        }
      },
      "reason": "Establish VIP slice policy for concert window"
    }
  ],
  "confidence": 0.87,
  "escalate_to_human": false
}
```

---

## Exercises

1. **Add a new tool**: Implement `detect_root_cause` that calls a log-analyzer LLM
2. **Tune safety bounds**: Adjust power limits and observe rejection rate
3. **Add rate limiting per tool**: Different limits for read vs. write operations
4. **Implement A/B testing**: Run two agent variants and compare KPI outcomes
5. **Add multi-agent coordination**: Have multiple agents negotiate before acting

## Next Lab

→ [Lab 2: NVIDIA ARC K8S Deployment](./k8s-arc-deployment.md)
