---
title: "Lab 3: Telecom-LLM Deployment"
description: "> Deploy a telecom-tuned SLM as a Non-RT RIC rApp service for intent translation and root cause anal"
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-08-25"
keywords: ['O-RAN', 'AI-RAN', 'RIC']
---

# Lab 3: Telecom-LLM Deployment

> Deploy a telecom-tuned SLM as a Non-RT RIC rApp service for intent translation and root cause analysis

## Overview

This lab deploys a **fine-tuned Qwen2.5-7B-Telecom** model using vLLM, exposing two capabilities:

1. **Intent Translation**: Natural language operator commands → O-RAN policy YAML
2. **Root Cause Analysis (RCA)**: Alarm log analysis → structured diagnosis

Deployed as a KServe InferenceService for production features (canary, autoscaling, A/B testing).

---

## Step 1: Model Preparation

### 1.1 Base Model + Telecom LoRA Adapter

```bash
# Download base model
huggingface-cli download Qwen/Qwen2.5-7B-Instruct \
  --local-dir /models/qwen2.5-7b-instruct

# Download telecom-tuned LoRA adapter (community example)
huggingface-cli download oran-community/qwen2.5-7b-telecom-lora \
  --local-dir /models/qwen2.5-7b-telecom-lora
```

### 1.2 Model Config

```yaml
# model-config.yaml
model_name: qwen2.5-7b-telecom
base_model_path: /models/qwen2.5-7b-instruct
lora_adapters:
  - name: telecom
    path: /models/qwen2.5-7b-telecom-lora
    default: true
max_model_len: 32768
dtype: bfloat16
gpu_memory_utilization: 0.9
enable_prefix_caching: true
```

---

## Step 2: KServe Deployment

### 2.1 Install KServe

```bash
# Install KServe with vLLM runtime
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.13.0/kserve.yaml
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.13.0/kserve-runtimes.yaml
```

### 2.2 InferenceService Manifest

```yaml
# telecom-llm-inferenceservice.yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: telecom-llm
  namespace: non-rt-ric
  annotations:
    serving.kserve.io/deploymentMode: RawDeployment
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
spec:
  predictor:
    timeout: 120
    minReplicas: 1
    maxReplicas: 4
    scaleMetric: gpuUtilization
    scaleTarget: 70
    containers:
    - name: vllm
      image: vllm/vllm-openai:v0.5.3
      args:
      - --model=/models/qwen2.5-7b-instruct
      - --served-model-name=qwen2.5-7b-telecom
      - --enable-lora
      - --lora-modules=telecom=/models/qwen2.5-7b-telecom-lora
      - --max-model-len=32768
      - --dtype=bfloat16
      - --gpu-memory-utilization=0.9
      - --enable-prefix-caching
      ports:
      - containerPort: 8000
        protocol: TCP
      resources:
        requests:
          cpu: "4"
          memory: "16Gi"
          nvidia.com/gpu: "1"
        limits:
          cpu: "8"
          memory: "32Gi"
          nvidia.com/gpu: "1"
      readinessProbe:
        httpGet:
          path: /health
          port: 8000
        initialDelaySeconds: 60
        periodSeconds: 10
      livenessProbe:
        httpGet:
          path: /health
          port: 8000
        initialDelaySeconds: 120
        periodSeconds: 30
      volumeMounts:
      - name: models
        mountPath: /models
    volumes:
    - name: models
      persistentVolumeClaim:
        claimName: telecom-llm-models-pvc
---
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: telecom-llm-canary
  namespace: non-rt-ric
  annotations:
    serving.kserve.io/deploymentMode: RawDeployment
spec:
  predictor:
    canaryTrafficPercent: 10
    containers:
    - name: vllm
      image: vllm/vllm-openai:v0.5.4  # Newer version for canary
      args:
      - --model=/models/qwen2.5-7b-instruct
      - --served-model-name=qwen2.5-7b-telecom
      # ... same args
      resources:
        requests:
          nvidia.com/gpu: "1"
        limits:
          nvidia.com/gpu: "1"
```

---

## Step 3: Intent Translation API

### 3.1 Translation Service Wrapper

