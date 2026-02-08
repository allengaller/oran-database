# O-RAN Utility Programs

## Overview
Collection of essential command-line tools, scripts, and utility programs specifically designed for O-RAN network management, troubleshooting, and daily operational tasks.

## Command Line Tools

### Network Configuration Utilities

#### O-RAN Configuration Manager (oran-cfg)
```
Core Functionality:
├── Configuration Template Management
│   ├── YANG model-based template generation
│   ├── Parameter validation against schemas
│   ├── Template version control and history
│   └── Bulk configuration deployment capabilities
├── Device Provisioning
│   ├── Automated device discovery and registration
│   ├── Zero-touch provisioning workflows
│   ├── Configuration push to multiple devices
│   └── Provisioning status monitoring and reporting
└── Configuration Compliance
    ├── Policy-based configuration validation
    ├── Drift detection and remediation
    ├── Audit trail generation
    └── Compliance reporting for regulatory requirements

Command Examples:
# Generate configuration template
oran-cfg template generate --model o-ran-module --output config-template.yaml

# Validate configuration against YANG model
oran-cfg validate --config site-config.yaml --schema o-ran-network-topology.yang

# Deploy configuration to devices
oran-cfg deploy --template prod-template.yaml --target-group ran-devices --dry-run

# Check configuration compliance
oran-cfg compliance check --policy security-baseline --devices o-du-cluster-1

Sample Configuration Template:
apiVersion: oran.org/v1
kind: O-RANConfiguration
metadata:
  name: site-a-production
  namespace: oran-config
  
spec:
  networkSlicing:
    enabled: true
    slices:
      - name: embb-slice
        priority: high
        qosProfile: enhanced-mobile-broadband
        resourceAllocation:
          cpu: "4"
          memory: "8Gi"
          bandwidth: "10Gbps"
          
      - name: urllc-slice
        priority: critical
        qosProfile: ultra-reliable-low-latency
        resourceAllocation:
          cpu: "2"
          memory: "4Gi"
          latency: "< 1ms"
          
  fronthaul:
    protocol: eCPRI
    compression: 
      enabled: true
      algorithm: MODULATION_BASED
      ratio: "2:1"
      
  monitoring:
    prometheus:
      enabled: true
      scrapeInterval: "15s"
      retention: "30d"
    logging:
      level: INFO
      format: json
      destinations:
        - type: elasticsearch
          url: https://logging-cluster:9200
        - type: syslog
          server: syslog-server:514
```

#### NETCONF Client Utilities
```
Enhanced NETCONF Operations:
├── Session Management
│   ├── Persistent session establishment
│   ├── Connection pooling for multiple devices
│   ├── TLS/SSH encryption support
│   └── Session timeout and retry mechanisms
├── Configuration Operations
│   ├── Edit-config with candidate datastore support
│   ├── Copy-config between datastores
│   ├── Delete-config for partial configuration removal
│   └── Lock/unlock operations for configuration safety
└── Data Retrieval
    ├── Get/get-config with XPath filtering
    ├── Notification subscription and handling
    ├── Performance data collection
    └── State data monitoring

NETCONF Utility Commands:
# Establish NETCONF session
netconf-client connect --host o-du-01 --port 830 --username admin --password *****

# Retrieve running configuration
netconf-client get-config --source running --filter-xpath "/o-ran-interfaces:interfaces"

# Edit candidate configuration
netconf-client edit-config --target candidate --config-file new-settings.xml

# Commit configuration changes
netconf-client commit --confirmed --confirm-timeout 300

# Subscribe to notifications
netconf-client subscribe --stream o-ran-notifications --start-time "2024-01-01T00:00:00Z"

Advanced NETCONF Script:
#!/usr/bin/env python3
import ncclient.manager
import xml.etree.ElementTree as ET

class O-RANNETCONFManager:
    def __init__(self, host, port, username, password):
        self.manager = ncclient.manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            hostkey_verify=False,
            device_params={'name': 'default'}
        )
    
    def get_cell_status(self, cell_id):
        """Retrieve cell operational status"""
        filter_xml = f"""
        <filter>
            <cells xmlns="urn:o-ran:cell-management:1.0">
                <cell>
                    <id>{cell_id}</id>
                </cell>
            </cells>
        </filter>
        """
        
        response = self.manager.get(filter=filter_xml)
        return self.parse_cell_status(response)
    
    def configure_cell_parameters(self, cell_id, parameters):
        """Configure cell parameters dynamically"""
        config_xml = self.build_cell_config_xml(cell_id, parameters)
        
        # Use candidate datastore for safe configuration
        self.manager.edit_config(target='candidate', config=config_xml)
        
        # Validate configuration
        validation_result = self.manager.validate(source='candidate')
        if validation_result.ok:
            # Commit with confirmation
            commit_response = self.manager.commit(confirmed=True, confirm_timeout=300)
            return commit_response.ok
        else:
            self.manager.discard_changes()
            raise Exception(f"Configuration validation failed: {validation_result}")
```

