# Lab 2: NVIDIA ARC K8S Deployment

> Deploy GPU-accelerated baseband and AI workloads on NVIDIA ARC hardware

## Overview

This lab configures a Kubernetes node running **NVIDIA ARC-Compact** to host both:
- **GPU baseband processing** (cuMAC L2 scheduler)
- **Edge AI inference** (TensorRT models for B2B customers)

Using **NVIDIA MIG (Multi-Instance GPU)** to partition a single L4 GPU into isolated slices.

## Prerequisites

- NVIDIA ARC-Compact hardware with L4 GPU + Grace CPU
- Ubuntu 22.04 with real-time kernel (`linux-image-rt-amd64`)
- NVIDIA driver 550+, CUDA 12.4+, NVIDIA Container Toolkit
- Kubernetes 1.28+ with NVIDIA GPU Operator v24.3+

---

## Step 1: Node Configuration

### 1.1 Real-Time Kernel Setup

```bash
# Install real-time kernel on worker node
sudo apt install -y linux-image-6.5.0-rt-amd64 linux-headers-6.5.0-rt-amd64

# GRUB default to RT kernel
sudo sed -i 's/GRUB_DEFAULT=0/GRUB_DEFAULT="1>2"/' /etc/default/grub
sudo update-grub

# Verify RT kernel after reboot
uname -r
# Expected: 6.5.0-rt-amd64

# Check PREEMPT_RT
cat /sys/kernel/realtime
# Expected: 1
```

### 1.2 PTP Time Synchronization (nanosecond precision)

```bash
# Install linuxptp
sudo apt install -y linuxptp

# Configure PTP for fronthaul sync
cat <<EOF | sudo tee /etc/linuxptp/ptp4l-arc.conf
[global]
tx_timestamp_timeout 50
use_syslog 0
verbose 1
summary_interval 0
dataset_comparison ieee1588
[GmPll]
network_transport L2
delay_mechanism P2P
EOF

# Start ptp4l on fronthaul NIC
sudo systemctl enable --now ptp4l@eth1.service
```

### 1.3 CPU Isolation for Baseband Pods

```bash
# Reserve cores 0-3 for system, dedicate 4-71 for baseband
sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT=""/GRUB_CMDLINE_LINUX_DEFAULT="isolcpus=4-71 nohz_full=4-71 rcu_nocbs=4-71"/' /etc/default/grub
sudo update-grub
# Reboot required
```

---

## Step 2: GPU Operator with MIG

### 2.1 Install GPU Operator

```bash
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator --create-namespace \
  --set mig.strategy=mixed \
  --set driver.enabled=true \
  --set toolkit.enabled=true \
  --set dcgmExporter.enabled=true \
  --set nodeSelector.'nvidia\.com/gpu\.product'=NVIDIA-L4 \
  --version 24.3.0
```

### 2.2 Configure MIG Profiles for L4

```yaml
# mig-config.yaml
version: v1
mig_configs:
  # L4 has 24GB VRAM; partition for RAN + AI coexistence
  "1g.6gb+1g.6gb+1g.6gb+1g.6gb":
    - device_filter: "NVIDIA-L4"
      count: 4
      # 4 slices of 6GB each:
      # slice 0: cuMAC baseband (RAN)
      # slice 1: cuPHY physical layer (RAN)
      # slice 2: TensorRT inference (B2B AI service)
      # slice 3: Digital twin agent
```

```bash
kubectl apply -f mig-config.yaml

# Verify MIG instances
kubectl get nodes -l nvidia.com/gpu.product=NVIDIA-L4 \
  -o json | jq '.items[0].status.allocatable | with_entries(select(.key | startswith("nvidia.com/mig")))'
```

Expected output:
```json
{
  "nvidia.com/mig-1g.6gb": 4
}
```

---

## Step 3: Network Configuration

### 3.1 Multus CNI for Multi-Network Pods

```bash
# Install Multus
kubectl apply -f https://raw.githubusercontent.com/k8snetworkplumbingwg/multus-cni/master/deployments/multus-daemonset.yml
```

### 3.2 SR-IOV for Fronthaul (eCPRI)

