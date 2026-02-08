# O-RAN Daily Operations Procedures

## Overview
This document provides comprehensive guidelines and procedures for daily operational activities in O-RAN environments. It covers routine maintenance tasks, health checks, configuration management, and operational best practices to ensure system reliability and performance.

## Daily Health Check Procedures

### Morning System Health Verification
```bash
#!/bin/bash
# Daily morning health check script for O-RAN systems

echo "Starting O-RAN Daily Health Check - $(date)"

# Function to check component status
check_component_status() {
    local component=$1
    local endpoint=$2
    
    echo "Checking ${component} status..."
    response=$(curl -s -o /dev/null -w "%{http_code}" ${endpoint}/health)
    
    if [ "$response" = "200" ]; then
        echo "✓ ${component}: HEALTHY"
        return 0
    else
        echo "✗ ${component}: UNHEALTHY (Status: ${response})"
        return 1
    fi
}

# Check core O-RAN components
components=(
    "Near-RT RIC:http://192.168.1.100:8080"
    "O-DU-1:http://192.168.1.101:8080" 
    "O-DU-2:http://192.168.1.102:8080"
    "O-CU:http://192.168.1.103:8080"
    "SMO:http://192.168.1.104:8080"
)

healthy_count=0
total_components=${#components[@]}

for component_info in "${components[@]}"; do
    component=$(echo $component_info | cut -d':' -f1)
    endpoint=$(echo $component_info | cut -d':' -f2)
    
    if check_component_status "$component" "$endpoint"; then
        ((healthy_count++))
    fi
done

echo ""
echo "Health Check Summary:"
echo "Healthy Components: ${healthy_count}/${total_components}"

if [ $healthy_count -eq $total_components ]; then
    echo "✓ All systems operational"
    exit 0
else
    echo "✗ Some components require attention"
    # Send alert notification
    send_alert "O-RAN Health Check Alert" "Only ${healthy_count}/${total_components} components healthy"
    exit 1
fi
```

### Network Interface Monitoring
```python
# Network interface monitoring and alerting system
import psutil
import time
import smtplib
from email.mime.text import MIMEText

class NetworkMonitor:
    def __init__(self):
        self.interfaces = ['eth0', 'eth1', 'bond0']
        self.thresholds = {
            'packet_loss': 0.01,  # 1% packet loss threshold
            'latency': 50,        # 50ms latency threshold
            'bandwidth_util': 80  # 80% bandwidth utilization threshold
        }
        self.alert_history = {}
    
    def monitor_interfaces(self):
        """Monitor network interfaces for anomalies"""
        for interface in self.interfaces:
            stats = psutil.net_if_stats()[interface]
            io_counters = psutil.net_io_counters(pernic=True)[interface]
            
            # Check interface status
            if not stats.isup:
                self.send_alert(f"Interface Down: {interface}", 
                              f"Network interface {interface} is DOWN")
                continue
            
            # Check packet loss and errors
            if io_counters.errin > 0 or io_counters.dropin > 0:
                error_rate = (io_counters.errin + io_counters.dropin) / max(io_counters.packets_recv, 1)
                if error_rate > self.thresholds['packet_loss']:
                    self.send_alert(f"High Error Rate: {interface}",
                                  f"Error rate {error_rate:.2%} exceeds threshold")
            
            # Check bandwidth utilization
            bandwidth_util = self.calculate_bandwidth_utilization(interface, io_counters)
            if bandwidth_util > self.thresholds['bandwidth_util']:
                self.send_alert(f"High Bandwidth Utilization: {interface}",
                              f"Utilization {bandwidth_util}% exceeds threshold")
    
    def calculate_bandwidth_utilization(self, interface, counters):
        """Calculate current bandwidth utilization percentage"""
        # Implementation would involve measuring byte rates over time
        # This is a simplified example
        current_time = time.time()
        if interface in self.alert_history:
            last_check = self.alert_history[interface]['last_check']
            bytes_sent = counters.bytes_sent - self.alert_history[interface]['bytes_sent']
            time_diff = current_time - last_check
            
            # Calculate Mbps
            mbps = (bytes_sent * 8) / (time_diff * 1000000)
            # Assuming 1Gbps interface capacity
            utilization = (mbps / 1000) * 100
            
            self.alert_history[interface].update({
                'last_check': current_time,
                'bytes_sent': counters.bytes_sent,
                'utilization': utilization
            })
            
            return utilization
        else:
            self.alert_history[interface] = {
                'last_check': current_time,
                'bytes_sent': counters.bytes_sent,
                'utilization': 0
            }
            return 0
    
    def send_alert(self, subject, message):
        """Send alert notification via email"""
        msg = MIMEText(message)
        msg['Subject'] = f"O-RAN ALERT: {subject}"
        msg['From'] = "oran-monitor@company.com"
        msg['To'] = "noc-team@company.com"
        
        try:
            smtp_server = smtplib.SMTP('localhost')
            smtp_server.send_message(msg)
            smtp_server.quit()
            print(f"Alert sent: {subject}")
        except Exception as e:
            print(f"Failed to send alert: {e}")

# Usage
monitor = NetworkMonitor()
while True:
    monitor.monitor_interfaces()
    time.sleep(300)  # Check every 5 minutes
```

