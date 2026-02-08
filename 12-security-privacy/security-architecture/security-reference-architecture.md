# O-RAN Security Architecture Reference

## Overview
This document provides comprehensive security architecture guidelines for O-RAN deployments, covering threat modeling, security controls, cryptographic requirements, and compliance frameworks. It establishes the foundation for secure O-RAN system design and implementation.

## Security Architecture Framework

### Zero Trust Security Model
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
  
  - name: "Control Plane Domain"
    description: "E2, A1, O1 interfaces for control signaling"
    security_level: "high"
    access_controls: ["certificate_based_auth", "message_signing", "rate_limiting"]
  
  - name: "User Plane Domain"
    description: "F1, O-FH interfaces for user data"
    security_level: "medium"
    access_controls: ["encryption", "integrity_protection", "qos_isolation"]
  
  - name: "Infrastructure Domain"
    description: "Underlying compute, storage, and networking"
    security_level: "high"
    access_controls: ["hypervisor_security", "network_segmentation", "hardware_root_of_trust"]
```

### Defense in Depth Strategy
```markdown
## Multi-Layered Security Controls

### Layer 1: Physical Security
- Hardware root of trust (TPM, HSM)
- Secure boot mechanisms
- Physical access controls
- Tamper detection and response

### Layer 2: Network Security
- Network segmentation and microsegmentation
- Firewall and intrusion prevention systems
- Encrypted communications (TLS 1.3, IPSec)
- Network access control (802.1X)

### Layer 3: Platform Security
- Hypervisor security hardening
- Container security (image scanning, runtime protection)
- Operating system hardening
- Secure configuration management

### Layer 4: Application Security
- Secure coding practices
- Input validation and sanitization
- API security (OAuth 2.0, JWT)
- Regular security testing

### Layer 5: Data Security
- Encryption at rest and in transit
- Key management and rotation
- Data loss prevention
- Privacy-preserving techniques
```

## Cryptographic Requirements

### Certificate Management Framework
```bash
#!/bin/bash
# O-RAN certificate management system

# Certificate authority hierarchy
setup_certificate_authority() {
    echo "Setting up O-RAN Certificate Authority hierarchy..."
    
    # Root CA for organization
    openssl req -x509 -newkey rsa:4096 -keyout root-ca-key.pem -out root-ca-cert.pem \
        -days 3650 -nodes -subj "/CN=O-RAN Root CA/O=Organization/C=US"
    
    # Intermediate CAs for different domains
    for domain in management control user infrastructure; do
        openssl req -newkey rsa:2048 -keyout ${domain}-ca-key.pem -out ${domain}-ca-csr.pem \
            -nodes -subj "/CN=O-RAN ${domain^} CA/O=Organization/C=US"
        
        openssl x509 -req -in ${domain}-ca-csr.pem -out ${domain}-ca-cert.pem \
            -CA root-ca-cert.pem -CAkey root-ca-key.pem -CAcreateserial \
            -days 1825 -extfile ca-extensions.cnf
    done
}

# Component certificate issuance
issue_component_certificate() {
    local component_type=$1
    local component_name=$2
    local domain_ca=$3
    
    echo "Issuing certificate for ${component_type}/${component_name}"
    
    # Generate component key pair
    openssl genrsa -out ${component_name}-key.pem 2048
    
    # Create certificate signing request
    openssl req -new -key ${component_name}-key.pem -out ${component_name}-csr.pem \
        -subj "/CN=${component_name}.${component_type}.oran.org/O=Organization/C=US"
    
    # Sign with appropriate domain CA
    openssl x509 -req -in ${component_name}-csr.pem -out ${component_name}-cert.pem \
        -CA ${domain_ca}-ca-cert.pem -CAkey ${domain_ca}-ca-key.pem \
        -CAcreateserial -days 365 -extensions v3_req -extfile component-extensions.cnf
    
    # Package for deployment
    create_certificate_package ${component_name}
}

