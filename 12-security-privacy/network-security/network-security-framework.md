# O-RAN Network Security Framework

## Overview
This document provides a comprehensive network security framework for O-RAN systems, covering network segmentation, intrusion detection, DDoS protection, and secure communication protocols.

## Network Segmentation and Microsegmentation

### Zero Trust Network Architecture
```yaml
zero_trust_principles:
  never_trust_always_verify: true
  least_privilege_access: true
  continuous_validation: true
  microsegmentation: true
  
security_domains:
  - name: "Management Domain"
    description: "SMO and administrative interfaces"
    security_level: "high"
    access_controls: ["mutual_tls", "rbac", "audit_logging"]
    network_segments: ["10.10.0.0/24", "10.20.0.0/24"]
  
  - name: "Control Plane Domain"
    description: "E2, A1, O1 interfaces for control signaling"
    security_level: "high"
    access_controls: ["certificate_based_auth", "message_signing", "rate_limiting"]
    network_segments: ["10.30.0.0/24", "10.40.0.0/24"]
  
  - name: "User Plane Domain"
    description: "F1, O-FH interfaces for user data"
    security_level: "medium"
    access_controls: ["encryption", "integrity_protection", "qos_isolation"]
    network_segments: ["10.50.0.0/24", "10.60.0.0/24"]
  
  - name: "Infrastructure Domain"
    description: "Underlying compute, storage, and networking"
    security_level: "high"
    access_controls: ["hypervisor_security", "network_segmentation", "hardware_root_of_trust"]
    network_segments: ["10.70.0.0/24", "10.80.0.0/24"]
```

### Network Segmentation Implementation
```bash
#!/bin/bash
# O-RAN network segmentation implementation

# Create network namespaces for security domains
setup_network_namespaces() {
    echo "Setting up network namespaces for O-RAN security domains..."
    
    # Management namespace
    ip netns add oran_mgmt
    ip link add mgmt_br0 type bridge
    ip link set mgmt_br0 netns oran_mgmt
    
    # Control plane namespace
    ip netns add oran_control
    ip link add control_br0 type bridge
    ip link set control_br0 netns oran_control
    
    # User plane namespace
    ip netns add oran_user
    ip link add user_br0 type bridge
    ip link set user_br0 netns oran_user
    
    # Configure namespace networking
    configure_namespace_networking
}

configure_namespace_networking() {
    # Management network configuration
    ip netns exec oran_mgmt ip addr add 10.10.0.1/24 dev mgmt_br0
    ip netns exec oran_mgmt ip link set mgmt_br0 up
    ip netns exec oran_mgmt ip route add default via 10.10.0.1
    
    # Control plane network configuration
    ip netns exec oran_control ip addr add 10.30.0.1/24 dev control_br0
    ip netns exec oran_control ip link set control_br0 up
    ip netns exec oran_control ip route add default via 10.30.0.1
    
    # User plane network configuration
    ip netns exec oran_user ip addr add 10.50.0.1/24 dev user_br0
    ip netns exec oran_user ip link set user_br0 up
    ip netns exec oran_user ip route add default via 10.50.0.1
}

# VLAN-based segmentation
setup_vlan_segmentation() {
    local interface=$1
    
    # Create VLAN interfaces for different security domains
    for vlan_id in 100 200 300 400; do
        ip link add link ${interface} name ${interface}.${vlan_id} type vlan id ${vlan_id}
        ip link set ${interface}.${vlan_id} up
        
        case ${vlan_id} in
            100)  # Management VLAN
                ip addr add 10.10.0.10/24 dev ${interface}.${vlan_id}
                ;;
            200)  # Control Plane VLAN
                ip addr add 10.30.0.10/24 dev ${interface}.${vlan_id}
                ;;
            300)  # User Plane VLAN
                ip addr add 10.50.0.10/24 dev ${interface}.${vlan_id}
                ;;
            400)  # Infrastructure VLAN
                ip addr add 10.70.0.10/24 dev ${interface}.${vlan_id}
                ;;
        esac
    done
}
```

## Intrusion Detection and Prevention

