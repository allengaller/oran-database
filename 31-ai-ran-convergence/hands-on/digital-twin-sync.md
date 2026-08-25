---
title: "Lab 4: Digital Twin Sync Agent"
description: "> Build a real-time synchronization agent between physical RAN and NVIDIA AODT digital twin"
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-08-25"
keywords: ['O-RAN', 'AI-RAN', 'RIC']
---

# Lab 4: Digital Twin Sync Agent

> Build a real-time synchronization agent between physical RAN and NVIDIA AODT digital twin

## Overview

This lab builds a **twin sync agent** that:

1. **Subscribes** to RIC E2 telemetry via Kafka
2. **Streams** network state to NVIDIA AODT via Flink
3. **Detects** out-of-sync conditions and alerts
4. **Stores** historical twin states for trend analysis

## Architecture

```
Physical RAN                 Twin Sync Agent               Digital Twin
                                                              
  E2 Term ──────► Kafka ──► Flink ──┬──► NVIDIA AODT API    
                                     │                        
                                     ├──► TimescaleDB (history)
                                     │                        
                                     └──► Alertmanager (drift)
```

---

## Step 1: Kafka Topic Setup

### 1.1 Install Strimzi Kafka Operator

```bash
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka

# Wait for operator
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator \
  -n kafka --timeout=300s
```

### 1.2 Kafka Cluster + Topics

```yaml
# kafka-cluster.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: oran-twin
  namespace: kafka
spec:
  kafka:
    version: 3.7.0
    replicas: 3
    listeners:
    - name: plain
      port: 9092
      type: internal
      tls: false
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      default.replication.factor: 3
      min.insync.replicas: 2
    storage:
      type: ephemeral
  zookeeper:
    replicas: 3
    storage:
      type: ephemeral
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: e2-telemetry
  namespace: kafka
  labels:
    strimzi.io/cluster: oran-twin
spec:
  partitions: 12
  replicas: 3
  config:
    retention.ms: 86400000
    segment.bytes: 1073741824
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: twin-state-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: oran-twin
spec:
  partitions: 6
  replicas: 3
```

---

## Step 2: E2 Telemetry Subscriber

### 2.1 E2 Event Producer (sidecar in RIC)

```python
# e2-producer/e2_to_kafka.py
"""
Sidecar running alongside E2 termination in Near-RT RIC.
Forwards selected telemetry to Kafka for twin sync.
"""
from kafka import KafkaProducer
import json
import time
from e2_sdk import E2Subscriber

KAFKA_BOOTSTRAP = "oran-twin-kafka-bootstrap.kafka:9092"
TOPIC = "e2-telemetry"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BOOTSTRAP],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks="all",
    retries=5,
)

# Subscribe to key E2 service models
subscriber = E2Subscriber(
    e2term_endpoint="e2term.near-rt-ric:36421",
    service_models=["oran-e2sm-kpm", "oran-e2sm-rc"],
)


def on_indication(indication: dict):
    """Forward each E2 indication to Kafka."""
    event = {
        "timestamp": time.time(),
        "cell_id": indication.get("cell_global_id"),
        "event_type": indication.get("event_type"),
        "measurements": indication.get("measurements", {}),
        "sequence_number": indication.get("seq"),
    }
    producer.send(
        TOPIC,
        key=event["cell_id"].encode("utf-8"),
        value=event,
    )


subscriber.on_indication(on_indication)
subscriber.run()
```

---

## Step 3: Flink Streaming Job

### 3.1 Flink Cluster Deployment

```yaml
# flink-deployment.yaml
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: twin-sync-flink
  namespace: ai-ran-twin
spec:
  image: flink:1.19
  flinkVersion: v1_19
  flinkConfiguration:
    taskmanager.numberOfTaskSlots: "4"
    state.backend: rocksdb
    state.checkpoints.dir: s3://twin-sync-checkpoints/checkpoints
    state.savepoints.dir: s3://twin-sync-checkpoints/savepoints
    high-availability: kubernetes
  serviceAccount: flink
  jobManager:
    resource:
      memory: "2048m"
      cpu: 1
  taskManager:
    replicas: 3
    resource:
      memory: "4096m"
      cpu: 2
  job:
    jarURI: local:///opt/flink/usrlib/twin-sync-job.jar
    parallelism: 6
    upgradeMode: savepoint
    args:
    - --kafka-bootstrap=oran-twin-kafka-bootstrap.kafka:9092
    - --kafka-topic=e2-telemetry
    - --aodt-endpoint=https://aodt.aws.nvidia.com/api/v1
    - --timescale-host=timescaledb.ai-ran-twin
    - --sync-interval-seconds=5
```

