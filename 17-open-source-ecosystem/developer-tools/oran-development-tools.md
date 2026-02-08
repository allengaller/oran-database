# O-RAN Developer Tools and SDKs

## Overview
This document provides comprehensive information about development tools, SDKs, and frameworks specifically designed for O-RAN development, including IDE plugins, testing frameworks, simulation tools, and development environments.

## Development Environment Setup

### 1. Containerized Development Environment

```dockerfile
# Dockerfile for O-RAN Development Environment
FROM ubuntu:20.04

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    curl \
    wget \
    vim \
    nano \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" && \
    apt-get update && apt-get install -y docker-ce-cli

# Install Kubernetes tools
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install development tools
RUN pip3 install \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    pylint \
    requests \
    kubernetes \
    docker

# Install Go
ENV GO_VERSION=1.19.2
RUN wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz && \
    rm go${GO_VERSION}.linux-amd64.tar.gz

ENV PATH=$PATH:/usr/local/go/bin
ENV GOPATH=/go
ENV PATH=$PATH:$GOPATH/bin

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

# Install VS Code server
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Install O-RAN specific tools
RUN mkdir -p /opt/oran-tools

# Copy O-RAN development scripts
COPY oran-dev-setup.sh /opt/oran-tools/
RUN chmod +x /opt/oran-tools/oran-dev-setup.sh

# Set working directory
WORKDIR /workspace

# Expose ports
EXPOSE 8080 8443 3000

# Default command
CMD ["/usr/bin/code-server", "--bind-addr", "0.0.0.0:8080", "."]
```

### 2. Development Environment Configuration Scripts