### Network IDS/IPS Configuration
```python
# O-RAN Network Intrusion Detection System
import socket
import struct
import threading
from scapy.all import *
from collections import defaultdict, deque
import time

class ORANNetworkIDS:
    def __init__(self, interfaces=None):
        self.interfaces = interfaces or ['eth0', 'eth1']
        self.signatures = self.load_attack_signatures()
        self.flow_table = defaultdict(lambda: {'packets': deque(maxlen=100), 'last_seen': time.time()})
        self.alert_threshold = 10
        self.alert_cooldown = 300  # 5 minutes
        
    def load_attack_signatures(self):
        """Load known attack signatures"""
        return {
            'syn_flood': {
                'pattern': lambda pkt: TCP in pkt and pkt[TCP].flags == 'S',
                'threshold': 100,
                'time_window': 10
            },
            'port_scan': {
                'pattern': self.detect_port_scan,
                'threshold': 20,
                'time_window': 60
            },
            'malformed_packets': {
                'pattern': self.detect_malformed_packets,
                'threshold': 5,
                'time_window': 30
            }
        }
    
    def detect_port_scan(self, pkt):
        """Detect port scanning activity"""
        if TCP not in pkt:
            return False
        
        src_ip = pkt[IP].src
        dst_port = pkt[TCP].dport
        
        # Track connection attempts per source IP
        key = f"scan_{src_ip}"
        self.flow_table[key]['ports'].add(dst_port)
        self.flow_table[key]['attempts'] += 1
        
        # Alert if too many different ports targeted
        return len(self.flow_table[key]['ports']) > 15
    
    def detect_malformed_packets(self, pkt):
        """Detect malformed or suspicious packets"""
        issues = []
        
        # Check for invalid IP header
        if IP in pkt:
            if pkt[IP].len < 20 or pkt[IP].len > 65535:
                issues.append("invalid_ip_length")
            
            # Check for fragment issues
            if pkt[IP].flags.MF and pkt[IP].frag == 0:
                issues.append("invalid_fragmentation")
        
        # Check TCP flags
        if TCP in pkt:
            flags = pkt[TCP].flags
            # NULL scan (no flags set)
            if flags == 0:
                issues.append("null_scan")
            # XMAS scan (FIN+URG+PSH)
            elif flags == 0x29:
                issues.append("xmas_scan")
        
        return len(issues) > 0
    
    def packet_handler(self, pkt):
        """Handle incoming packets"""
        if IP not in pkt:
            return
            
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        
        # Update flow table
        flow_key = f"{src_ip}->{dst_ip}"
        self.flow_table[flow_key]['packets'].append(pkt)
        self.flow_table[flow_key]['last_seen'] = time.time()
        
        # Check against signatures
        for sig_name, signature in self.signatures.items():
            if signature['pattern'](pkt):
                self.generate_alert(sig_name, pkt)
    
    def generate_alert(self, alert_type, packet):
        """Generate security alert"""
        alert = {
            'timestamp': time.time(),
            'type': alert_type,
            'source_ip': packet[IP].src if IP in packet else 'unknown',
            'destination_ip': packet[IP].dst if IP in packet else 'unknown',
            'protocol': packet.lastlayer().name,
            'payload_sample': str(packet)[:100]  # First 100 chars
        }
        
        print(f"SECURITY ALERT: {alert_type} detected from {alert['source_ip']}")
        self.log_alert(alert)
    
    def log_alert(self, alert):
        """Log alert to security system"""
        # In production, this would send to SIEM or logging system
        with open('/var/log/oran-security-alerts.log', 'a') as f:
            f.write(f"{time.ctime(alert['timestamp'])}: {alert}\n")
    
    def start_monitoring(self):
        """Start packet capture and analysis"""
        print("Starting O-RAN Network IDS...")
        
        for interface in self.interfaces:
            print(f"Monitoring interface: {interface}")
            sniff(iface=interface, prn=self.packet_handler, store=0)

# Usage example
def main():
    ids = ORANNetworkIDS(interfaces=['eth0', 'eth1'])
    
    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=ids.start_monitoring)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down O-RAN IDS...")

if __name__ == "__main__":
    main()
```

## DDoS Protection

### Rate Limiting and Traffic Shaping
```yaml
# DDoS protection configuration
ddos_protection:
  rate_limiting:
    global_limits:
      packets_per_second: 10000
      bytes_per_second: 104857600  # 100 Mbps
      connections_per_second: 1000
    
    per_source_limits:
      packets_per_second: 1000
      bytes_per_second: 10485760   # 10 Mbps
      connections_per_second: 100
    
    burst_allowance:
      packets: 5000
      bytes: 52428800  # 50 MB
      duration: 10     # seconds
  
  traffic_shaping:
    e2_interface:
      bandwidth_limit: "1Gbps"
      priority: "high"
      queue_type: "pfifo_fast"
      shaping_algorithm: "token_bucket"
    
    f1_interface:
      bandwidth_limit: "10Gbps"
      priority: "highest"
      queue_type: "fq_codel"
      shaping_algorithm: "deficit_round_robin"
    
    management_interface:
      bandwidth_limit: "100Mbps"
      priority: "low"
      queue_type: "red"
      shaping_algorithm: "weighted_fair_queuing"
  
  mitigation_strategies:
    - "blackhole_routing"
    - "rate_limiting"
    - "connection_throttling"
    - "geographic_filtering"
    - "protocol_validation"
    - "signature_based_blocking"
```