create_certificate_package() {
    local component_name=$1
    
    mkdir -p /certs/deploy/${component_name}
    cp ${component_name}-cert.pem /certs/deploy/${component_name}/
    cp ${component_name}-key.pem /certs/deploy/${component_name}/
    cp root-ca-cert.pem /certs/deploy/${component_name}/
    
    # Create deployment manifest
    cat > /certs/deploy/${component_name}/manifest.yaml << EOF
component: ${component_name}
certificates:
  - type: tls_server
    file: ${component_name}-cert.pem
  - type: tls_private_key
    file: ${component_name}-key.pem
  - type: ca_bundle
    file: root-ca-cert.pem
validity_period: 365 days
renewal_required: 30 days before expiration
EOF
}
```

### Key Management System
```python
# O-RAN key management framework
import hashlib
import hmac
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets

class ORANKeyManager:
    def __init__(self):
        self.master_key = self._generate_master_key()
        self.key_derivation_params = {
            'iterations': 100000,
            'salt_length': 16,
            'key_length': 32
        }
    
    def _generate_master_key(self):
        """Generate cryptographically secure master key"""
        return secrets.token_bytes(32)
    
    def derive_component_key(self, component_id, purpose):
        """Derive key for specific component and purpose"""
        # Create unique derivation input
        derivation_input = f"{component_id}:{purpose}".encode('utf-8')
        
        # Generate salt
        salt = secrets.token_bytes(self.key_derivation_params['salt_length'])
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_derivation_params['key_length'],
            salt=salt,
            iterations=self.key_derivation_params['iterations']
        )
        
        derived_key = kdf.derive(self.master_key + derivation_input)
        
        return {
            'key': derived_key,
            'salt': salt,
            'component_id': component_id,
            'purpose': purpose
        }
    
    def encrypt_sensitive_data(self, data, component_id):
        """Encrypt sensitive data for component"""
        # Derive encryption key
        enc_key_info = self.derive_component_key(component_id, 'data_encryption')
        
        # Generate nonce for AES-GCM
        nonce = secrets.token_bytes(12)
        
        # Encrypt data
        aesgcm = AESGCM(enc_key_info['key'])
        ciphertext = aesgcm.encrypt(nonce, data.encode('utf-8'), None)
        
        return {
            'ciphertext': ciphertext,
            'nonce': nonce,
            'salt': enc_key_info['salt'],
            'component_id': component_id
        }
    
    def decrypt_sensitive_data(self, encrypted_data, component_id):
        """Decrypt sensitive data for component"""
        # Re-derive decryption key
        dec_key_info = self.derive_component_key(
            component_id, 
            'data_encryption'
        )
        
        # Verify salt matches
        if dec_key_info['salt'] != encrypted_data['salt']:
            raise ValueError("Salt mismatch - possible tampering")
        
        # Decrypt data
        aesgcm = AESGCM(dec_key_info['key'])
        plaintext = aesgcm.decrypt(
            encrypted_data['nonce'],
            encrypted_data['ciphertext'],
            None
        )
        
        return plaintext.decode('utf-8')

# Usage example
key_manager = ORANKeyManager()

# Encrypt configuration data
config_data = '{"database_password": "secret123", "api_keys": ["key1", "key2"]}'
encrypted_config = key_manager.encrypt_sensitive_data(config_data, "near-rt-ric")

# Decrypt when needed
decrypted_config = key_manager.decrypt_sensitive_data(encrypted_config, "near-rt-ric")
```

## Authentication and Authorization

### Mutual TLS Authentication
```yaml
# mTLS configuration for O-RAN interfaces
mtls_configuration:
  e2_interface:
    enabled: true
    certificate_authority: "control-plane-ca"
    client_certificate_required: true
    certificate_validity: "730 days"
    revocation_checking: "ocsp"
    cipher_suites:
      - "TLS_AES_256_GCM_SHA384"
      - "TLS_CHACHA20_POLY1305_SHA256"
      - "TLS_AES_128_GCM_SHA256"
  
  f1_interface:
    enabled: true
    certificate_authority: "user-plane-ca"
    client_certificate_required: true
    certificate_validity: "365 days"
    revocation_checking: "crl"
    cipher_suites:
      - "TLS_AES_128_GCM_SHA256"
      - "TLS_AES_256_GCM_SHA256"
  
  management_interface:
    enabled: true
    certificate_authority: "management-ca"
    client_certificate_required: true
    certificate_validity: "365 days"
    revocation_checking: "both"
    cipher_suites:
      - "TLS_AES_256_GCM_SHA384"
