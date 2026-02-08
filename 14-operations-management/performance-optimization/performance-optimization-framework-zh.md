# O-RAN 性能优化框架

## 概述
本文档为 O-RAN 系统提供全面的性能优化框架，涵盖网络层优化、计算层优化、应用层调优和监控工具链。

## 网络性能优化

### 网络接口调优
```bash
#!/bin/bash
# O-RAN 网络接口优化脚本

optimize_network_interfaces() {
    echo "优化 O-RAN 性能的网络接口..."
    
    # 识别 O-RAN 接口
    oran_interfaces=$(ip link show | grep -E "(eth|enp|eno)" | grep -v "lo" | cut -d: -f2 | tr -d ' ')
    
    for interface in $oran_interfaces; do
        echo "优化接口: $interface"
        
        # 禁用可能导致问题的网络卸载功能
        ethtool -K $interface gro off
        ethtool -K $interface lro off
        ethtool -K $interface tso off
        ethtool -K $interface gso off
        
        # 设置最佳环形缓冲区大小
        ethtool -G $interface rx 4096 tx 4096
        
        # 配置中断聚合
        ethtool -C $interface rx-usecs 10 tx-usecs 10
        
        # 设置最大传输单元
        ip link set dev $interface mtu 9000  # 巨帧
        
        # 应用流量控制设置
        tc qdisc add dev $interface root mq
        tc qdisc add dev $interface ingress
        
        # 为 O-RAN 流量设置优先级排队
        for i in {0..7}; do
            tc class add dev $interface parent 1: classid 1:$((i+1)) htb rate 10gbit ceil 10gbit
        done
        
        # 标记 O-RAN 流量优先级
        tc filter add dev $interface protocol ip parent 1: prio 1 u32 match ip dport 36421 0xffff flowid 1:1  # E2
        tc filter add dev $interface protocol ip parent 1: prio 1 u32 match ip dport 38472 0xffff flowid 1:2  # F1
        tc filter add dev $interface protocol ip parent 1: prio 1 u32 match ip dport 37521 0xffff flowid 1:3  # O-FH
    done
}

# 内核网络参数调优
tune_kernel_network_parameters() {
    echo "调优内核网络参数..."
    
    # 增加网络缓冲区大小
    echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
    echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
    echo 'net.core.rmem_default = 134217728' >> /etc/sysctl.conf
    echo 'net.core.wmem_default = 134217728' >> /etc/sysctl.conf
    
    # TCP 优化
    echo 'net.ipv4.tcp_rmem = 4096 87380 134217728' >> /etc/sysctl.conf
    echo 'net.ipv4.tcp_wmem = 4096 65536 134217728' >> /etc/sysctl.conf
    echo 'net.ipv4.tcp_congestion_control = bbr' >> /etc/sysctl.conf
    echo 'net.ipv4.tcp_slow_start_after_idle = 0' >> /etc/sysctl.conf
    
    # 减少 TCP 延迟
    echo 'net.ipv4.tcp_low_latency = 1' >> /etc/sysctl.conf
    echo 'net.ipv4.tcp_fin_timeout = 15' >> /etc/sysctl.conf
    echo 'net.ipv4.tcp_keepalive_time = 600' >> /etc/sysctl.conf
    
    # 应用更改
    sysctl -p
}

# NUMA 感知的网络优化
optimize_numa_network_binding() {
    echo "优化网络接口的 NUMA 绑定..."
    
    # 获取 CPU 拓扑
    cpu_info=$(lscpu)
    sockets=$(echo "$cpu_info" | grep "Socket(s):" | awk '{print $2}')
    cores_per_socket=$(echo "$cpu_info" | grep "Core(s) per socket:" | awk '{print $4}')
    
    # 将网络中断绑定到特定 CPU 核心
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

## 计算性能优化

### CPU 亲和性和调度
```python
# O-RAN CPU 亲和性和进程调度优化器
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
        """获取 CPU 拓扑信息"""
        try:
            # 获取 NUMA 节点信息
            numa_info = subprocess.check_output(['numactl', '--hardware'], text=True)
            
            topology = {
                'sockets': int(subprocess.check_output(['lscpu', '-p=SOCKET'], text=True).strip().split('\n')[-1]) + 1,
                'cores_per_socket': int(subprocess.check_output(['lscpu', '-p=CORE'], text=True).strip().split('\n')[-1]) + 1,
                'threads_per_core': psutil.cpu_count() // (psutil.cpu_count(logical=False) or 1),
                'numa_nodes': {}
            }
            
            # 解析 NUMA 信息
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
            print(f"获取 CPU 拓扑时出错: {e}")
            return {'sockets': 1, 'cores_per_socket': psutil.cpu_count(), 'threads_per_core': 1, 'numa_nodes': {0: list(range(psutil.cpu_count()))}}
    
    def set_process_affinity(self, process_name: str, pid: int):
        """为进程设置 CPU 亲和性"""
        if process_name in self.process_mappings:
            cores = self.process_mappings[process_name]['cores']
            try:
                process = psutil.Process(pid)
                process.cpu_affinity(cores)
                print(f"设置 {process_name} (PID: {pid}) 亲和性到核心 {cores}")
                
                # 设置进程优先级
                priority = self.process_mappings[process_name]['priority']
                os.system(f"renice {priority} {pid}")
                print(f"设置 {process_name} (PID: {pid}) 优先级为 {priority}")
                
                return True
            except Exception as e:
                print(f"为 {process_name} 设置亲和性时出错: {e}")
                return False
        return False
    
    def optimize_system_processes(self):
        """优化所有 O-RAN 相关进程"""
        print("优化 O-RAN 进程调度...")
        
        # 查找 O-RAN 进程
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                process_name = proc.info['name'].lower()
                pid = proc.info['pid']
                
                # 匹配 O-RAN 组件
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
        """为低延迟调优内核调度器"""
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
                print(f"设置 {param} = {value}")
            except Exception as e:
                print(f"设置 {param} 时出错: {e}")