## Configuration Management Procedures

### Configuration Backup and Restore
```yaml
# Configuration management workflow
configuration_management:
  backup_schedule:
    daily_full_backup: "02:00"
    hourly_incremental_backup: "*:30"
    weekly_archive: "Sun 03:00"
  
  backup_locations:
    primary: "/backup/oran-configs/"
    secondary: "s3://oran-backups/configs/"
    disaster_recovery: "azure://dr-backups/oran/"
  
  configuration_items:
    - name: "near-rt-ric-config"
      path: "/etc/oran/near-rt-ric/"
      type: "yaml"
      backup_frequency: "hourly"
    
    - name: "odu-configuration"  
      path: "/etc/oran/o-du/"
      type: "json"
      backup_frequency: "daily"
    
    - name: "cu-parameters"
      path: "/etc/oran/o-cu/"
      type: "xml"
      backup_frequency: "daily"
    
    - name: "smo-policies"
      path: "/etc/oran/smo/"
      type: "yaml"
      backup_frequency: "hourly"

# Backup script example
#!/bin/bash
BACKUP_DIR="/backup/oran-configs/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup Near-RT RIC configuration
tar -czf $BACKUP_DIR/near-rt-ric-config.tar.gz /etc/oran/near-rt-ric/
echo "$(date): Backed up Near-RT RIC configuration" >> /var/log/oran-backup.log

# Backup O-DU configurations
for odu in /etc/oran/o-du/*; do
    odu_name=$(basename $odu)
    tar -czf $BACKUP_DIR/o-du-${odu_name}.tar.gz $odu/
done

# Sync to remote storage
rsync -av $BACKUP_DIR/ s3://oran-backups/configs/$(date +%Y%m%d)/
```

### Change Management Process
```markdown
## O-RAN Configuration Change Management Process

### 1. Change Request Submission
- **Template**: Use standardized change request form
- **Required Information**:
  - Change description and justification
  - Impact assessment (services affected, downtime required)
  - Rollback plan and procedure
  - Testing requirements and validation criteria
  - Approval chain and stakeholders

### 2. Change Evaluation and Approval
- **Technical Review**: Architecture and security impact analysis
- **Business Impact Assessment**: Service disruption evaluation
- **Risk Assessment**: Probability and impact matrix
- **Approval Workflow**: Multi-level approval based on change severity
- **Scheduling**: Coordination with business hours and maintenance windows

### 3. Implementation Procedure
```bash
#!/bin/bash
# Standardized change implementation script

CHANGE_ID=$1
ENVIRONMENT=$2

echo "Implementing Change ${CHANGE_ID} in ${ENVIRONMENT}"

# Pre-implementation checks
echo "Performing pre-change validation..."
./validate_pre_conditions.sh $CHANGE_ID

# Backup current configuration
echo "Creating backup..."
./backup_current_config.sh $CHANGE_ID

# Apply changes
echo "Applying configuration changes..."
./apply_changes.sh $CHANGE_ID $ENVIRONMENT

# Post-implementation validation
echo "Validating post-change status..."
./validate_post_conditions.sh $CHANGE_ID

# Update change log
echo "$(date): Change ${CHANGE_ID} completed successfully" >> /var/log/oran-changes.log
```

### 4. Post-Change Verification
- **Automated Testing**: Execute regression test suite
- **Health Checks**: Verify all components functioning properly
- **Performance Baseline**: Compare against pre-change metrics
- **User Acceptance**: Stakeholder sign-off on functionality
- **Documentation Update**: Modify configuration documentation

### 5. Rollback Procedure
- **Trigger Conditions**: Performance degradation, service disruption, security issues
- **Rollback Window**: Defined timeframe for safe rollback
- **Procedure Execution**: Automated rollback scripts
- **Post-Rollback Validation**: Confirm system stability restored
```