### DDoS Mitigation Implementation
```bash
#!/bin/bash
# O-RAN DDoS mitigation system

# iptables rules for DDoS protection
setup_ddos_protection() {
    echo "Setting up DDoS protection rules..."
    
    # Flush existing rules
    iptables -F
    iptables -X
    
    # Default policies
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT
    
    # Allow loopback
    iptables -A INPUT -i lo -j ACCEPT
    
    # Allow established connections
    iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
    
    # Rate limiting for SYN packets (SYN flood protection)
    iptables -A INPUT -p tcp --syn -m limit --limit 10/sec --limit-burst 20 -j ACCEPT
    iptables -A INPUT -p tcp --syn -j DROP
    
    # Rate limiting for ICMP (Ping flood protection)
    iptables -A INPUT -p icmp -m limit --limit 5/sec --limit-burst 10 -j ACCEPT
    iptables -A INPUT -p icmp -j DROP
    
    # Connection limiting per IP
    iptables -A INPUT -p tcp --dport 36421 -m connlimit --connlimit-above 10 -j REJECT --reject-with tcp-reset
    iptables -A INPUT -p tcp --dport 38472 -m connlimit --connlimit-above 50 -j REJECT --reject-with tcp-reset
    
    # Port scan detection
    iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP
    iptables -A INPUT -p tcp --tcp-flags SYN,FIN SYN,FIN -j DROP
    iptables -A INPUT -p tcp --tcp-flags SYN,RST SYN,RST -j DROP
    
    # Save rules
    iptables-save > /etc/iptables/rules.v4
}

# NFTables implementation for better performance
setup_nftables_ddos() {
    echo "Setting up NFTables DDoS protection..."
    
    # Create tables and chains
    nft add table ip oran_filter
    nft add chain ip oran_filter input { type filter hook input priority 0 \; }
    nft add chain ip oran_filter forward { type filter hook forward priority 0 \; }
    nft add chain ip oran_filter output { type filter hook output priority 0 \; }
    
    # Basic rules
    nft add rule ip oran_filter input iif "lo" accept
    nft add rule ip oran_filter input ct state established,related accept
    
    # Rate limiting
    nft add rule ip oran_filter input tcp flags \& \(syn\|rst\) == syn \
        limit rate 10/second burst 20 packets accept
    nft add rule ip oran_filter input tcp flags \& \(syn\|rst\) == syn drop
    
    # Connection limiting for O-RAN interfaces
    nft add rule ip oran_filter input tcp dport {36421} \
        ct count over 10 reject with tcp reset
    nft add rule ip oran_filter input tcp dport {38472} \
        ct count over 50 reject with tcp reset
    
    # Save configuration
    nft list ruleset > /etc/nftables.conf
}

# Traffic monitoring and alerting
monitor_traffic_patterns() {
    local threshold_pps=10000
    local threshold_bps=104857600  # 100 Mbps
    
    while true; do
        # Get current traffic statistics
        current_rx=$(cat /proc/net/dev | grep eth0 | awk '{print $2}')
        current_tx=$(cat /proc/net/dev | grep eth0 | awk '{print $10}')
        
        # Calculate rates (simplified)
        rx_rate=$((current_rx - prev_rx))
        tx_rate=$((current_tx - prev_tx))
        
        # Check thresholds
        if [ $rx_rate -gt $threshold_bps ] || [ $tx_rate -gt $threshold_bps ]; then
            echo "$(date): High traffic detected - RX: $rx_rate bps, TX: $tx_rate bps" >> /var/log/ddos-alert.log
            # Trigger mitigation actions
            trigger_mitigation $rx_rate $tx_rate
        fi
        
        prev_rx=$current_rx
        prev_tx=$current_tx
        sleep 5
    done
}

trigger_mitigation() {
    local rx_rate=$1
    local tx_rate=$2
    
    echo "Triggering DDoS mitigation for rates: RX=${rx_rate}, TX=${tx_rate}"
    
    # Implement temporary blackholing
    # This is a simplified example - production systems would be more sophisticated
    if [ $rx_rate -gt 524288000 ]; then  # 500 Mbps
        echo "Activating aggressive mitigation measures..."
        # Temporarily block high-traffic sources
        # Integrate with upstream providers for blackholing
    fi
}
```

## Secure Communication Protocols

### TLS Configuration for O-RAN Interfaces
```nginx
# nginx configuration for secure O-RAN interfaces
server {
    listen 36421 ssl http2;
    server_name oran-e2-interface.example.com;
    
    # SSL/TLS configuration
    ssl_certificate /etc/ssl/certs/oran-e2-cert.pem;
    ssl_certificate_key /etc/ssl/private/oran-e2-key.pem;
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/ssl/certs/oran-ca-bundle.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api burst=10 nodelay;
    }
}

# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
```

This comprehensive network security framework provides robust protection for O-RAN systems against various network-based threats while maintaining the performance and reliability required for telecommunications infrastructure.