### Performance Monitoring Tools

#### O-RAN Metrics Collector (oran-metrics)
```
Real-time Metrics Collection:
├── Protocol-Specific Collectors
│   ├── E2 interface message statistics
│   ├── eCPRI fronthaul performance metrics
│   ├── O1 interface configuration changes
│   └── A1 interface policy enforcement data
├── Resource Utilization Monitoring
│   ├── CPU and memory usage per component
│   ├── Network interface statistics
│   ├── Storage utilization and I/O metrics
│   └── GPU utilization for ML workloads
└── Quality of Service Measurements
    ├── Latency and jitter measurements
    ├── Packet loss and error rate tracking
    ├── Throughput and bandwidth utilization
    └── Service level agreement compliance

Metrics Collection Commands:
# Start continuous metrics collection
oran-metrics collect --interval 15s --output-format prometheus --port 9100

# Collect specific metrics for analysis
oran-metrics snapshot --components o-du,o-cu,near-rt-ric --duration 5m

# Export metrics to file
oran-metrics export --format json --file metrics-export-$(date +%Y%m%d).json

# Stream metrics to monitoring system
oran-metrics stream --target prometheus-pushgateway:9091 --job oran-monitoring

Sample Metrics Output:
{
  "timestamp": "2024-01-15T10:30:00Z",
  "node": "o-du-01",
  "metrics": {
    "e2_interface": {
      "messages_sent": 12500,
      "messages_received": 12498,
      "average_latency_ms": 8.2,
      "error_rate": 0.00016
    },
    "fronthaul": {
      "bandwidth_utilization_percent": 65.3,
      "packet_loss_rate": 0.00002,
      "jitter_ms": 0.15,
      "sync_accuracy_ns": 50
    },
    "resources": {
      "cpu_usage_percent": 45.2,
      "memory_usage_bytes": 3221225472,
      "disk_io_ops_per_sec": 1250
    }
  }
}
```

#### Log Analysis Utilities

#### O-RAN Log Processor (oran-logproc)
```
Advanced Log Processing Capabilities:
├── Multi-Format Log Parsing
│   ├── Structured JSON log parsing
│   ├── Syslog format processing
│   ├── Custom log format definition
│   └── Binary log file analysis
├── Real-time Log Streaming
│   ├── Tail-like functionality for live logs
│   ├── Filter and search during streaming
│   ├── Highlight important events
│   └── Export filtered streams to files
└── Log Correlation and Analysis
    ├── Cross-component log correlation
    ├── Temporal pattern analysis
    ├── Error cascade detection
    └── Root cause analysis support

Log Processing Commands:
# Parse and filter logs
oran-logproc parse --input /var/log/oran/*.log --filter "ERROR|WARN" --since "1h"

# Correlate logs across components
oran-logproc correlate --components o-du,o-cu,near-rt-ric --window 30s

# Generate analysis report
oran-logproc analyze --input parsed-logs.json --output analysis-report.pdf

# Real-time log monitoring
oran-logproc monitor --follow --highlight "E2_CONNECTION|POLICY_ENFORCEMENT" --alert-threshold 5

Log Analysis Script Example:
#!/usr/bin/env python3
import re
import json
from datetime import datetime, timedelta

class O-RANLogAnalyzer:
    def __init__(self):
        self.patterns = {
            'e2_errors': r'E2_ERROR.*Cell:(\d+).*Error:(.+)',
            'connection_issues': r'CONNECTION_LOST.*Component:(\w+)',
            'performance_degradation': r'PERFORMANCE_DEGRADED.*Metric:(\w+).*Value:([\d.]+)'
        }
        
    def analyze_log_file(self, filepath):
        issues = {
            'errors': [],
            'warnings': [],
            'performance_issues': [],
            'timeline': []
        }
        
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                timestamp = self.extract_timestamp(line)
                
                # Check for different issue types
                for issue_type, pattern in self.patterns.items():
                    match = re.search(pattern, line)
                    if match:
                        issue = {
                            'line': line_num,
                            'timestamp': timestamp,
                            'content': line.strip(),
                            'details': match.groups()
                        }
                        issues[issue_type].append(issue)
                        issues['timeline'].append({
                            'timestamp': timestamp,
                            'event': issue_type,
                            'line': line_num
                        })
        
        # Sort timeline chronologically
        issues['timeline'].sort(key=lambda x: x['timestamp'])
        
        return issues

    def extract_timestamp(self, line):
        timestamp_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        match = re.search(timestamp_pattern, line)
        return datetime.fromisoformat(match.group()) if match else None

# Usage
analyzer = O-RANLogAnalyzer()
results = analyzer.analyze_log_file('/var/log/oran/system.log')
print(json.dumps(results, indent=2, default=str))
```