### 3.2 Flink Job Logic (Java sketch)

```java
// TwinSyncJob.java
public class TwinSyncJob {
    public static void main(String[] args) {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.enableCheckpointing(5000);  // 5-second checkpoints

        KafkaSource<TelemetryEvent> source = KafkaSource.<TelemetryEvent>builder()
            .setBootstrapServers(params.kafkaBootstrap)
            .setTopics(params.kafkaTopic)
            .setGroupId("twin-sync")
            .setValueOnlyDeserializer(new TelemetryDeserializer())
            .build();

        DataStream<TelemetryEvent> events = env.fromSource(
            source, WatermarkStrategy.noWatermarks(), "E2 Telemetry");

        // Window by cell + 5-second intervals
        KeyedStream<TelemetryEvent, String> byCell = events.keyBy(e -> e.cellId);

        SingleOutputStreamOperator<TwinStateUpdate> updates = byCell
            .window(TumblingEventTimeWindows.of(Time.seconds(5)))
            .aggregate(new CellStateAggregator());

        // Sink to AODT
        updates.addSink(new AODTSinkFunction(params.aodtEndpoint));

        // Sink to TimescaleDB
        updates.addSink(new TimescaleSinkFunction(params.timescaleHost));

        // Detect drift and alert
        updates
            .filter(TwinSyncJob::isDriftSignificant)
            .addSink(new AlertmanagerSink("http://alertmanager:9093/api/v2/alerts"));

        env.execute("Twin Sync Job");
    }

    private static boolean isDriftSignificant(TwinStateUpdate update) {
        // Drift > 10% on critical KPIs triggers alert
        return update.kpiDriftPercentage > 10.0;
    }
}
```

---

## Step 4: AODT Client

### 4.1 AODT Sync Sink

```python
# sinks/aodt_sink.py
import requests
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TwinStateUpdate:
    cell_id: str
    timestamp: float
    measurements: Dict[str, Any]
    neighbor_cells: list


class AODTClient:
    """NVIDIA AODT REST API client."""

    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def update_cell_state(self, update: TwinStateUpdate) -> dict:
        payload = {
            "cell_id": update.cell_id,
            "timestamp": update.timestamp,
            "measurements": {
                "prb_utilization_pct": update.measurements.get("prb_util"),
                "connected_ues": update.measurements.get("ue_count"),
                "throughput_mbps": update.measurements.get("throughput"),
                "sinr_db": update.measurements.get("avg_sinr"),
                "drop_rate_pct": update.measurements.get("drop_rate"),
            },
            "topology": {"neighbor_cells": update.neighbor_cells},
        }
        resp = requests.post(
            f"{self.endpoint}/cells/{update.cell_id}/state",
            json=payload,
            headers=self.headers,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def run_simulation(self, scenario: dict) -> dict:
        resp = requests.post(
            f"{self.endpoint}/simulate",
            json=scenario,
            headers=self.headers,
            timeout=60,
        )
        return resp.json()
```

---

## Step 5: TimescaleDB for Historical State

### 5.1 TimescaleDB Deployment

```yaml
# timescaledb.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: timescaledb
  namespace: ai-ran-twin
spec:
  serviceName: timescaledb
  replicas: 1
  selector:
    matchLabels:
      app: timescaledb
  template:
    metadata:
      labels:
        app: timescaledb
    spec:
      containers:
      - name: timescaledb
        image: timescale/timescaledb:latest-pg16
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: timescaledb-secret
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ReadWriteOnce]
      resources:
        requests:
          storage: 500Gi
```

### 5.2 Hypertable Schema

```sql
-- schema.sql
CREATE TABLE twin_state_history (
    time        TIMESTAMPTZ NOT NULL,
    cell_id     TEXT NOT NULL,
    prb_util    DOUBLE PRECISION,
    ue_count    INTEGER,
    throughput  DOUBLE PRECISION,
    sinr_db     DOUBLE PRECISION,
    drop_rate   DOUBLE PRECISION,
    twin_synced BOOLEAN DEFAULT true,
    drift_pct   DOUBLE PRECISION
);

SELECT create_hypertable('twin_state_history', 'time');

-- Retention: keep 90 days of high-frequency data, downsample older data
SELECT add_retention_policy('twin_state_history', INTERVAL '90 days');

-- Continuous aggregate for hourly rollups
CREATE MATERIALIZED VIEW twin_state_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    cell_id,
    AVG(prb_util) AS avg_prb,
    AVG(ue_count) AS avg_ues,
    AVG(throughput) AS avg_throughput,
    AVG(sinr_db) AS avg_sinr
FROM twin_state_history
GROUP BY bucket, cell_id;

SELECT add_continuous_aggregate_policy('twin_state_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
```