# 使用示例
def main():
    optimizer = ORANComputeOptimizer()
    
    # 显示 CPU 拓扑
    print("CPU 拓扑:")
    print(f"插槽: {optimizer.cpu_topology['sockets']}")
    print(f"每插槽核心数: {optimizer.cpu_topology['cores_per_socket']}")
    print(f"每核心线程数: {optimizer.cpu_topology['threads_per_core']}")
    print(f"NUMA 节点: {optimizer.cpu_topology['numa_nodes']}")
    
    # 优化进程
    optimizer.optimize_system_processes()
    
    # 调优内核调度器
    optimizer.tune_kernel_scheduler()

if __name__ == "__main__":
    main()
```

## 应用层优化

### 容器资源优化
```yaml
# O-RAN 组件的 Kubernetes 资源优化
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
          value: "20"  # 积极的垃圾回收
        - name: GOMAXPROCS
          value: "4"   # 匹配 CPU 限制
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

## 监控和性能分析

### 性能仪表板配置
```json
{
  "仪表板配置": {
    "标题": "O-RAN 性能优化仪表板",
    "刷新间隔": "30秒",
    "时间范围": "1小时",
    "面板": [
      {
        "标题": "按组件划分的 CPU 利用率",
        "类型": "时间序列",
        "数据源": "prometheus",
        "目标": [
          {
            "表达式": "rate(process_cpu_seconds_total{job=~\"near-rt-ric|o-du|o-cu\"}[5m]) * 100",
            "图例格式": "{{job}}"
          }
        ],
        "阈值": {
          "警告": 70,
          "严重": 85
        }
      },
      {
        "标题": "内存使用分析",
        "类型": "图表",
        "目标": [
          {
            "表达式": "process_resident_memory_bytes{job=~\"near-rt-ric|o-du|o-cu\"}",
            "图例格式": "{{job}} RSS"
          }
        ]
      }
    ]
  }
}
```

这个全面的性能优化框架提供了系统化的方法来优化 O-RAN 系统在网络、计算和应用层的性能，同时保持监控和自动化调优能力。