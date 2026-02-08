# O-RAN Performance Optimization Framework

## Overview
This document provides a comprehensive performance optimization framework for O-RAN systems, covering network layer optimization, compute layer optimization, application layer tuning, and monitoring toolchains.

## Network Performance Optimization

### Network Interface Tuning
```bash
#!/bin/bash
# O-RAN network interface optimization script

optimize_network_interfaces() {
    echo "Optimizing network interfaces for O-RAN performance..."
    
    # Identify O-RAN interfaces
    oran_interfaces=$(ip link show | grep -E "(eth|enp|eno)" | grep -v "lo" | cut -d: -f2 | tr -d ' ')
    
    for interface in $oran_interfaces; do
        echo "Optimizing interface: $interface"
        
        # Disable network offloading features that can cause issues
        ethtool -K $interface gro off
        ethtool -K $interface lro off
        ethtool -K $interface tso off
        ethtool -K $interface gso off
        
        # Set optimal ring buffer sizes
        ethtool -G $interface rx 4096 tx 4096
        
        # Configure interrupt coalescing
        ethtool -C $interface rx-usecs 10 tx-usecs 10
        
        # Set maximum transmission unit
        ip link set dev $interface mtu 9000  # Jumbo frames
        
        # Apply traffic control settings
        tc qdisc add dev $interface root mq
        tc qdisc add dev $interface ingress
        
        # Set up priority queuing for O-RAN traffic
        for i in {0..7}; do
            tc class add dev $interface parent 1: classid 1:$((i+1)) htb rate 10gbit ceil 10gbit
        done
        
        # Mark O-RAN traffic priorities
        tc filter add dev $interface protocol ip parent 1: prio 1 u32 match ip dport 36421 0xffff flowid 1:1  # E2
        tc filter add dev $interface protocol ip parent 1: prio 1 u32 match ip dport 38472 0xffff flowid 1:2  # F1
        tc filter add dev $interface protocol ip parent 1: prio 1 u32 match ip dport 37521 0xffff flowid 1:3  # O-FH
    done
}

# Kernel network parameter tuning
tune_kernel_network_parameters() {
    echo "Tuning kernel network parameters..."
    
    # Increase network buffer sizes
    echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
    echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
    echo 'net.core.rmem_default = 134217728' >> /etc/sysctl.conf
    echo 'net.core.wmem_default = 134217728' >> /etc/sysctl.conf
    
    # TCP optimizations
    echo 'net.ipv4.tcp_rmem = 4096 87380 134217728' >> /etc/sysctl.conf
    echo 'net.ipv4.tcp_wmem = 4096 65536 134217728' >> /etc/sysctl.conf
    echo 'net.ipv4.tcp_congestion_control = bbr' >> /etc/sysctl.conf
    echo 'net.ipv4.tcp_slow_start_after_idle = 0' >> /etc/sysctl.conf
    
    # Reduce TCP delays
    echo 'net.ipv4.tcp_low_latency = 1' >> /etc/sysctl.conf
    echo 'net.ipv4.tcp_fin_timeout = 15' >> /etc/sysctl.conf
    echo 'net.ipv4.tcp_keepalive_time = 600' >> /etc/sysctl.conf
    
    # Apply changes
    sysctl -p
}

# NUMA-aware network optimization
optimize_numa_network_binding() {
    echo "Optimizing NUMA binding for network interfaces..."
    
    # Get CPU topology
    cpu_info=$(lscpu)
    sockets=$(echo "$cpu_info" | grep "Socket(s):" | awk '{print $2}')
    cores_per_socket=$(echo "$cpu_info" | grep "Core(s) per socket:" | awk '{print $4}')
    
    # Bind network interrupts to specific CPU cores
    interface_index=0
    for interface in $(ls /sys/class/net/ | grep -E "^(eth|enp|eno)" | grep -v "lo"); do
        irq_list=$(grep "$interface" /proc/interrupts | awk '{print $1}' | sed 's/://' | head -4)
        
        core_index=$((interface_index * 2))
        for irq in $irq_list; do
            echo $core_index > /proc/irq/$irq/smp_affinity_list
            core_index=$((core_index + 1))
        done
        
        interface_index=$((interface_index + 1))
    done
}
```

## Compute Performance Optimization

