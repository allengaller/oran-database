---
title: "Post-Quantum Cryptography for AI-RAN"
description: "> **Updated: 2026-05** | NIST PQC Standards, O-RAN WG11 O-R006 v02.00, 6G Roadmap"
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-08-25"
keywords: ['O-RAN', 'AI-RAN', 'RIC']
---

# Post-Quantum Cryptography for AI-RAN

> **Updated: 2026-05** | NIST PQC Standards, O-RAN WG11 O-R006 v02.00, 6G Roadmap

## Overview

Quantum computers capable of breaking RSA-2048 and ECC-256 are projected within **10-15 years** (consensus estimate as of 2026). For AI-RAN systems deployed today with a **15-20 year operational lifespan**, this creates a unique threat: **"harvest now, decrypt later"** attacks where encrypted O-RAN traffic is recorded today and decrypted when quantum computers mature.

The **O-RAN Alliance WG11** published **O-R006 v02.00** (2026) — the **Post-Quantum Migration Guide** — outlining how operators should begin transitioning to quantum-safe cryptography. This chapter covers:

- **NIST PQC standards** (Kyber, Dilithium, SPHINCS+, FALCON)
- **Integration with O-RAN interfaces** (E2, A1, O1, O2)
- **Migration roadmap** (2026-2030)
- **Quantum-safe RIC communication patterns**

---

## The Quantum Threat to RAN

### Why RAN Must Care

| Asset at Risk | Current Protection | Quantum Threat | Time Horizon |
|:---|:---|:---|:---|
| **A1 policies** | TLS 1.3 (ECDHE) | Shor's algorithm breaks ECDH | 2035-2040 |
| **E2 telemetry** | TLS 1.3 + mTLS | Same — asymmetric key exchange broken | 2035-2040 |
| **Model weights (at rest)** | AES-256 | Grover's algorithm halves key strength (AES-128 safe) | Less urgent |
| **Signed policies** | RSA-2048/ECDSA-P256 | Shor's algorithm — total break | 2035-2040 |
| **Audit logs (long retention)** | Encrypted archive | Harvest now, decrypt later | **Already at risk** |

### The "Harvest Now, Decrypt Later" Problem

```
2026:  Attacker records encrypted A1 policies (TLS 1.3 with ECDHE)
       Stores in cold storage (exabytes cheap)
       
2038:  Quantum computer with ~4000 logical qubits available
       Runs Shor's algorithm → recovers ECDHE private keys
       Decrypts 12 years of A1 policies
       Result: Complete historical topology of operator network
              + all strategic decisions + AI model configurations
```

**Implication**: Anything encrypted today that has **long-term confidentiality requirements** (topology, strategic AI policies, subscriber data) must be **re-encrypted with PQC** or never transmitted in classical form.

---

## NIST Post-Quantum Standards (2024-2026)

### The Four Standardized Algorithms

| Algorithm | Type | Use Case | Key Size | Signature/Ciphertext | Performance |
|:---|:---|:---|:---|:---|:---|
| **ML-KEM (Kyber)** | Key Encapsulation | TLS key exchange | 800-1500 B | 768-1568 B | Very fast |
| **ML-DSA (Dilithium)** | Digital Signature | Code/policy signing | 1.3-2.5 KB | 2.4-4.6 KB | Fast |
| **SLH-DSA (SPHINCS+)** | Digital Signature | Long-term archival | 32-64 B | 7.9-49 KB | Slow |
| **FN-DSA (FALCON)** | Digital Signature | Certificates, TLS | 1.3-1.8 KB | 666-1.2 KB | Medium |

### Selection Guide for O-RAN

| O-RAN Use Case | Recommended Algorithm | Why |
|:---|:---|:---|
| **E2/A1/O1 TLS** | ML-KEM-768 + ML-DSA-44 (hybrid) | Fast key exchange + signatures |
| **A1 policy signing** | ML-DSA-44 | Compact signature, fast verify |
| **Audit log signing** (long retention) | SLH-DSA-128s | Long-term quantum-safe, conservative |
| **xApp/rApp container signing** | ML-DSA-65 | Balance of size and security |
| **Operator root CA** | SLH-DSA-256s | Decades-long validity, max security |

---

## Hybrid Cryptography: The Migration Strategy

### What Is Hybrid?

**Hybrid cryptography** combines classical (ECDHE/ECDSA) and post-quantum (Kyber/Dilithium) algorithms in a single protocol. If the PQC algorithm has an undiscovered weakness, the classical algorithm still protects. If a quantum computer arrives, the PQC algorithm still protects.