```bash
#!/bin/bash
# oran-dev-setup.sh - O-RAN Development Environment Setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# System requirements check
check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check RAM
    RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [ $RAM_GB -lt 16 ]; then
        log_warn "Recommended minimum RAM is 16GB, found ${RAM_GB}GB"
    fi
    
    # Check CPU cores
    CPU_CORES=$(nproc)
    if [ $CPU_CORES -lt 8 ]; then
        log_warn "Recommended minimum CPU cores is 8, found ${CPU_CORES}"
    fi
    
    # Check disk space
    DISK_SPACE_GB=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ $DISK_SPACE_GB -lt 50 ]; then
        log_warn "Recommended minimum disk space is 50GB, found ${DISK_SPACE_GB}GB"
    fi
}

# Install base dependencies
install_base_dependencies() {
    log_info "Installing base dependencies..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y \
            build-essential \
            cmake \
            git \
            python3 \
            python3-pip \
            python3-venv \
            curl \
            wget \
            vim \
            docker.io \
            docker-compose
    elif command -v yum &> /dev/null; then
        sudo yum install -y \
            gcc \
            gcc-c++ \
            make \
            cmake \
            git \
            python3 \
            python3-pip \
            curl \
            wget \
            vim \
            docker \
            docker-compose
    else
        log_error "Unsupported package manager"
        exit 1
    fi
}

# Setup Python environment
setup_python_environment() {
    log_info "Setting up Python environment..."
    
    # Create virtual environment
    python3 -m venv ~/oran-env
    source ~/oran-env/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install O-RAN development packages
    pip install \
        pytest \
        pytest-cov \
        pytest-asyncio \
        black \
        flake8 \
        mypy \
        pylint \
        requests \
        kubernetes \
        docker \
        pyyaml \
        jinja2 \
        cryptography \
        paramiko
}

# Install O-RAN specific tools
install_oran_tools() {
    log_info "Installing O-RAN specific tools..."
    
    # Install O-DU/O-CU simulator
    mkdir -p ~/oran-tools/simulators
    cd ~/oran-tools/simulators
    
    # Download and build OAI RAN simulator
    if [ ! -d "openairinterface5g" ]; then
        git clone https://gitlab.eurecom.fr/oai/openairinterface5g.git
        cd openairinterface5g
        source oaienv
        cd cmake_targets
        ./build_oai -I -w SIMU --ninja
    fi
    
    # Install RIC simulator
    cd ~/oran-tools/simulators
    if [ ! -d "ric-simulator" ]; then
        git clone https://gerrit.oran-osc.org/r/simulators/ric-simulator
        cd ric-simulator
        make
    fi
}

# Setup IDE configurations
setup_ide_configurations() {
    log_info "Setting up IDE configurations..."
    
    # VS Code extensions
    code_extensions=(
        "ms-python.python"
        "ms-vscode.cpptools"
        "redhat.vscode-yaml"
        "ms-kubernetes-tools.vscode-kubernetes-tools"
        "ms-azuretools.vscode-docker"
        "eamodio.gitlens"
        "ms-vscode.hexeditor"
    )
    
    for extension in "${code_extensions[@]}"; do
        code --install-extension "$extension" || log_warn "Failed to install $extension"
    done
    
    # Create VS Code settings
    mkdir -p ~/.config/Code/User
    cat > ~/.config/Code/User/settings.json << EOF
{
    "python.defaultInterpreterPath": "~/oran-env/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "files.associations": {
        "*.yang": "yang",
        "*.asn": "asn1"
    },
    "yaml.schemas": {
        "kubernetes": "*.yaml"
    }
}
EOF
}

# Setup pre-commit hooks
setup_git_hooks() {
    log_info "Setting up Git hooks..."
    
    # Install pre-commit
    pip install pre-commit
    
    # Create .pre-commit-config.yaml
    cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.3.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
      
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.961
    hooks:
      - id: mypy
EOF
    
    # Install hooks
    pre-commit install
}

# Create project templates
create_project_templates() {
    log_info "Creating project templates..."
    
    mkdir -p ~/oran-templates
    
    # Python xApp template
    mkdir -p ~/oran-templates/python-xapp
    cat > ~/oran-templates/python-xapp/template.py << EOF
#!/usr/bin/env python3
"""
O-RAN xApp Template
"""

import logging
import asyncio
from typing import Dict, Any
from ricxappframe.xapp_frame import RMRXapp, rmr
from mdclogpy import Logger

logger = Logger(name=__name__)
logger.set_level(logging.INFO)

class XAppTemplate:
    def __init__(self):
        self.rmr_xapp = None
        self.running = False
        
    async def start(self):
        """Start the xApp"""
        logger.info("Starting xApp...")
        
        # Initialize RMR
        self.rmr_xapp = RMRXapp(self._default_handler)
        self.rmr_xapp.run()
        
        self.running = True
        logger.info("xApp started successfully")
        
        # Main loop
        while self.running:
            await asyncio.sleep(1)
            
    def _default_handler(self, summary: Dict[str, Any], sbuf: rmr.RmrBuf):
        """Default message handler"""
        logger.debug(f"Received message: {summary}")
        # Process message here
        self.rmr_xapp.rmr_free(sbuf)
        
    def stop(self):
        """Stop the xApp"""
        logger.info("Stopping xApp...")
        self.running = False
        if self.rmr_xapp:
            self.rmr_xapp.stop()

if __name__ == "__main__":
    xapp = XAppTemplate()
    try:
        asyncio.run(xapp.start())
    except KeyboardInterrupt:
        xapp.stop()
EOF

    # Create Dockerfile for xApp
    cat > ~/oran-templates/python-xapp/Dockerfile << EOF
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "template.py"]
EOF

    # Create requirements.txt
    cat > ~/oran-templates/python-xapp/requirements.txt << EOF
ricxappframe>=3.0.0
mdclogpy>=1.0.0
EOF
}

# Main setup function
main() {
    log_info "Starting O-RAN development environment setup..."
    
    check_system_requirements
    install_base_dependencies
    setup_python_environment
    install_oran_tools
    setup_ide_configurations
    setup_git_hooks
    create_project_templates
    
    log_info "Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Activate Python environment: source ~/oran-env/bin/activate"
    echo "2. Navigate to your project directory"
    echo "3. Start developing O-RAN applications!"
}

# Run setup
main "$@"
```

## Integrated Development Environments (IDEs)

### 1. VS Code Extensions for O-RAN Development