### CPU Affinity and Scheduling
```python
# O-RAN CPU affinity and process scheduling optimizer
import psutil
import os
import subprocess
from typing import Dict, List

class ORANComputeOptimizer:
    def __init__(self):
        self.cpu_topology = self.get_cpu_topology()
        self.process_mappings = {
            'near-rt-ric': {'cores': [0, 1, 2, 3], 'priority': -10},
            'o-du': {'cores': [4, 5, 6, 7], 'priority': -5},
            'o-cu': {'cores': [8, 9, 10, 11], 'priority': -5},
            'smo': {'cores': [12, 13], 'priority': 0}
        }
    
    def get_cpu_topology(self) -> Dict:
        """Get CPU topology information"""
        try:
            # Get NUMA node information
            numa_info = subprocess.check_output(['numactl', '--hardware'], text=True)
            
            topology = {
                'sockets': int(subprocess.check_output(['lscpu', '-p=SOCKET'], text=True).strip().split('\n')[-1]) + 1,
                'cores_per_socket': int(subprocess.check_output(['lscpu', '-p=CORE'], text=True).strip().split('\n')[-1]) + 1,
                'threads_per_core': psutil.cpu_count() // (psutil.cpu_count(logical=False) or 1),
                'numa_nodes': {}
            }
            
            # Parse NUMA information
            for line in numa_info.split('\n'):
                if 'available:' in line:
                    numa_count = int(line.split(':')[1].split()[0])
                    topology['numa_nodes'] = {i: [] for i in range(numa_count)}
                elif 'node ' in line and 'cpus:' in line:
                    parts = line.split()
                    node_id = int(parts[1])
                    if len(parts) > 3:
                        cpus = [int(cpu.strip()) for cpu in parts[3].split(',')]
                        topology['numa_nodes'][node_id] = cpus
            
            return topology
        except Exception as e:
            print(f"Error getting CPU topology: {e}")
            return {'sockets': 1, 'cores_per_socket': psutil.cpu_count(), 'threads_per_core': 1, 'numa_nodes': {0: list(range(psutil.cpu_count()))}}
    
    def set_process_affinity(self, process_name: str, pid: int):
        """Set CPU affinity for a process"""
        if process_name in self.process_mappings:
            cores = self.process_mappings[process_name]['cores']
            try:
                process = psutil.Process(pid)
                process.cpu_affinity(cores)
                print(f"Set {process_name} (PID: {pid}) affinity to cores {cores}")
                
                # Set process priority
                priority = self.process_mappings[process_name]['priority']
                os.system(f"renice {priority} {pid}")
                print(f"Set {process_name} (PID: {pid}) priority to {priority}")
                
                return True
            except Exception as e:
                print(f"Error setting affinity for {process_name}: {e}")
                return False
        return False
    
    def optimize_system_processes(self):
        """Optimize all O-RAN related processes"""
        print("Optimizing O-RAN process scheduling...")
        
        # Find O-RAN processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                process_name = proc.info['name'].lower()
                pid = proc.info['pid']
                
                # Match O-RAN components
                if 'ric' in process_name and 'near' in process_name:
                    self.set_process_affinity('near-rt-ric', pid)
                elif 'o-du' in process_name or 'odu' in process_name:
                    self.set_process_affinity('o-du', pid)
                elif 'o-cu' in process_name or 'ocu' in process_name:
                    self.set_process_affinity('o-cu', pid)
                elif 'smo' in process_name:
                    self.set_process_affinity('smo', pid)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def tune_kernel_scheduler(self):
        """Tune kernel scheduler for low latency"""
        scheduler_settings = {
            'kernel.sched_migration_cost_ns': '5000000',
            'kernel.sched_autogroup_enabled': '0',
            'kernel.sched_child_runs_first': '0',
            'kernel.sched_cfs_bandwidth_slice_us': '3000',
            'kernel.sched_rt_runtime_us': '950000',
            'kernel.sched_rt_period_us': '1000000'
        }
        
        for param, value in scheduler_settings.items():
            try:
                with open(f'/proc/sys/{param.replace(".", "/")}', 'w') as f:
                    f.write(value)
                print(f"Set {param} = {value}")
            except Exception as e:
                print(f"Error setting {param}: {e}")

# Usage example
def main():
    optimizer = ORANComputeOptimizer()
    
    # Display CPU topology
    print("CPU Topology:")
    print(f"Sockets: {optimizer.cpu_topology['sockets']}")
    print(f"Cores per socket: {optimizer.cpu_topology['cores_per_socket']}")
    print(f"Threads per core: {optimizer.cpu_topology['threads_per_core']}")
    print(f"NUMA nodes: {optimizer.cpu_topology['numa_nodes']}")
    
    # Optimize processes
    optimizer.optimize_system_processes()
    
    # Tune kernel scheduler
    optimizer.tune_kernel_scheduler()

if __name__ == "__main__":
    main()
```