```
TLS 1.3 Hybrid Handshake:
  Client Hello:
    key_share: x25519 + ML-KEM-768   # Both offered
    signature_algorithms: ecdsa_secp256r1 + ml-dsa-44
  
  Server Hello:
    key_share: x25519 + ML-KEM-768   # Both used
    signature: ecdsa_secp256r1 AND ml-dsa-44  # Dual-signed
  
  Shared secret = KDF(x25519_shared || ML-KEM_shared)
  → Compromise of ONE algorithm does not compromise session
```

### Why Hybrid Is Required

- **Conservative operators** won't deploy PQC-only until 2030+
- **Regulatory uncertainty** — some regimes may require classical backup
- **Interoperability** — legacy devices may not support PQC
- **Risk mitigation** — if a PQC algorithm is broken, classical still works

---

## Integration with O-RAN Interfaces

### E2 Interface (Near-RT RIC ↔ O-DU)

#### Current State (2024)
- TLS 1.3 with ECDHE-P256
- mTLS with X.509 certificates
- SCTP transport (in some implementations)

#### PQC Migration Path

```yaml
# e2-tls-config.yaml — Hybrid E2 TLS configuration
apiVersion: security.oran.io/v1
kind: E2TLSProfile
metadata:
  name: e2-hybrid-2026
spec:
  min_tls_version: "1.3"
  
  key_exchange:
    mode: hybrid
    classical: x25519
    post_quantum: ml-kem-768
  
  signatures:
    mode: hybrid
    classical: ecdsa_secp256r1_sha256
    post_quantum: ml-dsa-44
  
  certificates:
    issuer: oran-hybrid-ca
    validity_days: 365
    dual_signed: true  # Both classical + PQC signatures
  
  fallback:
    allow_classical_only: false  # Enforce hybrid
```

#### Performance Impact

| Metric | Classical Only | Hybrid (Kyber+X25519) | Delta |
|:---|:---|:---|:---|
| TLS handshake time | 12 ms | 15 ms | +25% |
| Certificate chain size | 4 KB | 8 KB | +100% |
| Bandwidth per handshake | 5 KB | 10 KB | +100% |
| CPU per handshake | 1x | 1.3x | +30% |

**Impact on E2**: Negligible — handshakes are infrequent (per-session, not per-message).

### A1 Interface (Non-RT RIC ↔ Near-RT RIC)

A1 carries **strategic AI policies** — high confidentiality value, long-term sensitivity.

#### PQC-Secured A1 Policy

```python
# a1_pqc_signer.py — Sign A1 policies with hybrid signatures
class A1HybridSigner:
    def __init__(self, classical_key, pqc_key):
        self.classical_key = classical_key  # ECDSA-P256
        self.pqc_key = pqc_key              # ML-DSA-44
    
    def sign_policy(self, policy: A1Policy) -> SignedPolicy:
        canonical = json.dumps(policy.to_dict(), sort_keys=True).encode()
        
        # Dual-sign: both algorithms must validate
        classical_sig = self.classical_key.sign(canonical)
        pqc_sig = self.pqc_key.sign(canonical)
        
        return SignedPolicy(
            policy=policy,
            signatures={
                'classical': {
                    'algorithm': 'ecdsa_secp256r1_sha256',
                    'value': base64.b64encode(classical_sig).decode()
                },
                'post_quantum': {
                    'algorithm': 'ml-dsa-44',
                    'value': base64.b64encode(pqc_sig).decode()
                }
            },
            signer_cert_chain=self._dual_cert_chain()
        )
```

### O1 / O2 Interfaces (Management)

O1 (management) and O2 (orchestration) carry **configuration, telemetry, and orchestration commands**. Both need PQC protection.

**Special consideration**: O2 orchestrates K8S resources including AI model deployments. **Model signing must be PQC** to prevent "harvest now, compromise later" attacks on model integrity.

---

## Migration Roadmap: 2026-2030

### Phase 1: Inventory and Cryptographic Agility (2026)

**Goal**: Know what you have and be able to swap algorithms.

- [ ] Inventory all TLS endpoints in RIC (E2, A1, O1, O2, Kafka, gRPC)
- [ ] Identify all signing keys (xApp/rApp code signing, policy signing, CA roots)
- [ ] Implement **crypto-agility** — abstraction layer that can swap algorithms without code changes
- [ ] Test NIST reference implementations in lab
- [ ] Document which data has long-term confidentiality needs

### Phase 2: Hybrid Deployment in Non-Production (2027)

**Goal**: Deploy hybrid TLS in dev/staging RIC.

- [ ] Stand up **hybrid PKI** (dual-signed certificates with classical + PQC)
- [ ] Deploy hybrid TLS on E2, A1 endpoints in lab
- [ ] Validate with reference xApps/rApps
- [ ] Measure performance impact at scale (100+ cells)
- [ ] Update certificate rotation automation (PQC certs are larger)

### Phase 3: Hybrid Production Rollout (2028)