---

## Step 6: Drift Detection and Alerting

### 6.1 Drift Detector

```python
# drift/detector.py
"""
Compares physical RAN state against twin prediction to detect drift.
"""
import numpy as np
from dataclasses import dataclass


@dataclass
class DriftReport:
    cell_id: str
    kpi_drift_pct: float
    affected_kpis: list
    severity: str  # 'info', 'warning', 'critical'
    recommended_action: str


class DriftDetector:
    """Detects when digital twin diverges from physical network."""

    THRESHOLDS = {
        "info": 5.0,
        "warning": 10.0,
        "critical": 25.0,
    }

    def detect(
        self,
        cell_id: str,
        physical_state: dict,
        twin_prediction: dict,
    ) -> DriftReport:
        drifts = {}
        for kpi in ["prb_util", "ue_count", "throughput", "sinr_db"]:
            p = physical_state.get(kpi, 0)
            t = twin_prediction.get(kpi, 0)
            if t != 0:
                drifts[kpi] = abs(p - t) / abs(t) * 100

        max_drift_kpi = max(drifts, key=drifts.get)
        max_drift_pct = drifts[max_drift_kpi]

        if max_drift_pct >= self.THRESHOLDS["critical"]:
            severity = "critical"
            action = "Pause agent actions; trigger full twin resync"
        elif max_drift_pct >= self.THRESHOLDS["warning"]:
            severity = "warning"
            action = "Schedule twin recalibration within 1 hour"
        elif max_drift_pct >= self.THRESHOLDS["info"]:
            severity = "info"
            action = "Log for weekly twin model retraining"
        else:
            severity = "ok"
            action = "No action needed"

        return DriftReport(
            cell_id=cell_id,
            kpi_drift_pct=max_drift_pct,
            affected_kpis=[k for k, v in drifts.items() if v > 5.0],
            severity=severity,
            recommended_action=action,
        )
```

### 6.2 Prometheus Alerts

```yaml
# twin-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: twin-sync-alerts
  namespace: ai-ran-twin
spec:
  groups:
  - name: twin.rules
    rules:
    - alert: TwinDriftWarning
      expr: twin_drift_pct > 10
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Digital twin drift detected in {{ $labels.cell_id }}"
        description: "{{ $value }}% drift — twin predictions diverging from physical"

    - alert: TwinDriftCritical
      expr: twin_drift_pct > 25
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "Critical twin drift in {{ $labels.cell_id }}"
        description: "Pause agent actions until twin is resynced"

    - alert: TwinSyncLag
      expr: twin_sync_lag_seconds > 10
      for: 3m
      labels:
        severity: warning
      annotations:
        summary: "Twin sync lagging by {{ $value }}s"

    - alert: TwinSyncDown
      expr: up{job="twin-sync-agent"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Twin sync agent down"
```

---

## Step 7: End-to-End Verification

```bash
# 1. Produce a test E2 event
kubectl exec -n near-rt-ric deployment/e2-producer -- \
  python -c "from e2_producer import send_test_event; send_test_event()"

# 2. Verify Kafka received it
kubectl exec -n kafka -it oran-twin-kafka-0 -- \
  bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
    --topic e2-telemetry --from-beginning --max-messages 1

# 3. Check Flink job status
kubectl port-forward -n ai-ran-twin svc/twin-sync-flink-rest 8081:8081
# Open http://localhost:8081

# 4. Query TimescaleDB
kubectl exec -n ai-ran-twin statefulset/timescaledb -- \
  psql -U postgres -c "SELECT count(*) FROM twin_state_history WHERE time > now() - interval '5 minutes'"

# 5. Simulate action via AODT
curl -X POST https://aodt.aws.nvidia.com/api/v1/simulate \
  -H "Authorization: Bearer $AODT_KEY" \
  -d '{"scenario": "activate_sleeping_cell", "cell_id": "Cell_Stadium_02"}'
```

---

## Exercises

1. **Bidirectional sync**: Extend to push twin recommendations back to RIC
2. **ML-based drift detection**: Train anomaly detector on historical drift patterns
3. **Multi-cluster sync**: Sync multiple regional twins with a global twin
4. **Cost tracking**: Report per-cell AODT API usage for chargeback
5. **Replay mode**: Load historical telemetry to test agent logic offline

---

## References

- [NVIDIA AODT API Documentation](https://developer.nvidia.com/blog/5-new-digital-twin-products-developers-can-use-to-build-6g-networks/)
- [Strimzi Kafka Operator](https://strimzi.io/)
- [Apache Flink on K8S](https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/resource-providers/native_kubernetes/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