## Application Layer Optimization

### Container Resource Optimization
```yaml
# Kubernetes resource optimization for O-RAN components
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oran-near-rt-ric
spec:
  replicas: 3
  selector:
    matchLabels:
      app: near-rt-ric
  template:
    metadata:
      labels:
        app: near-rt-ric
    spec:
      containers:
      - name: near-rt-ric
        image: oran/near-rt-ric:latest
        resources:
          requests:
            cpu: "2"
            memory: "4Gi"
            ephemeral-storage: "2Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
            ephemeral-storage: "4Gi"
        env:
        - name: GOGC
          value: "20"  # Aggressive garbage collection
        - name: GOMAXPROCS
          value: "4"   # Match CPU limit
        ports:
        - containerPort: 36421
          name: e2-interface
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: near-rt-ric-service
spec:
  selector:
    app: near-rt-ric
  ports:
  - port: 36421
    targetPort: 36421
    name: e2-interface
  type: ClusterIP
```

### Memory Optimization Techniques
```bash
#!/bin/bash
# O-RAN memory optimization script

optimize_memory_settings() {
    echo "Optimizing memory settings for O-RAN..."
    
    # Configure huge pages for better performance
    configure_hugepages() {
        echo "Configuring huge pages..."
        
        # Calculate huge page requirements (assuming 2MB pages)
        total_memory_gb=$(free -g | awk '/^Mem:/{print $2}')
        hugepages_needed=$((total_memory_gb * 512))  # 512 pages per GB
        
        echo "vm.nr_hugepages = $hugepages_needed" >> /etc/sysctl.conf
        
        # Reserve huge pages at boot
        echo "hugepages = $hugepages_needed" >> /etc/default/grub
        update-grub
        
        # Mount huge pages
        mkdir -p /dev/hugepages
        mount -t hugetlbfs none /dev/hugepages
    }
    
    # Optimize memory allocation
    tune_memory_allocator() {
        echo "Tuning memory allocator settings..."
        
        # For applications using jemalloc or similar
        echo 'export MALLOC_CONF="background_thread:true,narenas:4"' >> /etc/profile.d/oran-malloc.sh
        
        # For Go applications
        echo 'export GOGC=20' >> /etc/profile.d/oran-go.sh
        echo 'export GOMEMLIMIT=7GiB' >> /etc/profile.d/oran-go.sh
    }
    
    # Configure memory overcommit
    configure_memory_overcommit() {
        echo "Configuring memory overcommit settings..."
        
        # Conservative overcommit (recommended for telecom)
        echo 'vm.overcommit_memory = 2' >> /etc/sysctl.conf
        echo 'vm.overcommit_ratio = 80' >> /etc/sysctl.conf
        
        # Swappiness tuning
        echo 'vm.swappiness = 1' >> /etc/sysctl.conf  # Minimal swapping
    }
    
    # Execute optimizations
    configure_hugepages
    tune_memory_allocator
    configure_memory_overcommit
    
    # Apply changes
    sysctl -p
}

# NUMA memory binding optimization
optimize_numa_memory_binding() {
    echo "Optimizing NUMA memory binding..."
    
    # Bind processes to local memory
    for pid in $(pgrep -f "near-rt-ric|o-du|o-cu"); do
        # Get process NUMA node preference
        numa_node=$(ps -o psr= -p $pid | xargs numactl --hardware | grep "node .* cpus" | head -1 | cut -d' ' -f2)
        
        # Bind to local memory
        numactl --cpunodebind=$numa_node --membind=$numa_node --pid=$pid
        echo "Bound PID $pid to NUMA node $numa_node"
    done
}
```

## Monitoring and Performance Analysis