**Goal**: Hybrid mode in production for high-value interfaces.

- [ ] Migrate A1 interface to hybrid (strategic policies are high-value)
- [ ] Migrate audit log signing to SLH-DSA (long retention requirement)
- [ ] Migrate model signing to ML-DSA-65
- [ ] Maintain classical fallback for legacy devices

### Phase 4: PQC-Only Where Possible (2029-2030)

**Goal**: Pure PQC where all endpoints support it.

- [ ] Decommission classical-only endpoints
- [ ] Re-encrypt archived data with PQC (for long-retention records)
- [ ] Transition root CAs to SLH-DSA-256s

### K8S Implementation: Hybrid Ingress Controller

```yaml
# nginx-ingress-pqc.yaml — Hybrid TLS termination for RIC APIs
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ric-api-ingress
  namespace: near-rt-ric
  annotations:
    nginx.ingress.kubernetes.io/ssl-ciphers: "TLS_AES_256_GCM_SHA384"
    nginx.ingress.kubernetes.io/ssl-pqc-kem: "ml-kem-768"
    nginx.ingress.kubernetes.io/ssl-pqc-signature: "ml-dsa-44"
    nginx.ingress.kubernetes.io/ssl-hybrid-mode: "true"
spec:
  tls:
  - hosts:
    - ric-api.operator.com
    secretName: ric-hybrid-tls  # Contains hybrid cert (dual-signed)
  rules:
  - host: ric-api.operator.com
    http:
      paths:
      - path: /a1
        pathType: Prefix
        backend:
          service:
            name: a1-policy-service
            port:
              number: 443
```

---

## Quantum-Safe RIC Communication Patterns

### Pattern 1: Pre-Shared PQC Keys

For latency-sensitive E2 traffic where handshake cost matters:

```python
# preshared_pqc.py — Use ML-KEM to pre-establish shared secrets
class PresharedPQCSession:
    def __init__(self, ric_id: str, du_id: str, pqc_key: MLKEMKey):
        # On session setup, do one ML-KEM exchange
        # Derive long-term symmetric key
        self.shared_secret = pqc_key.key_exchange(peer_public_key)
        self.symmetric_key = HKDF(self.shared_secret, salt=ric_id + du_id)
        
        # Use symmetric key for all subsequent messages
        self.cipher = ChaCha20Poly1305(self.symmetric_key)
    
    def encrypt_message(self, plaintext: bytes, nonce: bytes) -> bytes:
        return self.cipher.encrypt(nonce, plaintext)
```

**Benefit**: One quantum-safe handshake, then fast symmetric encryption.

### Pattern 2: Quantum Key Distribution (QKD) Integration

For ultra-high-value links (e.g., inter-region RIC backbone), operators can deploy **QKD** to generate provably-secure symmetric keys.

```yaml
# qkd-integration.yaml — QKD as key source for symmetric encryption
apiVersion: security.oran.io/v1
kind: QKDLink
metadata:
  name: ric-backbone-qkd
spec:
  endpoints:
  - region: us-east
    ric: non-rt-ric-1
  - region: us-west
    ric: non-rt-ric-2
  
  qkd_provider: "toshiba-qkd"  # Or ID Quantique, etc.
  key_refresh_rate_hz: 1000    # 1000 fresh symmetric keys per second
  
  usage:
    encrypt:
    - traffic: "ric-to-ric-backbone"
      algorithm: "aes-256-gcm"  # Symmetric, quantum-safe
      key_source: "qkd"
```

### Pattern 3: Confidential Computing + PQC

Combine **hardware TEEs** (AMD SEV, Intel TDX, NVIDIA confidential computing) with PQC for defense-in-depth:

```
┌─────────────────────────────────────────────────┐
│  Confidential VM (AMD SEV-SNP)                   │
│  • Memory encrypted + integrity-protected        │
│  • Hardware-attested boot chain                   │
│                                                   │
│  ┌───────────────────────────────────────────┐  │
│  │  AI Agent (Tier 1 Strategic)              │  │
│  │  • Model weights in encrypted memory      │  │
│  │  • Reasoning chains never leave TEE       │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  Egress: ML-KEM-768 + ML-DSA-44 TLS             │
│  (Quantum-safe, dual-hybrid)                     │
└─────────────────────────────────────────────────┘
```

---

## K8S Infrastructure for PQC

### PQC Certificate Manager

```yaml
# cert-manager-pqc.yaml — Extends cert-manager for PQC
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: oran-pqc-issuer
spec:
  pqc:
    algorithm: ml-dsa-44
    hybridWith: ecdsa_secp256r1
    privateKey:
      secretName: pqc-issuer-key
    rootCA:
      secretName: pqc-root-ca  # SLH-DSA-256s signed
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: ric-api-hybrid-cert
  namespace: near-rt-ric
spec:
  secretName: ric-hybrid-tls
  issuerRef:
    name: oran-pqc-issuer
    kind: ClusterIssuer
  commonName: ric-api.operator.com
  duration: 2160h  # 90 days
  renewBefore: 360h
```