```python
# services/intent_translator.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import yaml

app = FastAPI(title="O-RAN Intent Translator")

VLLM_ENDPOINT = "http://telecom-llm.non-rt-ric.svc.cluster.local:8000/v1/chat/completions"

INTENT_SYSTEM_PROMPT = """You are an O-RAN policy translator.
Convert operator natural-language intent into valid O-RAN A1 policy YAML.

Policy schema (O-RAN A1):
- policy_type_id: integer (100=SLA, 200=energy, 300=mobility, 400=QoS)
- policy_id: string (unique identifier, kebab-case)
- scope: {cell_ids: [...], time_window: "HH:MM-HH:MM"}
- statement: {action: <action>, parameters: {...}, conditions: {...}}
- priority: integer 1-10

Output ONLY the YAML, no markdown fences, no commentary.
"""


class IntentRequest(BaseModel):
    intent: str
    operator_id: str
    context: Optional[dict] = None


class IntentResponse(BaseModel):
    policy_yaml: str
    confidence: float
    clarification_needed: Optional[str] = None


@app.post("/translate", response_model=IntentResponse)
async def translate_intent(req: IntentRequest):
    messages = [
        {"role": "system", "content": INTENT_SYSTEM_PROMPT},
        {"role": "user", "content": req.intent},
    ]

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            VLLM_ENDPOINT,
            json={
                "model": "qwen2.5-7b-telecom",
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 1024,
            },
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail="LLM service error")

    content = resp.json()["choices"][0]["message"]["content"]

    # Validate YAML
    try:
        policy = yaml.safe_load(content)
        # Basic schema validation
        required = ["policy_type_id", "policy_id", "scope", "statement"]
        for field in required:
            if field not in policy:
                raise ValueError(f"Missing {field}")
    except Exception as e:
        return IntentResponse(
            policy_yaml=content,
            confidence=0.3,
            clarification_needed=f"Generated invalid YAML: {e}",
        )

    return IntentResponse(policy_yaml=content, confidence=0.9)
```

### 3.2 Example Intent → Policy

**Input Intent** (spoken/written by operator):
```
"Next Friday night, there's a concert at the National Stadium starting at 7 PM,
expected attendance 50,000. Please ensure VIP subscribers get at least 50 Mbps
downlink throughput from 6 PM to 11 PM in the stadium cells."
```

**Generated A1 Policy YAML**:
```yaml
policy_type_id: 400
policy_id: vip-slice-stadium-concert-2026-03-20
scope:
  cell_ids:
    - Cell_Stadium_01
    - Cell_Stadium_02
    - Cell_Stadium_03
    - Cell_Stadium_04
  time_window: "18:00-23:00"
  effective_date: "2026-03-20"
statement:
  action: prioritize_slice
  parameters:
    slice_type: vip
    subscriber_filter: "subscription_tier == 'VIP'"
    min_throughput_mbps: 50
    direction: downlink
    preemption: false
  conditions:
    attendance_threshold: 30000
    fallback_policy: default-sla
priority: 8
```

---

## Step 4: Root Cause Analysis API

### 4.1 RCA Service

```python
# services/rca_analyzer.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import httpx

app = FastAPI(title="O-RAN Alarm RCA Analyzer")

VLLM_ENDPOINT = "http://telecom-llm.non-rt-ric.svc.cluster.local:8000/v1/chat/completions"

RCA_SYSTEM_PROMPT = """You are a senior O-RAN network operations engineer.
Analyze the alarm log and return a structured diagnosis.

Return JSON:
{
  "root_cause": "one-line summary",
  "category": "<hardware|software|configuration|external|capacity>",
  "affected_components": ["O-RU-XX", "O-DU-YY", ...],
  "evidence": ["specific log line references"],
  "recommended_actions": [
    {"priority": 1, "action": "...", "expected_outcome": "..."},
    ...
  ],
  "confidence": 0.0-1.0,
  "escalate_to_vendor": false,
  "related_3gpp_specs": ["38.401", "38.331", ...]
}

Use your knowledge of 3GPP, O-RAN specs, and typical fault patterns.
If evidence is ambiguous, lower confidence and suggest further diagnostics.
"""


class AlarmLog(BaseModel):
    alarms: List[dict]
    timeframe_minutes: int
    cell_ids: List[str]


class RCAResponse(BaseModel):
    root_cause: str
    category: str
    affected_components: List[str]
    evidence: List[str]
    recommended_actions: List[dict]
    confidence: float
    escalate_to_vendor: bool
    related_3gpp_specs: List[str]


@app.post("/rca", response_model=RCAResponse)
async def analyze_rca(log: AlarmLog):
    user_content = (
        f"Timeframe: last {log.timeframe_minutes} minutes\n"
        f"Cells: {', '.join(log.cell_ids)}\n\n"
        f"Alarm log:\n"
    )
    for alarm in log.alarms[:50]:  # Cap at 50 alarms to fit context
        user_content += f"- [{alarm.get('timestamp')}] {alarm.get('severity')} " \
                        f"{alarm.get('source')}: {alarm.get('message')}\n"

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(
            VLLM_ENDPOINT,
            json={
                "model": "qwen2.5-7b-telecom",
                "messages": [
                    {"role": "system", "content": RCA_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0.2,
                "max_tokens": 1500,
                "response_format": {"type": "json_object"},
            },
        )

    content = resp.json()["choices"][0]["message"]["content"]
    import json
    return json.loads(content)
```

### 4.2 Example RCA Output