```json
{
    "recommendations": [
        "ms-python.python",
        "ms-vscode.cpptools",
        "redhat.vscode-yaml",
        "ms-kubernetes-tools.vscode-kubernetes-tools",
        "ms-azuretools.vscode-docker",
        "eamodio.gitlens",
        "timonwong.shellcheck",
        "ms-vscode.hexeditor",
        "yzhang.markdown-all-in-one",
        "davidanson.vscode-markdownlint",
        "ms-vscode.vscode-typescript-next"
    ],
    "settings": {
        "[python]": {
            "editor.defaultFormatter": "ms-python.black-formatter",
            "editor.formatOnSave": true
        },
        "[yaml]": {
            "editor.defaultFormatter": "redhat.vscode-yaml",
            "editor.formatOnSave": true
        },
        "python.linting.enabled": true,
        "python.linting.flake8Enabled": true,
        "python.testing.pytestEnabled": true,
        "yaml.schemas": {
            "kubernetes": "/*.yaml"
        },
        "files.associations": {
            "*.yang": "yang",
            "*.asn": "asn1",
            "*.proto": "proto3"
        }
    }
}
```

### 2. PyCharm Professional Configuration

```xml
<!-- .idea/codeStyles/Project.xml -->
<code_scheme name="O-RAN-Style" version="173">
  <Python>
    <option name="SPACE_BEFORE_PY_COLON" value="true" />
    <option name="SPACE_AROUND_POWER_OPERATOR" value="true" />
    <option name="SPACE_BEFORE_BACKSLASH" value="true" />
  </Python>
  <codeStyleSettings language="Python">
    <option name="RIGHT_MARGIN" value="88" />
    <option name="ALIGN_MULTILINE_PARAMETERS" value="false" />
    <option name="SPACE_BEFORE_PY_COLON" value="true" />
    <option name="SPACE_AROUND_POWER_OPERATOR" value="true" />
    <option name="SPACE_BEFORE_BACKSLASH" value="true" />
  </codeStyleSettings>
</code_scheme>
```

## Testing and Validation Tools

### 1. Automated Testing Framework

```python
#!/usr/bin/env python3
"""
O-RAN Testing Framework
"""

import unittest
import asyncio
import logging
from typing import Dict, List, Any
import json
import time
from dataclasses import dataclass

@dataclass
class TestResult:
    test_name: str
    status: str  # PASS, FAIL, SKIP
    duration: float
    error_message: str = ""
    metrics: Dict[str, Any] = None

class ORANTestCase(unittest.TestCase):
    """Base class for O-RAN test cases"""
    
    def setUp(self):
        """Setup test environment"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.start_time = time.time()
        self.test_metrics = {}
        
    def tearDown(self):
        """Cleanup after test"""
        duration = time.time() - self.start_time
        self.logger.info(f"Test completed in {duration:.2f} seconds")
        
    def assertRICConnection(self, ric_endpoint: str):
        """Assert RIC connection is established"""
        # Implementation for RIC connection testing
        pass
        
    def assertE2Interface(self, e2_messages: List[Dict]):
        """Assert E2 interface functionality"""
        # Implementation for E2 interface testing
        pass
        
    def assertPerformanceMetrics(self, metrics: Dict[str, float], 
                               thresholds: Dict[str, float]):
        """Assert performance meets thresholds"""
        for metric, threshold in thresholds.items():
            if metric in metrics:
                self.assertGreaterEqual(metrics[metric], threshold,
                                      f"{metric} below threshold")

class RICTestSuite:
    """Comprehensive RIC testing suite"""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.logger = logging.getLogger(__name__)
        
    async def run_near_rt_ric_tests(self) -> List[TestResult]:
        """Run Near-RT RIC tests"""
        tests = [
            self.test_ric_startup_sequence,
            self.test_e2_connection_handling,
            self.test_xapp_lifecycle,
            self.test_policy_management,
            self.test_performance_monitoring
        ]
        
        results = []
        for test_func in tests:
            try:
                start_time = time.time()
                await test_func()
                duration = time.time() - start_time
                results.append(TestResult(
                    test_name=test_func.__name__,
                    status="PASS",
                    duration=duration
                ))
            except Exception as e:
                duration = time.time() - start_time
                results.append(TestResult(
                    test_name=test_func.__name__,
                    status="FAIL",
                    duration=duration,
                    error_message=str(e)
                ))
                
        self.test_results.extend(results)
        return results
    
    async def test_ric_startup_sequence(self):
        """Test RIC startup sequence"""
        self.logger.info("Testing RIC startup sequence...")
        # Implementation for startup testing
        await asyncio.sleep(0.1)  # Simulate test execution
        
    async def test_e2_connection_handling(self):
        """Test E2 connection handling"""
        self.logger.info("Testing E2 connection handling...")
        # Implementation for E2 testing
        await asyncio.sleep(0.1)
        
    async def test_xapp_lifecycle(self):
        """Test xApp lifecycle management"""
        self.logger.info("Testing xApp lifecycle...")
        # Implementation for xApp testing
        await asyncio.sleep(0.1)
        
    async def test_policy_management(self):
        """Test policy management functionality"""
        self.logger.info("Testing policy management...")
        # Implementation for policy testing
        await asyncio.sleep(0.1)
        
    async def test_performance_monitoring(self):
        """Test performance monitoring capabilities"""
        self.logger.info("Testing performance monitoring...")
        # Implementation for performance testing
        await asyncio.sleep(0.1)

# CLI interface for testing
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='O-RAN Testing Framework')
    parser.add_argument('--suite', choices=['near-rt-ric', 'non-rt-ric', 'fronthaul'],
                       help='Test suite to run')
    parser.add_argument('--output', default='test-results.json',
                       help='Output file for results')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Run tests
    test_suite = RICTestSuite()
    
    if args.suite == 'near-rt-ric':
        results = asyncio.run(test_suite.run_near_rt_ric_tests())
    else:
        results = []
    
    # Output results
    results_dict = [vars(r) for r in results]
    with open(args.output, 'w') as f:
        json.dump(results_dict, f, indent=2)
    
    passed = len([r for r in results if r.status == 'PASS'])
    total = len(results)
    print(f"Tests completed: {passed}/{total} passed")

if __name__ == "__main__":
    main()
```