## Incident Response Procedures

### Level 1 Support Escalation Matrix
```markdown
## O-RAN Incident Classification and Escalation

### Severity Levels
- **Severity 1 (Critical)**: Complete service outage, security breach, data loss
- **Severity 2 (High)**: Major performance degradation, partial service disruption  
- **Severity 3 (Medium)**: Minor service impact, configuration issues
- **Severity 4 (Low)**: Informational alerts, enhancement requests

### Escalation Timelines
| Severity | Initial Response | Escalation | Resolution Target |
|----------|------------------|------------|-------------------|
| Sev 1    | 15 minutes       | 30 minutes | 2 hours           |
| Sev 2    | 30 minutes       | 1 hour     | 8 hours           |
| Sev 3    | 2 hours          | 4 hours    | 24 hours          |
| Sev 4    | 1 business day   | 2 days     | 5 business days   |

### Communication Protocols
- **Internal**: Ticketing system, team chat channels, email notifications
- **External**: Customer portal, status page updates, direct customer contact
- **Stakeholder**: Executive summaries, regular status updates, post-mortem reports
```

### Troubleshooting Playbooks
```markdown
## Common O-RAN Issue Resolution Playbooks

### E2 Interface Connectivity Issues
**Symptoms**: 
- RIC unable to establish connection with O-DU/O-CU
- Subscription management failures
- Indication message timeouts

**Diagnostic Steps**:
1. Verify network connectivity between RIC and network functions
2. Check E2 interface configuration parameters
3. Validate certificate and security settings
4. Review logs for specific error messages
5. Test with simplified configuration

**Resolution Actions**:
- Restart E2 interface services
- Reconfigure security certificates
- Adjust timeout and retry parameters
- Update routing tables if needed

### F1 Interface Performance Degradation
**Symptoms**:
- High latency between CU and DU
- Packet loss in user plane traffic
- UE attachment failures
- Handover procedure timeouts

**Investigation Process**:
1. Monitor interface metrics (latency, throughput, errors)
2. Check hardware resource utilization (CPU, memory, network)
3. Verify split option configuration consistency
4. Analyze traffic patterns and congestion points
5. Review QoS and priority settings

### O-FH Synchronization Problems
**Symptoms**:
- Timing synchronization failures
- IQ data corruption
- RU-DU communication breakdown
- Phase alignment issues

**Troubleshooting Guide**:
1. Verify IEEE 1588 PTP configuration
2. Check GPS and clock source status
3. Validate fronthaul network quality
4. Monitor synchronization metrics
5. Test with known good configuration
```

## Performance Monitoring and Optimization

### Key Performance Indicators Dashboard
```json
{
  "dashboard_name": "O-RAN_Daily_Operations_KPIs",
  "refresh_interval": "30s",
  "panels": [
    {
      "title": "System Availability",
      "type": "singlestat",
      "datasource": "Prometheus",
      "targets": [
        {
          "expr": "avg(up{job=~\"oran.*\"}) * 100",
          "legendFormat": "Overall Availability %"
        }
      ],
      "thresholds": "99.9,99.95"
    },
    {
      "title": "Interface Latencies",
      "type": "graph",
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
    },
    {
      "title": "Active Connections",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(active_ue_connections)",
          "legendFormat": "Total Active UEs"
        }
      ]
    }
  ]
}
```

### Automated Performance Alerts
```yaml
# Performance alerting rules
groups:
- name: oran-performance-alerts
  rules:
  - alert: HighInterfaceLatency
    expr: histogram_quantile(0.95, rate(interface_latency_seconds_bucket[5m])) > 0.050
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Interface latency exceeding threshold"
      description: "{{ $labels.interface_type }} latency is {{ $value }}s"

  - alert: ComponentUnhealthy
    expr: up{job=~"oran.*"} == 0
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "O-RAN component unavailable"
      description: "{{ $labels.job }} is not responding"

  - alert: HighErrorRate
    expr: rate(interface_errors_total[5m]) > 0.001
    for: 3m
    labels:
      severity: warning
    annotations:
      summary: "High interface error rate detected"
      description: "Error rate of {{ $value }} exceeds threshold"
```

These procedures provide a comprehensive foundation for daily O-RAN operations management, ensuring system reliability, performance optimization, and rapid incident response.