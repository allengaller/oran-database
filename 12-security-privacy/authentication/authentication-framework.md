# O-RAN Authentication Framework

## Overview
This document provides a comprehensive authentication framework for O-RAN systems, covering multi-factor authentication, certificate management, and secure credential handling.

## Authentication Architecture

### Multi-Factor Authentication (MFA)
```yaml
mfa_configuration:
  primary_auth: "username_password"
  secondary_auth: 
    - "totp_token"
    - "smart_card"
    - "biometric_verification"
  tertiary_auth: "hardware_security_module"
  
authentication_levels:
  level_1: "basic_access"
  level_2: "administrative_access" 
  level_3: "root_access"
  level_4: "security_administration"
```

### PKI Certificate Management
```bash
#!/bin/bash
# O-RAN PKI certificate management system

# Certificate Authority hierarchy setup
setup_oran_ca() {
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
}
```

### OAuth 2.0 Implementation
```json
{
  "oauth2_configuration": {
    "authorization_server": "https://auth.oran.org",
    "token_endpoint": "https://auth.oran.org/oauth2/token",
    "client_registration": {
      "client_id": "oran-component-001",
      "client_secret": "generated-secret-key",
      "redirect_uris": [
        "https://near-rt-ric.oran.org/callback",
        "https://smo.oran.org/auth/callback"
      ],
      "grant_types": ["authorization_code", "client_credentials"],
      "response_types": ["code"],
      "scopes": ["read", "write", "admin"]
    },
    "jwt_configuration": {
      "signing_algorithm": "RS256",
      "token_lifetime": 3600,
      "refresh_token_lifetime": 86400,
      "issuer": "https://auth.oran.org"
    }
  }
}
```

## Security Protocols

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
```

### Session Management
```python
# Secure session management for O-RAN components
import hashlib
import secrets
from datetime import datetime, timedelta

class ORANSessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = 3600  # 1 hour
    
    def create_session(self, user_id, auth_level):
        """Create secure session for authenticated user"""
        session_id = secrets.token_urlsafe(32)
        session_token = hashlib.sha256(
            f"{user_id}:{session_id}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'auth_level': auth_level,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'session_token': session_token,
            'ip_address': self.get_client_ip()
        }
        
        return session_id, session_token
    
    def validate_session(self, session_id, session_token):
        """Validate session authenticity and freshness"""
        if session_id not in self.sessions:
            return False, "Invalid session"
        
        session = self.sessions[session_id]
        
        # Check token validity
        expected_token = hashlib.sha256(
            f"{session['user_id']}:{session_id}:{session['created_at'].isoformat()}".encode()
        ).hexdigest()
        
        if session_token != expected_token:
            return False, "Invalid session token"
        
        # Check session timeout
        if datetime.utcnow() > session['last_activity'] + timedelta(seconds=self.session_timeout):
            del self.sessions[session_id]
            return False, "Session expired"
        
        # Update last activity
        session['last_activity'] = datetime.utcnow()
        
        return True, "Session valid"
    
    def get_client_ip(self):
        """Get client IP address (implementation dependent)"""
        # This would typically come from request headers
        return "192.168.1.100"
```

## Best Practices

### Credential Security
- Use strong password policies (minimum 12 characters, mixed case, numbers, symbols)
- Implement password hashing with bcrypt or Argon2
- Enable automatic password rotation every 90 days
- Store credentials in encrypted vaults (HashiCorp Vault, AWS Secrets Manager)
- Never log passwords or sensitive credentials

### Certificate Management
- Regular certificate rotation (annually for root CAs, semi-annually for intermediate CAs)
- Automated certificate renewal processes
- Proper certificate revocation procedures
- Certificate transparency logging
- Backup of private keys with hardware security modules

### Audit and Monitoring
- Log all authentication attempts (successful and failed)
- Monitor for unusual authentication patterns
- Implement account lockout after failed attempts
- Regular security audits of authentication systems
- Compliance reporting for regulatory requirements