```

### Role-Based Access Control (RBAC)
```json
{
  "rbac_policy": {
    "roles": [
      {
        "name": "system_administrator",
        "permissions": [
          "full_system_access",
          "configuration_management",
          "security_policy_management",
          "audit_log_review"
        ],
        "scope": "global"
      },
      {
        "name": "network_engineer",
        "permissions": [
          "network_configuration",
          "performance_monitoring",
          "fault_management"
        ],
        "scope": "domain_specific"
      },
      {
        "name": "security_analyst",
        "permissions": [
          "security_monitoring",
          "threat_analysis",
          "incident_response"
        ],
        "scope": "security_domain"
      },
      {
        "name": "ric_developer",
        "permissions": [
          "xapp_deployment",
          "policy_management",
          "subscription_management"
        ],
        "scope": "ric_domain"
      }
    ],
    "role_mapping": {
      "ldap_groups": {
        "oran-admins": "system_administrator",
        "oran-engineers": "network_engineer",
        "oran-security": "security_analyst",
        "oran-developers": "ric_developer"
      }
    }
  }
}
```

## Security Monitoring and Analytics

### SIEM Integration Framework
```python
# Security Information and Event Management integration
import json
import time
from datetime import datetime
import elasticsearch
from kafka import KafkaProducer

class ORANSecurityMonitor:
    def __init__(self, es_host, kafka_bootstrap_servers):
        self.es_client = elasticsearch.Elasticsearch([es_host])
        self.kafka_producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        self.threat_intel_feeds = []
    
    def collect_security_events(self):
        """Collect security events from O-RAN components"""
        security_events = []
        
        # Collect from various sources
        events = [
            self.collect_authentication_logs(),
            self.collect_network_traffic_anomalies(),
            self.collect_configuration_changes(),
            self.collect_performance_anomalies()
        ]
        
        for event_list in events:
            security_events.extend(event_list)
        
        return security_events
    
    def collect_authentication_logs(self):
        """Collect authentication and access logs"""
        auth_events = []
        
        # Simulate log collection from components
        sample_logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "authentication_attempt",
                "source_component": "near-rt-ric",
                "user": "admin",
                "result": "success",
                "ip_address": "192.168.1.100",
                "session_id": "sess_" + secrets.token_hex(8)
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "authorization_failure",
                "source_component": "o-du",
                "user": "unknown_user",
                "resource": "/api/configuration",
                "reason": "insufficient_privileges",
                "ip_address": "10.0.0.50"
            }
        ]
        
        auth_events.extend(sample_logs)
        return auth_events
    
    def detect_security_threats(self, events):
        """Detect potential security threats from collected events"""
        threats = []
        
        for event in events:
            threat = self.analyze_event_for_threats(event)
            if threat:
                threats.append(threat)
        
        return threats
    
    def analyze_event_for_threats(self, event):
        """Analyze individual event for security threats"""
        threat_indicators = {
            "failed_login_attempts": 0,
            "unusual_access_patterns": False,
            "configuration_modifications": False,
            "network_anomalies": False
        }
        
        # Analyze authentication events
        if event.get("event_type") == "authentication_attempt":
            if event.get("result") == "failure":
                threat_indicators["failed_login_attempts"] += 1
                
                # Check for brute force patterns
                if threat_indicators["failed_login_attempts"] > 5:
                    return {
                        "threat_type": "brute_force_attack",
                        "severity": "high",
                        "confidence": 0.8,
                        "details": {
                            "target_component": event.get("source_component"),
                            "attacker_ip": event.get("ip_address"),
                            "attempt_count": threat_indicators["failed_login_attempts"]
                        }
                    }
        
        # Analyze configuration changes
        elif event.get("event_type") == "configuration_change":
            if not event.get("authorized"):
                return {
                    "threat_type": "unauthorized_configuration_change",
                    "severity": "critical",
                    "confidence": 0.9,
                    "details": {
                        "component": event.get("source_component"),
                        "change_type": event.get("change_type"),
                        "user": event.get("user", "unknown")
                    }
                }
        
        return None
    
    def generate_security_alert(self, threat):
        """Generate security alert for detected threat"""
        alert = {
            "alert_id": "alert_" + secrets.token_hex(12),
            "timestamp": datetime.utcnow().isoformat(),
            "threat": threat,
            "recommendations": self.get_threat_recommendations(threat["threat_type"]),
            "escalation_required": threat["severity"] in ["high", "critical"]
        }
        
        # Send to SIEM and alerting systems
        self.send_to_elasticsearch(alert)
        self.send_to_kafka(alert)
        
        return alert
    
    def get_threat_recommendations(self, threat_type):
        """Get recommended response actions for threat type"""
        recommendations = {
            "brute_force_attack": [
                "Block source IP address temporarily",
                "Reset authentication tokens for affected accounts",
                "Review and strengthen password policies",
                "Enable multi-factor authentication"
            ],
            "unauthorized_configuration_change": [
                "Immediately rollback unauthorized changes",
                "Investigate user account compromise",
                "Review access control policies",
                "Enhance audit logging for configuration changes"
            ],
            "network_anomaly": [
                "Isolate affected network segments",
                "Perform packet capture and analysis",
                "Review firewall and IDS/IPS rules",
                "Coordinate with network security team"
            ]
        }
        
        return recommendations.get(threat_type, ["Investigate incident", "Document findings"])