### Performance Dashboard Configuration
```json
{
  "dashboard_configuration": {
    "title": "O-RAN Performance Optimization Dashboard",
    "refresh_interval": "30s",
    "time_range": "1h",
    "panels": [
      {
        "title": "CPU Utilization by Component",
        "type": "timeseries",
        "datasource": "prometheus",
        "targets": [
          {
            "expr": "rate(process_cpu_seconds_total{job=~\"near-rt-ric|o-du|o-cu\"}[5m]) * 100",
            "legendFormat": "{{job}}"
          }
        ],
        "thresholds": {
          "warning": 70,
          "critical": 85
        }
      },
      {
        "title": "Memory Usage Analysis",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes{job=~\"near-rt-ric|o-du|o-cu\"}",
            "legendFormat": "{{job}} RSS"
          },
          {
            "expr": "go_memstats_alloc_bytes{job=~\"near-rt-ric|o-du|o-cu\"}",
            "legendFormat": "{{job}} Allocated"
          }
        ]
      },
      {
        "title": "Network Performance Metrics",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(container_network_receive_bytes_total{container=~\"near-rt-ric|o-du|o-cu\"}[5m])",
            "legendFormat": "{{container}} RX"
          },
          {
            "expr": "rate(container_network_transmit_bytes_total{container=~\"near-rt-ric|o-du|o-cu\"}[5m])",
            "legendFormat": "{{container}} TX"
          }
        ]
      },
      {
        "title": "Latency Distribution",
        "type": "heatmap",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(e2_interface_latency_seconds_bucket[5m]))",
            "legendFormat": "E2 95th Percentile"
          },
          {
            "expr": "histogram_quantile(0.95, rate(f1_interface_latency_seconds_bucket[5m]))",
            "legendFormat": "F1 95th Percentile"
          }
        ]
      }
    ]
  }
}
```