```yaml
# sriov-fronthaul-net.yaml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: sriov-fronthaul
  namespace: ai-ran-cell-site
  annotations:
    k8s.v1.cni.cncf.io/resourceName: nvidia.com/sriov_fronthaul
spec:
  config: '{
    "type": "sriov",
    "cniVersion": "0.3.1",
    "name": "fronthaul",
    "vlan": 100,
    "ipam": {
      "type": "static",
      "addresses": [
        {"address": "10.100.1.10/24", "gateway": "10.100.1.1"}
      ]
    }
  }'
```

### 3.3 DPDK for Low-Latency Data Plane

```bash
# Bind fronthaul NIC to vfio-pci for DPDK
sudo modprobe vfio-pci
echo "0000:03:00.0" | sudo tee /sys/bus/pci/devices/0000:03:00.0/driver/unbind
echo "vfio-pci" | sudo tee /sys/bus/pci/devices/0000:03:00.0/driver_override
echo "0000:03:00.0" | sudo tee /sys/bus/pci/drivers/vfio-pci/bind
```

---

## Step 4: Deploy Baseband + AI Workloads

### 4.1 cuMAC Baseband Pod

```yaml
# cumac-baseband.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cumac-baseband
  namespace: ai-ran-cell-site
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cumac-baseband
  template:
    metadata:
      labels:
        app: cumac-baseband
      annotations:
        k8s.v1.cni.cncf.io/networks: sriov-fronthaul
        cpu-load-balancing.crio.io: "disable"
        cpu-quota.crio.io: "disable"
    spec:
      runtimeClassName: nvidia-rt
      nodeSelector:
        nvidia.com/gpu.product: NVIDIA-L4
      containers:
      - name: cumac
        image: nvcr.io/nvidia/aerial/cumac:24.07
        resources:
          limits:
            nvidia.com/mig-1g.6gb: 1
            cpu: "16"
            memory: "16Gi"
            hugepages-1Gi: "8Gi"
          requests:
            nvidia.com/mig-1g.6gb: 1
            cpu: "16"
            memory: "16Gi"
            hugepages-1Gi: "8Gi"
        env:
        - name: NVIDIA_VISIBLE_DEVICES
          value: "all"
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        - name: CELL_ID
          value: "Cell_Stadium_01"
        - name: SECTOR_COUNT
          value: "3"
        - name: CARRIER_BANDWIDTH_MHZ
          value: "40"
        securityContext:
          capabilities:
            add: ["IPC_LOCK", "SYS_NICE"]
        volumeMounts:
        - name: hugepages
          mountPath: /dev/hugepages
      volumes:
      - name: hugepages
        emptyDir:
          medium: HugePages
```

### 4.2 Edge AI Inference Pod (B2B Service)

```yaml
# edge-ai-inference.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: edge-ai-inference
  namespace: ai-ran-cell-site
spec:
  replicas: 1
  selector:
    matchLabels:
      app: edge-ai-inference
  template:
    metadata:
      labels:
        app: edge-ai-inference
    spec:
      runtimeClassName: nvidia
      nodeSelector:
        nvidia.com/gpu.product: NVIDIA-L4
      containers:
      - name: triton-server
        image: nvcr.io/nvidia/tritonserver:24.05-py3
        args: ["tritonserver", "--model-repository=/models"]
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 8002
          name: metrics
        resources:
          limits:
            nvidia.com/mig-1g.6gb: 1
            cpu: "4"
            memory: "8Gi"
        env:
        - name: TRITON_MODEL_CONTROL_MODE
          value: "explicit"
        volumeMounts:
        - name: models
          mountPath: /models
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: ai-models-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: edge-ai-inference
  namespace: ai-ran-cell-site
spec:
  type: LoadBalancer
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  selector:
    app: edge-ai-inference
```

---

## Step 5: Observability

### 5.1 DCGM Exporter (already installed with GPU Operator)

```bash
# Verify DCGM is running
kubectl get pods -n gpu-operator -l app=nvidia-dcgm-exporter

# Check GPU metrics
kubectl get --raw "/api/v1/namespaces/gpu-operator/services/nvidia-dcgm-exporter:9400/proxy/metrics" \
  | grep DCGM_FI_DEV_GPU_UTIL
```

### 5.2 Grafana Dashboard

```bash
# Import NVIDIA GPU dashboard
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/dcgm-exporter/main/grafana/dcgm-exporter-dashboard.json

# Access via port-forward
kubectl port-forward svc/grafana -n monitoring 3000:3000
```