### PQC Library in Base Image

```dockerfile
# Dockerfile.pqc — Base image with PQC libraries
FROM ubuntu:22.04

# Install liboqs (Open Quantum Safe library)
RUN apt-get update && apt-get install -y \
    cmake ninja-build libssl-dev git && \
    git clone --branch main https://github.com/open-quantum-safe/liboqs.git && \
    cd liboqs && mkdir build && cd build && \
    cmake -GNinja -DBUILD_SHARED_LIBS=ON .. && \
    ninja && ninja install

# Install oqs-provider for OpenSSL 3
RUN git clone https://github.com/open-quantum-safe/oqs-provider.git && \
    cd oqs-provider && mkdir build && cd build && \
    cmake .. && make install

# Configure OpenSSL 3 to use PQC provider
RUN echo "[provider_sect]" >> /etc/ssl/openssl.cnf && \
    echo "oqsprovider = oqsprovider_sect" >> /etc/ssl/openssl.cnf

# Verify PQC works
RUN openssl list -kem-algorithms | grep -i kyber
```

---

## Testing PQC in the Lab

### Reference Testbed

```yaml
# pqc-testbed.yaml — Minimal PQC test environment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pqc-e2-simulator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pqc-e2-test
  template:
    metadata:
      labels:
        app: pqc-e2-test
    spec:
      containers:
      - name: e2-client
        image: oran/e2-simulator:pqc-2026.1
        env:
        - name: E2_TLS_MODE
          value: "hybrid"
        - name: E2_KEM_ALGORITHM
          value: "ml-kem-768"
        - name: E2_SIGNATURE_ALGORITHM
          value: "ml-dsa-44"
        command:
        - /bin/sh
        - -c
        - |
          # Run E2 handshake test 1000 times
          for i in $(seq 1 1000); do
            openssl s_client -connect e2-server:3801 \
              -groups x25519:kyber768 \
              -sigalgs ecdsa_secp256r1_sha256+ml_dsa_44 \
              < /dev/null
          done
```

### Performance Benchmarking

```bash
# Benchmark hybrid TLS vs classical
openssl speed rsa2048 ecdsap256 ml-dsa-44 ml-kem-768

# Expected results (Intel Xeon 2024):
# RSA-2048 sign:     1100 ops/sec
# ECDSA-P256 sign:   32000 ops/sec
# ML-DSA-44 sign:    12000 ops/sec   (slower than ECDSA, acceptable)
# ML-KEM-768 encap:  28000 ops/sec   (comparable to ECDHE)
```

---

## K8S Engineer Checklist

### Implement Today

- [ ] **Inventory cryptographic assets** — Where is RSA/ECC used?
- [ ] **Enable crypto-agility** — Abstract algorithm choice behind interfaces
- [ ] **Use AES-256 for data at rest** — Quantum-safe (Grover's only halves strength)
- [ ] **Sign audit logs with dual signatures** — Start now for long-retention data

### Implement This Quarter

- [ ] **Test liboqs + oqs-provider** — In lab environment
- [ ] **Stand up hybrid PKI** — cert-manager with PQC issuer
- [ ] **Benchmark hybrid TLS** — Measure latency and CPU impact
- [ ] **Update CI/CD** — Sign container images with ML-DSA-65

### Plan for 2027

- [ ] **Migrate A1 to hybrid** — Strategic policies have long-term sensitivity
- [ ] **Pilot QKD** — On highest-value backbone links
- [ ] **Train security team on PQC** — New operational procedures

---

## References

- [NIST Post-Quantum Cryptography Standardization](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [NIST FIPS 203: ML-KEM (Kyber)](https://csrc.nist.gov/pubs/fips/203/final)
- [NIST FIPS 204: ML-DSA (Dilithium)](https://csrc.nist.gov/pubs/fips/204/final)
- [NIST FIPS 205: SLH-DSA (SPHINCS+)](https://csrc.nist.gov/pubs/fips/205/final)
- [O-RAN WG11 O-R006 v02.00: Post-Quantum Migration Guide](https://www.o-ran.org/specifications)
- [Open Quantum Safe Project](https://openquantumsafe.org/)
- [Cloudflare: Post-Quantum for All (2024)](https://blog.cloudflare.com/post-quantum-for-all/)
- [NSA CNSA 2.0 Timeline](https://media.defense.gov/2022/Sep/07/2003071834/-1/-1/0/CSA_CNSA_2.0_ALGORITHMS_.PDF)