### Automated Performance Tuning
```python
# Automated performance tuning system
import time
import json
from datetime import datetime, timedelta
import numpy as np

class ORANPerformanceTuner:
    def __init__(self, monitoring_client):
        self.monitoring_client = monitoring_client
        self.tuning_history = []
        self.performance_thresholds = {
            'cpu_utilization': 80,
            'memory_utilization': 85,
            'network_latency': 5.0,  # ms
            'throughput_degradation': 0.1  # 10% decrease
        }
    
    def collect_performance_metrics(self):
        """Collect current performance metrics"""
        metrics = {
            'timestamp': datetime.utcnow(),
            'cpu_utilization': self.get_average_cpu_utilization(),
            'memory_utilization': self.get_average_memory_utilization(),
            'network_latency': self.get_average_network_latency(),
            'throughput': self.get_current_throughput(),
            'error_rate': self.get_error_rate()
        }
        return metrics
    
    def analyze_performance_trends(self, metrics_history):
        """Analyze performance trends and identify optimization opportunities"""
        recommendations = []
        
        # CPU utilization analysis
        cpu_trend = self.calculate_trend([m['cpu_utilization'] for m in metrics_history[-10:]])
        if cpu_trend > 5:  # Increasing trend
            recommendations.append({
                'type': 'cpu_scaling',
                'action': 'consider_horizontal scaling',
                'urgency': 'medium',
                'impact': 'performance'
            })
        elif cpu_trend < -5:  # Decreasing trend
            recommendations.append({
                'type': 'resource_optimization',
                'action': 'consider rightsizing instances',
                'urgency': 'low',
                'impact': 'cost'
            })
        
        # Memory analysis
        memory_avg = np.mean([m['memory_utilization'] for m in metrics_history[-5:]])
        if memory_avg > self.performance_thresholds['memory_utilization']:
            recommendations.append({
                'type': 'memory_optimization',
                'action': 'tune garbage collection or increase memory',
                'urgency': 'high',
                'impact': 'stability'
            })
        
        # Network analysis
        latency_avg = np.mean([m['network_latency'] for m in metrics_history[-5:]])
        if latency_avg > self.performance_thresholds['network_latency']:
            recommendations.append({
                'type': 'network_tuning',
                'action': 'optimize network interface settings',
                'urgency': 'high',
                'impact': 'performance'
            })
        
        return recommendations
    
    def apply_performance_tunings(self, recommendations):
        """Apply recommended performance tunings"""
        applied_tunings = []
        
        for recommendation in recommendations:
            tuning_result = self.apply_single_tuning(recommendation)
            if tuning_result:
                applied_tunings.append(tuning_result)
                self.tuning_history.append({
                    'timestamp': datetime.utcnow(),
                    'recommendation': recommendation,
                    'result': tuning_result
                })
        
        return applied_tunings
    
    def apply_single_tuning(self, recommendation):
        """Apply a single performance tuning"""
        try:
            if recommendation['type'] == 'cpu_scaling':
                # Implement horizontal scaling logic
                return self.scale_horizontally()
            elif recommendation['type'] == 'memory_optimization':
                # Apply memory tuning
                return self.tune_memory_settings()
            elif recommendation['type'] == 'network_tuning':
                # Apply network optimization
                return self.optimize_network_settings()
            else:
                return None
        except Exception as e:
            print(f"Error applying tuning {recommendation['type']}: {e}")
            return None
    
    def generate_performance_report(self, metrics_history, recommendations):
        """Generate comprehensive performance optimization report"""
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'period_analyzed': f"{len(metrics_history)} data points",
            'current_performance': self.summarize_current_performance(metrics_history[-1]),
            'trends_identified': self.analyze_performance_trends(metrics_history),
            'recommendations_applied': len(recommendations),
            'estimated_performance_gain': self.estimate_performance_improvement(recommendations)
        }
        
        return json.dumps(report, indent=2)
    
    # Helper methods (implementations would depend on specific monitoring system)
    def get_average_cpu_utilization(self):
        return np.random.uniform(40, 90)  # Placeholder
    
    def get_average_memory_utilization(self):
        return np.random.uniform(50, 95)  # Placeholder
    
    def get_average_network_latency(self):
        return np.random.uniform(1, 10)   # Placeholder
    
    def get_current_throughput(self):
        return np.random.uniform(1000, 5000)  # Placeholder
    
    def get_error_rate(self):
        return np.random.uniform(0, 0.05)     # Placeholder
    
    def calculate_trend(self, values):
        if len(values) < 2:
            return 0
        return np.polyfit(range(len(values)), values, 1)[0]
    
    def summarize_current_performance(self, latest_metrics):
        return {
            'overall_health': 'good' if latest_metrics['cpu_utilization'] < 80 else 'warning',
            'bottlenecks': self.identify_bottlenecks(latest_metrics),
            'resource_utilization': {
                'cpu': f"{latest_metrics['cpu_utilization']:.1f}%",
                'memory': f"{latest_metrics['memory_utilization']:.1f}%",
                'network': f"{latest_metrics['network_latency']:.2f}ms avg latency"
            }
        }
    
    def identify_bottlenecks(self, metrics):
        bottlenecks = []
        if metrics['cpu_utilization'] > 85:
            bottlenecks.append('CPU')
        if metrics['memory_utilization'] > 90:
            bottlenecks.append('Memory')
        if metrics['network_latency'] > 5:
            bottlenecks.append('Network')
        return bottlenecks
    
    def estimate_performance_improvement(self, recommendations):
        # Simplified estimation logic
        estimated_improvement = 0
        for rec in recommendations:
            if rec['type'] == 'cpu_scaling':
                estimated_improvement += 15  # 15% CPU improvement
            elif rec['type'] == 'memory_optimization':
                estimated_improvement += 10  # 10% memory efficiency
            elif rec['type'] == 'network_tuning':
                estimated_improvement += 20  # 20% network performance
        return min(estimated_improvement, 50)  # Cap at 50%

# Usage example
def main():
    # This would integrate with your monitoring system
    tuner = ORANPerformanceTuner(monitoring_client=None)
    
    # Collect metrics over time
    metrics_history = []
    for _ in range(24):  # 24 hours of data
        metrics = tuner.collect_performance_metrics()
        metrics_history.append(metrics)
        time.sleep(300)  # 5-minute intervals
    
    # Analyze and optimize
    recommendations = tuner.analyze_performance_trends(metrics_history)
    applied_tunings = tuner.apply_performance_tunings(recommendations)
    
    # Generate report
    report = tuner.generate_performance_report(metrics_history, recommendations)
    print("Performance Optimization Report:")
    print(report)

if __name__ == "__main__":
    main()
```

This comprehensive performance optimization framework provides systematic approaches to optimize O-RAN system performance across network, compute, and application layers while maintaining monitoring and automated tuning capabilities.