### 5.3 Custom Prometheus Alerts

```yaml
# gpu-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: ai-ran-gpu-alerts
  namespace: ai-ran-cell-site
spec:
  groups:
  - name: gpu.rules
    rules:
    - alert: GPUBasebandUtilizationHigh
      expr: DCGM_FI_DEV_GPU_UTIL{pod=~"cumac-.*"} > 95
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Baseband GPU utilization above 95%"
        description: "Risk of missed subframe deadlines"

    - alert: GPUMemoryLeak
      expr: increase(DCGM_FI_DEV_FB_USED{pod=~"edge-ai-.*"}[1h]) > 1024
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "AI inference pod memory leak suspected"

    - alert: GPUTemperatureHigh
      expr: DCGM_FI_DEV_GPU_TEMP > 80
      for: 2m
      labels:
        severity: warning
      annotations:
        summary: "GPU temperature above 80C — check cooling"
```

---

## Step 6: Power and Thermal Management

### 6.1 GPU Power Capping

```bash
# Cap L4 GPU at 72W (cell-site power budget)
sudo nvidia-smi -pl 72

# Verify
nvidia-smi -q -d POWER | grep "Power Limit"
```

### 6.2 K8S Power Capping via DaemonSet

```yaml
# gpu-power-cap-daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: gpu-power-cap
  namespace: gpu-operator
spec:
  selector:
    matchLabels:
      app: gpu-power-cap
  template:
    metadata:
      labels:
        app: gpu-power-cap
    spec:
      nodeSelector:
        nvidia.com/gpu.product: NVIDIA-L4
      hostPID: true
      containers:
      - name: power-cap
        image: busybox
        command: ["/bin/sh", "-c"]
        args:
        - |
          nvidia-smi -pl 72
          while true; do sleep 3600; done
        securityContext:
          privileged: true
        volumeMounts:
        - name: dev
          mountPath: /dev
      volumes:
      - name: dev
        hostPath:
          path: /dev
```

---

## Verification

```bash
# 1. Verify node is Ready with MIG devices
kubectl get nodes -l nvidia.com/gpu.product=NVIDIA-L4 -o wide

# 2. Verify cuMAC pod is running
kubectl get pods -n ai-ran-cell-site -l app=cumac-baseband

# 3. Check baseband latency
kubectl logs -n ai-ran-cell-site deployment/cumac-baseband | grep "subframe_latency_us"

# 4. Verify AI inference endpoint
kubectl exec -n ai-ran-cell-site deployment/edge-ai-inference -- \
  curl -s localhost:8000/v2/health/ready

# 5. Check GPU utilization breakdown
kubectl get --raw "/api/v1/namespaces/gpu-operator/services/nvidia-dcgm-exporter:9400/proxy/metrics" \
  | grep "DCGM_FI_DEV_GPU_UTIL"
```

---

## Troubleshooting

| Symptom | Cause | Fix |
|:---|:---|:---|
| cuMAC pod stuck in ContainerCreating | MIG not initialized | Restart GPU Operator: `kubectl rollout restart ds/nvidia-operator-validator -n gpu-operator` |
| Subframe deadline missed | Non-RT kernel | Ensure real-time kernel is active: `uname -r` should show `-rt` |
| AI inference latency spikes | MIG slice too small | Increase MIG profile from 1g.6gb to 1g.12gb |
| SR-IOV not attaching | VF not bound | Re-run VF bind: `echo 4 > /sys/class/net/eth1/device/sriov_numvfs` |
| PTP not syncing | Wrong NIC selected | Verify PTP-capable NIC is used for fronthaul |

---

## Next Lab

→ [Lab 3: Telecom-LLM Deployment](./telecom-llm-deployment.md)

## References

- [NVIDIA ARC-Compact Deployment Guide](https://developer.nvidia.com/blog/deploy-ai-ran-at-cell-sites-with-nvidia-arc-compact/)
- [NVIDIA GPU Operator Documentation](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/)
- [NVIDIA Aerial CUDA-Accelerated RAN (GitHub)](https://github.com/NVIDIA/aerial-cuda-accelerated-ran)
- [Multus CNI Documentation](https://github.com/k8snetworkplumbingwg/multus-cni)