## Automation Scripts

### Deployment Automation

#### O-RAN Cluster Provisioner (oran-provision)
```
Kubernetes Cluster Setup:
├── Infrastructure Provisioning
│   ├── VM creation and configuration
│   ├── Network setup and security groups
│   ├── Storage provisioning and mounting
│   └── Load balancer configuration
├── Kubernetes Installation
│   ├── Container runtime setup (containerd/docker)
│   ├── Kubernetes control plane initialization
│   ├── Worker node joining and configuration
│   └── CNI plugin installation and configuration
└── O-RAN Component Deployment
    ├── Helm chart deployment for RAN components
    ├── Namespace and RBAC configuration
    ├── Persistent volume claims setup
    └── Service mesh integration (Istio/Linkerd)

Provisioning Script Structure:
#!/bin/bash
# oran-provision.sh

set -euo pipefail

# Configuration
CLUSTER_NAME="${1:-oran-cluster}"
REGION="${2:-us-west-2}"
NODE_COUNT="${3:-6}"

# Infrastructure Setup
setup_infrastructure() {
    echo "Setting up infrastructure for ${CLUSTER_NAME}"
    
    # Create VPC and networking
    aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
        --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=${CLUSTER_NAME}}]"
    
    # Create security groups
    create_security_groups
    
    # Launch EC2 instances
    launch_control_plane_nodes
    launch_worker_nodes
}

# Kubernetes Installation
install_kubernetes() {
    echo "Installing Kubernetes on cluster nodes"
    
    # Install container runtime
    install_container_runtime
    
    # Initialize control plane
    kubeadm init --config=kubeadm-config.yaml
    
    # Configure kubectl
    mkdir -p $HOME/.kube
    cp /etc/kubernetes/admin.conf $HOME/.kube/config
    
    # Install CNI
    kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
}

# O-RAN Component Deployment
deploy_oran_components() {
    echo "Deploying O-RAN components"
    
    # Add Helm repositories
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add oran-sc https://o-ran-sc.github.io/helm-charts
    
    # Create namespaces
    kubectl create namespace oran-control-plane
    kubectl create namespace oran-user-plane
    kubectl create namespace oran-management
    
    # Deploy Near-RT RIC
    helm install near-rt-ric oran-sc/near-rt-ric \
        --namespace oran-control-plane \
        --values oran-values.yaml
    
    # Deploy O-CU/O-DU components
    deploy_o_cu_components
    deploy_o_du_components
}

# Main execution
main() {
    echo "Starting O-RAN cluster provisioning: ${CLUSTER_NAME}"
    
    setup_infrastructure
    install_kubernetes
    deploy_oran_components
    
    echo "Cluster provisioning completed successfully!"
    echo "Access your cluster with: kubectl config use-context ${CLUSTER_NAME}"
}

main "$@"
```

### Maintenance and Troubleshooting Scripts