# Usage example
monitor = ORANSecurityMonitor(
    es_host="elasticsearch.internal:9200",
    kafka_bootstrap_servers=["kafka1:9092", "kafka2:9092"]
)

# Collect and analyze security events
events = monitor.collect_security_events()
threats = monitor.detect_security_threats(events)

for threat in threats:
    alert = monitor.generate_security_alert(threat)
    print(f"Security Alert Generated: {alert}")
```

## Compliance and Audit Requirements

### Regulatory Compliance Framework
```markdown
## O-RAN Security Compliance Matrix

### GDPR Compliance
- **Data Protection**: Implement privacy by design principles
- **Data Minimization**: Collect only necessary operational data
- **Right to Erasure**: Provide mechanisms for data deletion
- **Breach Notification**: 72-hour incident reporting requirement
- **Privacy Impact Assessments**: Regular DPIA for new features

### NIST Cybersecurity Framework
- **Identify**: Asset management, business environment, governance
- **Protect**: Access control, awareness training, data security
- **Detect**: Anomalies and events, continuous monitoring
- **Respond**: Response planning, communications, mitigation
- **Recover**: Recovery planning, improvements, communications

### ISO 27001 Requirements
- **Information Security Policy**: Documented security policies
- **Organization of Information Security**: Roles and responsibilities
- **Human Resource Security**: Background checks, training, termination
- **Asset Management**: Inventory and classification of assets
- **Access Control**: User access management, privilege management
- **Cryptography**: Key management, algorithm selection
- **Physical and Environmental Security**: Facility security, equipment security
- **Operations Security**: Operational procedures, malware protection
- **Communications Security**: Network controls, information transfer
- **System Acquisition**: Security requirements, supplier relationships
- **Incident Management**: Incident response, reporting, learning
- **Business Continuity**: BCM requirements, redundancy
- **Compliance**: Legal requirements, reviews, compliance measurements

### 3GPP Security Requirements
- **TS 33.501**: Security architecture and procedures for 5G
- **TS 33.102**: Security requirements for 3GPP systems
- **TS 33.401**: Security requirements for E-UTRAN
- **Authentication and key agreement protocols**
- **Network domain security**
- **Subscriber identity privacy**
```

This security architecture reference provides a comprehensive foundation for implementing robust security controls in O-RAN deployments, ensuring protection against evolving cyber threats while maintaining compliance with industry standards and regulations.