**Input Alarm Log**:
```json
{
  "alarms": [
    {"timestamp": "2026-03-15T14:32:01Z", "severity": "major", "source": "O-RU-142", "message": "Optical module TX power low: -12 dBm (threshold: -8 dBm)"},
    {"timestamp": "2026-03-15T14:32:05Z", "severity": "critical", "source": "O-DU-07", "message": "Fronthaul link down: port eth2"},
    {"timestamp": "2026-03-15T14:32:10Z", "severity": "major", "source": "O-DU-07", "message": "eCPRI sync lost for cell Cell_Highway_142"},
    {"timestamp": "2026-03-15T14:32:15Z", "severity": "warning", "source": "Cell_Highway_142", "message": "UE drop rate elevated: 8.5% (normal: <1%)"},
    {"timestamp": "2026-03-15T14:32:20Z", "severity": "warning", "source": "Cell_Highway_142", "message": "Handover success rate degraded: 87% (normal: >98%)"}
  ],
  "timeframe_minutes": 5,
  "cell_ids": ["Cell_Highway_142"]
}
```

**RCA Response**:
```json
{
  "root_cause": "Optical transceiver failure at O-RU-142 causing fronthaul link loss",
  "category": "hardware",
  "affected_components": ["O-RU-142", "O-DU-07", "Cell_Highway_142"],
  "evidence": [
    "O-RU-142 reported TX power -12 dBm, 4 dB below threshold",
    "O-DU-07 fronthaul port eth2 went down 4 seconds later",
    "eCPRI sync loss is downstream consequence of physical link failure",
    "UE drop rate and handover degradation are symptoms of cell unavailability"
  ],
  "recommended_actions": [
    {"priority": 1, "action": "Dispatch field tech to replace SFP+ optical module at O-RU-142", "expected_outcome": "Restore fronthaul link within 30 minutes"},
    {"priority": 2, "action": "Temporarily redirect traffic to adjacent cells Cell_Highway_141 and Cell_Highway_143 via A1 mobility policy", "expected_outcome": "Reduce UE drops by ~80% during repair"},
    {"priority": 3, "action": "Check other O-RUs on same fiber chain for early signs of degradation", "expected_outcome": "Prevent cascade failures"}
  ],
  "confidence": 0.92,
  "escalate_to_vendor": false,
  "related_3gpp_specs": ["38.401", "38.473", "ORAN-WG4-O-FH"]
}
```

---

## Step 5: Integration with Agentic Agent

```yaml
# agent-config.yaml (ConfigMap for Lab 1 agent)
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-tool-endpoints
  namespace: non-rt-ric
data:
  intent_translator: "http://intent-translator.non-rt-ric:8000/translate"
  rca_analyzer: "http://rca-analyzer.non-rt-ric:8000/rca"
  vllm_endpoint: "http://telecom-llm.non-rt-ric:8000/v1"
```

The Agentic Agent from Lab 1 can now call:
- **Intent Translation** to convert operator requests into policies
- **RCA** as a diagnostic tool in its `diagnostics` step

---

## Step 6: Monitoring and Evaluation

### 6.1 vLLM Metrics

```bash
# Scrape vLLM metrics
kubectl port-forward -n non-rt-ric svc/telecom-llm 8080:80
curl localhost:8080/metrics | grep vllm
```

Key metrics:
- `vllm:num_requests_running`
- `vllm:avg_generation_throughput_tokens_per_s`
- `vllm:e2e_request_latency_seconds`
- `vllm:gpu_cache_usage_perc`

### 6.2 Quality Evaluation

```python
# eval/intent_eval.py
# Run weekly quality evaluation against golden dataset
from sklearn.metrics import precision_score, recall_score

golden = load_golden_intents("eval/golden.yaml")
predictions = []
for intent in golden:
    resp = translate_intent(intent)
    predictions.append(validate_policy(resp.policy_yaml))

precision = precision_score(golden.labels, predictions, average="macro")
recall = recall_score(golden.labels, predictions, average="macro")

# Alert if quality degrades
if precision < 0.85 or recall < 0.85:
    alert("Intent translation quality below threshold — retrain LoRA")
```

---

## Cost Analysis

| Configuration | GPU | Cost/month (AWS g6) | Throughput |
|:---|:---|:---|:---|
| Single replica | 1x L4 | ~$600 | 15 req/s |
| Production (4 replicas) | 4x L4 | ~$2,400 | 60 req/s |
| With prefix caching | 4x L4 | ~$2,400 | ~90 req/s (+50%) |

---

## Next Lab

→ [Lab 4: Digital Twin Sync Agent](./digital-twin-sync.md)

## References

- [vLLM Documentation](https://docs.vllm.ai/)
- [KServe Documentation](https://kserve.github.io/website/latest/)
- [Qwen2.5 Model Family](https://huggingface.co/Qwen)
- [O-RAN A1 Policy Management Spec](https://www.o-ran.org/specifications)