#### O-RAN Health Checker (oran-health)
```
Comprehensive Health Assessment:
├── Component Status Verification
│   ├── Pod and service status checks
│   ├── Container health and resource usage
│   ├── Network connectivity validation
│   └── Storage and persistent volume health
├── Protocol Interface Testing
│   ├── E2 interface message exchange verification
│   ├── eCPRI fronthaul link quality testing
│   ├── O1 interface configuration validation
│   └── A1 interface policy communication checks
└── Performance Benchmarking
    ├── Latency and throughput measurements
    ├── Resource utilization benchmarks
    ├── Scalability testing under load
    └── Failover and recovery time measurements

Health Check Script:
#!/usr/bin/env python3
import subprocess
import json
import requests
from datetime import datetime

class O-RANHealthChecker:
    def __init__(self, kubeconfig=None):
        self.kubeconfig = kubeconfig
        self.results = {
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }
    
    def check_kubernetes_components(self):
        """Check Kubernetes component health"""
        checks = {}
        
        # Check node status
        result = subprocess.run(['kubectl', 'get', 'nodes', '-o', 'json'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            nodes = json.loads(result.stdout)
            ready_nodes = sum(1 for node in nodes['items'] 
                            if any(condition['status'] == 'True' 
                                 for condition in node['status']['conditions'] 
                                 if condition['type'] == 'Ready'))
            checks['nodes_ready'] = {
                'status': 'PASS' if ready_nodes == len(nodes['items']) else 'FAIL',
                'ready_count': ready_nodes,
                'total_count': len(nodes['items'])
            }
        
        # Check pod status
        result = subprocess.run(['kubectl', 'get', 'pods', '-A', '-o', 'json'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            pods = json.loads(result.stdout)
            running_pods = sum(1 for pod in pods['items'] 
                             if pod['status']['phase'] == 'Running')
            checks['pods_running'] = {
                'status': 'PASS' if running_pods == len(pods['items']) else 'WARN',
                'running_count': running_pods,
                'total_count': len(pods['items'])
            }
        
        self.results['checks']['kubernetes'] = checks
        return checks
    
    def check_oran_interfaces(self):
        """Check O-RAN interface connectivity"""
        checks = {}
        
        # Test E2 interface
        try:
            response = requests.get('http://near-rt-ric:8080/health/e2', timeout=5)
            checks['e2_interface'] = {
                'status': 'PASS' if response.status_code == 200 else 'FAIL',
                'response_time_ms': response.elapsed.total_seconds() * 1000
            }
        except requests.RequestException as e:
            checks['e2_interface'] = {
                'status': 'FAIL',
                'error': str(e)
            }
        
        # Test fronthaul connectivity
        checks['fronthaul_links'] = self.test_fronthaul_connectivity()
        
        self.results['checks']['interfaces'] = checks
        return checks
    
    def test_fronthaul_connectivity(self):
        """Test fronthaul network connectivity"""
        # This would typically involve more sophisticated network testing
        # For demonstration, we'll simulate the test
        return {
            'status': 'PASS',
            'links_tested': 12,
            'failed_links': 0,
            'average_latency_ms': 0.08
        }
    
    def generate_report(self):
        """Generate health check report"""
        passed = sum(1 for category in self.results['checks'].values()
                    for check in category.values()
                    if check.get('status') == 'PASS')
        total = sum(len(category) for category in self.results['checks'].values())
        
        self.results['summary'] = {
            'overall_status': 'HEALTHY' if passed == total else 'DEGRADED',
            'checks_passed': passed,
            'total_checks': total,
            'pass_rate': f"{(passed/total)*100:.1f}%"
        }
        
        return json.dumps(self.results, indent=2)

# Usage
checker = O-RANHealthChecker()
checker.check_kubernetes_components()
checker.check_oran_interfaces()
report = checker.generate_report()
print(report)
```

### Backup and Recovery Tools

#### O-RAN Configuration Backup (oran-backup)
```
Automated Backup System:
├── Configuration Backup
│   ├── YANG model-based configuration export
│   ├── Running configuration snapshots
│   ├── Device state and operational data
│   └── Custom configuration backups
├── Data Protection
│   ├── Database backup and recovery
│   ├── Persistent volume snapshots
│   ├── Certificate and key management
│   └── Log file archiving
└── Recovery Automation
    ├── Point-in-time recovery capabilities
    ├── Automated restore procedures
    ├── Configuration rollback mechanisms
    └── Disaster recovery orchestration

Backup Script Example:
#!/bin/bash
# oran-backup.sh

BACKUP_DIR="/backup/oran/$(date +%Y%m%d_%H%M%S)"
CONFIG_BACKUP="$BACKUP_DIR/config"
DATA_BACKUP="$BACKUP_DIR/data"
LOGS_BACKUP="$BACKUP_DIR/logs"

# Create backup directory structure
mkdir -p "$CONFIG_BACKUP" "$DATA_BACKUP" "$LOGS_BACKUP"

# Backup Kubernetes configuration
echo "Backing up Kubernetes configuration..."
kubectl get all -A -o yaml > "$CONFIG_BACKUP/k8s-all-resources.yaml"
kubectl get secrets -A -o yaml > "$CONFIG_BACKUP/k8s-secrets.yaml"

# Backup O-RAN specific configurations
echo "Backing up O-RAN configurations..."
kubectl get configmaps -n oran-control-plane -o yaml > "$CONFIG_BACKUP/oran-configmaps.yaml"
kubectl get deployments -n oran-control-plane -o yaml > "$CONFIG_BACKUP/oran-deployments.yaml"

# Backup persistent data
echo "Backing up persistent data..."
for pv in $(kubectl get pv -o jsonpath='{.items[*].metadata.name}'); do
    kubectl get pv "$pv" -o yaml > "$DATA_BACKUP/pv-${pv}.yaml"
done

# Backup database (if using external database)
if [ -n "$DATABASE_URL" ]; then
    echo "Backing up database..."
    pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" > "$DATA_BACKUP/database.sql"
fi

# Archive and compress
echo "Creating backup archive..."
tar -czf "/backup/oran-backup-$(date +%Y%m%d_%H%M%S).tar.gz" -C /backup/oran "$(basename $BACKUP_DIR)"

# Cleanup old backups (keep last 7 days)
find /backup/oran -name "oran-backup-*" -mtime +7 -delete

echo "Backup completed successfully!"
```

These utility programs provide essential tools for O-RAN network administrators and engineers to efficiently manage, monitor, and troubleshoot O-RAN deployments while maintaining operational excellence and minimizing downtime.