### 2. Network Simulation Tools

```python
#!/usr/bin/env python3
"""
O-RAN Network Simulator
"""

import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import random
import time

@dataclass
class NetworkNode:
    node_id: str
    node_type: str  # O-RU, O-DU, O-CU, RIC
    ip_address: str
    status: str = "active"
    metrics: Dict[str, float] = field(default_factory=dict)
    
class ORANNetworkSimulator:
    def __init__(self):
        self.nodes: Dict[str, NetworkNode] = {}
        self.connections: List[tuple] = []
        self.logger = logging.getLogger(__name__)
        
    def add_node(self, node_id: str, node_type: str, ip_address: str):
        """Add a network node to the simulation"""
        node = NetworkNode(node_id, node_type, ip_address)
        self.nodes[node_id] = node
        self.logger.info(f"Added {node_type} node {node_id} at {ip_address}")
        
    def connect_nodes(self, node1_id: str, node2_id: str):
        """Create connection between two nodes"""
        if node1_id in self.nodes and node2_id in self.nodes:
            self.connections.append((node1_id, node2_id))
            self.logger.info(f"Connected {node1_id} to {node2_id}")
        else:
            self.logger.error("Invalid node IDs for connection")
            
    async def simulate_network_traffic(self, duration_seconds: int = 60):
        """Simulate network traffic and generate metrics"""
        self.logger.info(f"Starting network traffic simulation for {duration_seconds}s")
        
        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            # Simulate traffic between connected nodes
            for node1_id, node2_id in self.connections:
                if random.random() < 0.8:  # 80% chance of traffic
                    await self._simulate_traffic_between_nodes(node1_id, node2_id)
                    
            # Update node metrics
            await self._update_node_metrics()
            
            await asyncio.sleep(1)  # 1-second intervals
            
    async def _simulate_traffic_between_nodes(self, node1_id: str, node2_id: str):
        """Simulate traffic between two specific nodes"""
        node1 = self.nodes[node1_id]
        node2 = self.nodes[node2_id]
        
        # Simulate latency
        latency = random.uniform(0.5, 5.0)  # ms
        packet_loss = random.uniform(0, 0.02)  # 0-2%
        throughput = random.uniform(100, 1000)  # Mbps
        
        # Update metrics for both nodes
        node1.metrics.update({
            f"latency_to_{node2_id}": latency,
            f"packet_loss_to_{node2_id}": packet_loss,
            f"throughput_to_{node2_id}": throughput
        })
        
        node2.metrics.update({
            f"latency_to_{node1_id}": latency,
            f"packet_loss_to_{node1_id}": packet_loss,
            f"throughput_to_{node1_id}": throughput
        })
        
    async def _update_node_metrics(self):
        """Update overall node metrics"""
        for node in self.nodes.values():
            # Simulate CPU and memory usage
            node.metrics["cpu_usage"] = random.uniform(20, 80)
            node.metrics["memory_usage"] = random.uniform(30, 70)
            
            # Simulate specific metrics based on node type
            if node.node_type == "O-RU":
                node.metrics["rf_power"] = random.uniform(30, 50)
                node.metrics["antenna_gain"] = random.uniform(8, 15)
            elif node.node_type == "O-DU":
                node.metrics["processing_load"] = random.uniform(40, 90)
                node.metrics["connected_ues"] = random.randint(50, 200)
            elif node.node_type == "RIC":
                node.metrics["policy_decisions"] = random.randint(100, 1000)
                node.metrics["e2_connections"] = random.randint(10, 50)
                
    def get_network_topology(self) -> Dict[str, Any]:
        """Get current network topology"""
        return {
            "nodes": [vars(node) for node in self.nodes.values()],
            "connections": self.connections,
            "timestamp": time.time()
        }
        
    def get_node_metrics(self, node_id: str) -> Optional[Dict[str, float]]:
        """Get metrics for specific node"""
        if node_id in self.nodes:
            return self.nodes[node_id].metrics
        return None

# Example usage
async def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create simulator
    simulator = ORANNetworkSimulator()
    
    # Add nodes
    simulator.add_node("oru-001", "O-RU", "192.168.1.10")
    simulator.add_node("odu-001", "O-DU", "192.168.1.20")
    simulator.add_node("ocu-001", "O-CU", "192.168.1.30")
    simulator.add_node("ric-001", "RIC", "192.168.1.40")
    
    # Create connections
    simulator.connect_nodes("oru-001", "odu-001")
    simulator.connect_nodes("odu-001", "ocu-001")
    simulator.connect_nodes("ocu-001", "ric-001")
    
    # Run simulation
    await simulator.simulate_network_traffic(duration_seconds=30)
    
    # Output results
    topology = simulator.get_network_topology()
    print("Network Topology:")
    print(f"Nodes: {len(topology['nodes'])}")
    print(f"Connections: {len(topology['connections'])}")
    
    # Show metrics for RIC node
    ric_metrics = simulator.get_node_metrics("ric-001")
    if ric_metrics:
        print("\nRIC Metrics:")
        for key, value in ric_metrics.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Continuous Integration and Deployment

### 1. GitHub Actions Workflow for O-RAN Projects

```yaml
# .github/workflows/oran-ci.yml
name: O-RAN CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-20.04
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
        
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov black flake8 mypy
        
    - name: Code quality checks
      run: |
        black --check .
        flake8 .
        mypy .
        
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=./ --cov-report=xml
        
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  docker-build:
    needs: build-and-test
    runs-on: ubuntu-20.04
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      
    - name: Login to DockerHub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: oranorg/${{ github.event.repository.name }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  kubernetes-deployment:
    needs: docker-build
    runs-on: ubuntu-20.04
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      
    - name: Deploy to Kubernetes
      run: |
        kubectl config use-context ${{ secrets.KUBE_CONTEXT }}
        kubectl apply -f k8s/deployment.yaml
        kubectl rollout status deployment/${{ github.event.repository.name }}
```

### 2. Helm Chart for O-RAN Components

```yaml
# charts/oran-component/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "oran-component.fullname" . }}
  labels:
    {{- include "oran-component.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "oran-component.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "oran-component.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
              protocol: TCP
          env:
            - name: RIC_ENDPOINT
              value: {{ .Values.ric.endpoint }}
            - name: E2_PORT
              value: "{{ .Values.e2.port }}"
            - name: LOG_LEVEL
              value: {{ .Values.log.level }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
---
# charts/oran-component/values.yaml
replicaCount: 1

image:
  repository: oranorg/component
  pullPolicy: IfNotPresent
  tag: ""

ric:
  endpoint: "ric-platform:38000"

e2:
  port: 36421

service:
  type: ClusterIP
  port: 8080

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

log:
  level: "INFO"

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

These developer tools and frameworks provide a comprehensive foundation for O-RAN development, testing, and deployment activities.