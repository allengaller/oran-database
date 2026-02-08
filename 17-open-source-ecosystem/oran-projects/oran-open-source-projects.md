# O-RAN Open Source Projects Catalog

## Overview
This catalog provides a comprehensive overview of major open source projects related to O-RAN technology, including their features, architectures, use cases, and contribution opportunities.

## Major O-RAN Open Source Projects

### 1. O-RAN Software Community (OSC) Projects

#### RIC Platform (RIC-PLT)
```yaml
project_info:
  name: "RIC Platform"
  repository: "https://gerrit.oran-osc.org/r/ric-plt"
  license: "Apache 2.0"
  primary_language: "C++, Python, Go"
  stars: 450
  contributors: 180+

components:
  - near-rt-ric:
      description: "Near-Real Time RAN Intelligent Controller"
      key_features:
        - E2 interface implementation
        - xApp management framework
        - Policy management system
        - Real-time analytics processing
      architecture:
        - rmr_message_router: "Reliable Messaging Router for inter-component communication"
        - db_connector: "Database connectivity layer"
        - subscription_manager: "E2 subscription handling"
        - xapp_manager: "xApp lifecycle management"
      deployment:
        - containerized: "Docker/Kubernetes"
        - ha_ready: "High availability support"
        - scalable: "Horizontal scaling capabilities"
  
  - non-rt-ric:
      description: "Non-Real Time RAN Intelligent Controller"
      key_features:
        - A1 interface implementation
        - rApp management framework
        - Long-term analytics
        - Network optimization algorithms
      architecture:
        - policy_agent: "Policy decision point"
        - data_collector: "Multi-source data aggregation"
        - ml_engine: "Machine learning inference engine"
        - dashboard_ui: "Web-based management interface"
  
  - simulators:
      description: "O-RAN network simulators and test frameworks"
      components:
        - ric_simulator: "RIC platform simulation"
        - ran_simulator: "Radio Access Network simulation"
        - e2_term_sim: "E2 termination simulation"
        - a1_term_sim: "A1 termination simulation"
```

#### O-DU/O-CU High Layers
```yaml
project_info:
  name: "O-DU/O-CU High Layers"
  repository: "https://gerrit.oran-osc.org/r/o-du/o-du-high"
  license: "BSD 3-Clause"
  primary_language: "C"
  stars: 320
  contributors: 120+

architecture_overview:
  layers:
    - mac_layer:
        description: "Medium Access Control layer"
        protocols: ["MAC", "HARQ", "Scheduling"]
        interfaces: ["F1-U", "E1"]
    
    - rlc_layer:
        description: "Radio Link Control layer"
        protocols: ["RLC-AM", "RLC-UM", "RLC-TM"]
        interfaces: ["F1-U"]
    
    - pdcp_layer:
        description: "Packet Data Convergence Protocol layer"
        protocols: ["PDCP", "Header Compression"]
        interfaces: ["F1-U", "E1"]
    
    - rrc_layer:
        description: "Radio Resource Control layer"
        protocols: ["RRC", "NAS"]
        interfaces: ["F1-C", "NG-C"]

implementation_features:
  - multi_threading: "Thread-per-layer architecture"
  - vector_processing: "SIMD optimizations for packet processing"
  - dynamic_memory: "Pool-based memory management"
  - logging_framework: "Structured logging with multiple levels"
  - configuration_mgmt: "YANG-based configuration management"
```

### 2. OpenAirInterface (OAI) Projects

#### OAI RAN
```yaml
project_info:
  name: "OpenAirInterface RAN"
  repository: "https://gitlab.eurecom.fr/oai/openairinterface5g"
  license: "OAI Public License v1.1"
  primary_language: "C"
  stars: 2800
  contributors: 450+

supported_components:
  - oai_ru:
      description: "O-RAN Radio Unit implementation"
      features:
        - phy_layer: "Physical layer processing"
        - rf_interface: "RF device abstraction layer"
        - synchronization: "Timing and frequency synchronization"
        - beamforming: "Digital beamforming support"
      hardware_support:
        - usrp_series: "Ettus USRP devices"
        - blade_rf: "Nuand BladeRF"
        - lime_sdr: "LimeSDR family"
        - xilinx_rf: "Xilinx RFSoC platforms"
  
  - oai_du:
      description: "O-RAN Distributed Unit implementation"
      features:
        - f1_interface: "F1 interface protocol stack"
        - mac_scheduler: "Advanced MAC scheduling algorithms"
        - rrc_procedures: "Complete RRC state machine"
        - security_functions: "UE authentication and key derivation"
      oran_compliance:
        - split_option_7_2x: "Full compliance"
        - split_option_2: "Partial support"
        - ecpri_protocol: "Native implementation"
  
  - oai_cu:
      description: "O-RAN Centralized Unit implementation"
      features:
        - ng_interface: "Next Generation interface"
        - pdu_session: "5G PDU session management"
        - qoS_handling: "Quality of Service management"
        - mobility_mgmt: "UE mobility procedures"
```

### 3. ONAP Integration Projects

#### ONAP for O-RAN
```yaml
project_info:
  name: "ONAP O-RAN Integration"
  repository: "https://gerrit.onap.org/r/"
  license: "Apache 2.0"
  primary_language: "Java, Python"
  integration_level: "High"

key_integration_modules:
  - oran-control-loop:
      description: "Automated control loops for O-RAN optimization"
      control_loops:
        - load_balancing:
            trigger: "Cell overload detection"
            action: "UE handover optimization"
            metrics: ["PRB utilization", "RRC connection count"]
        
        - interference_management:
            trigger: "High interference levels"
            action: "Power control adjustment"
            metrics: ["RSRP", "SINR", "BLER"]
        
        - energy_optimization:
            trigger: "Low traffic periods"
            action: "Sleep mode activation"
            metrics: ["Traffic load", "Power consumption"]
  
  - oran-policy:
      description: "Policy management for O-RAN networks"
      policy_types:
        - qos_policy:
            scope: "Bearer level QoS parameters"
            enforcement: "PDCP layer"
            parameters: ["5QI", "ARP", "GFBR", "MFBR"]
        
        - slicing_policy:
            scope: "Network slice management"
            enforcement: "Core network level"
            parameters: ["Slice ID", "Resource allocation"]
        
        - security_policy:
            scope: "Access control and authentication"
            enforcement: "RRC and NAS layers"
            parameters: ["Security algorithms", "Key lifetimes"]
```

## Project Comparison Matrix

### Feature Comparison Table

| Feature | OSC RIC | OAI RAN | ONAP O-RAN | Commercial |
|---------|---------|---------|------------|------------|
| E2 Interface | ✓ Full | ✓ Partial | ✓ Via Integration | ✓ Full |
| A1 Interface | ✓ Full | ✗ | ✓ Full | ✓ Full |
| F1 Interface | ✗ | ✓ Full | ✗ | ✓ Full |
| CU/DU Split | ✗ | ✓ Options 2,7.2x | ✗ | ✓ All Options |
| xApp Support | ✓ Rich | ✗ | ✓ Via ONAP Apps | ✓ Proprietary |
| 5G NR Support | ✓ Basic | ✓ Full | ✓ Full | ✓ Full |
| LTE Support | ✓ Limited | ✓ Full | ✓ Full | ✓ Full |
| Containerization | ✓ Native | ✓ Docker | ✓ Kubernetes | ✓ Various |
| HA Support | ✓ Native | ✓ Manual | ✓ Native | ✓ Native |

### Performance Benchmarks

```python
#!/usr/bin/env python3
"""
O-RAN Project Performance Benchmarking Tool
"""

import time
import json
import subprocess
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    project_name: str
    test_name: str
    duration_ms: float
    throughput_mbps: float
    cpu_usage_percent: float
    memory_mb: float
    success_rate: float

class ORANBenchmarkSuite:
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        
    def run_e2_interface_benchmark(self) -> List[BenchmarkResult]:
        """Benchmark E2 interface performance"""
        projects = ["osc-ric", "onap-oran", "commercial-ref"]
        results = []
        
        for project in projects:
            result = self._benchmark_single_project(project, "e2_interface")
            results.append(result)
            
        self.results.extend(results)
        return results
    
    def run_xapp_performance_benchmark(self) -> List[BenchmarkResult]:
        """Benchmark xApp performance and resource usage"""
        xapps = ["load_balancer", "interference_mitigation", "energy_saver"]
        results = []
        
        for xapp in xapps:
            result = self._benchmark_xapp(xapp)
            results.append(result)
            
        self.results.extend(results)
        return results
    
    def _benchmark_single_project(self, project_name: str, test_type: str) -> BenchmarkResult:
        """Run benchmark for single project"""
        start_time = time.time()
        
        # Simulate benchmark execution
        if project_name == "osc-ric":
            duration = 15.2
            throughput = 1250.5
            cpu_usage = 45.3
            memory = 2048
            success_rate = 99.8
        elif project_name == "onap-oran":
            duration = 22.8
            throughput = 980.2
            cpu_usage = 62.1
            memory = 3072
            success_rate = 99.5
        else:  # commercial
            duration = 8.9
            throughput = 1850.0
            cpu_usage = 32.7
            memory = 1536
            success_rate = 99.9
            
        execution_time = (time.time() - start_time) * 1000
        
        return BenchmarkResult(
            project_name=project_name,
            test_name=test_type,
            duration_ms=duration,
            throughput_mbps=throughput,
            cpu_usage_percent=cpu_usage,
            memory_mb=memory,
            success_rate=success_rate
        )
    
    def _benchmark_xapp(self, xapp_name: str) -> BenchmarkResult:
        """Benchmark specific xApp"""
        # Simulate xApp benchmark
        metrics = {
            "load_balancer": {
                "duration": 5.2,
                "throughput": 5000,
                "cpu": 15.8,
                "memory": 512,
                "success": 99.9
            },
            "interference_mitigation": {
                "duration": 12.8,
                "throughput": 2500,
                "cpu": 28.4,
                "memory": 768,
                "success": 99.7
            },
            "energy_saver": {
                "duration": 8.1,
                "throughput": 1000,
                "cpu": 8.2,
                "memory": 256,
                "success": 99.9
            }
        }
        
        metric = metrics[xapp_name]
        return BenchmarkResult(
            project_name="reference-xapp",
            test_name=xapp_name,
            duration_ms=metric["duration"],
            throughput_mbps=metric["throughput"],
            cpu_usage_percent=metric["cpu"],
            memory_mb=metric["memory"],
            success_rate=metric["success"]
        )
    
    def generate_report(self, output_file: str = "benchmark-report.json"):
        """Generate comprehensive benchmark report"""
        report_data = {
            "timestamp": time.time(),
            "summary": {
                "total_tests": len(self.results),
                "avg_success_rate": sum(r.success_rate for r in self.results) / len(self.results),
                "best_performing": self._find_best_performing()
            },
            "detailed_results": [vars(result) for result in self.results]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        return report_data
    
    def _find_best_performing(self) -> Dict[str, str]:
        """Find best performing projects for each metric"""
        best_results = {}
        
        # Group results by test type
        test_groups = {}
        for result in self.results:
            if result.test_name not in test_groups:
                test_groups[result.test_name] = []
            test_groups[result.test_name].append(result)
        
        # Find best in each category
        for test_name, results in test_groups.items():
            # Best throughput
            best_throughput = max(results, key=lambda x: x.throughput_mbps)
            # Best latency
            best_latency = min(results, key=lambda x: x.duration_ms)
            # Best efficiency (throughput/cpu ratio)
            best_efficiency = max(results, key=lambda x: x.throughput_mbps/x.cpu_usage_percent)
            
            best_results[test_name] = {
                "best_throughput": best_throughput.project_name,
                "best_latency": best_latency.project_name,
                "best_efficiency": best_efficiency.project_name
            }
            
        return best_results

# Usage example
def main():
    benchmark_suite = ORANBenchmarkSuite()
    
    # Run benchmarks
    e2_results = benchmark_suite.run_e2_interface_benchmark()
    xapp_results = benchmark_suite.run_xapp_performance_benchmark()
    
    # Generate report
    report = benchmark_suite.generate_report("oran-benchmark-report.json")
    
    # Print summary
    print("O-RAN Project Benchmark Results:")
    print(f"Total tests executed: {report['summary']['total_tests']}")
    print(f"Average success rate: {report['summary']['avg_success_rate']:.2f}%")
    
    print("\nBest Performing Projects:")
    for test_type, best in report['summary']['best_performing'].items():
        print(f"\n{test_type}:")
        for metric, project in best.items():
            print(f"  {metric}: {project}")

if __name__ == "__main__":
    main()
```

## Getting Started with O-RAN Projects

### Quick Start Guides

#### 1. OSC RIC Quick Start
```bash
#!/bin/bash
# Quick start script for OSC RIC

# Prerequisites check
check_prerequisites() {
    echo "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker not found"
        exit 1
    fi
    
    # Check Kubernetes
    if ! command -v kubectl &> /dev/null; then
        echo "Error: kubectl not found"
        exit 1
    fi
    
    echo "All prerequisites satisfied"
}

# Clone and setup
setup_osc_ric() {
    echo "Setting up OSC RIC..."
    
    # Clone repository
    git clone "https://gerrit.oran-osc.org/r/ric-plt" ~/osc-ric
    cd ~/osc-ric
    
    # Install dependencies
    make install-deps
    
    # Build components
    make build-all
    
    echo "OSC RIC setup complete"
}

# Deploy to Kubernetes
deploy_ric() {
    echo "Deploying RIC to Kubernetes..."
    
    # Create namespace
    kubectl create namespace oran-ric
    
    # Deploy using Helm
    helm install near-rt-ric ./charts/near-rt-ric \
        --namespace oran-ric \
        --set replicaCount=1
    
    # Wait for deployment
    kubectl wait --for=condition=ready pod -l app=near-rt-ric \
        --namespace oran-ric --timeout=300s
    
    echo "RIC deployment complete"
}

# Verify installation
verify_installation() {
    echo "Verifying installation..."
    
    # Check pod status
    kubectl get pods -n oran-ric
    
    # Check services
    kubectl get services -n oran-ric
    
    # Test E2 interface
    kubectl port-forward svc/near-rt-ric 36421:36421 -n oran-ric &
    sleep 5
    
    # Simple connectivity test
    nc -z localhost 36421 && echo "E2 interface accessible" || echo "E2 interface not accessible"
    
    # Cleanup port-forward
    pkill -f "port-forward.*36421"
}

# Main execution
main() {
    check_prerequisites
    setup_osc_ric
    deploy_ric
    verify_installation
    
    echo "OSC RIC is ready for development!"
    echo "Access dashboard at: http://localhost:8080"
}

main "$@"
```

#### 2. OAI RAN Quick Start
```bash
#!/bin/bash
# Quick start script for OAI RAN

# Environment setup
setup_oai_environment() {
    echo "Setting up OAI RAN environment..."
    
    # Clone repository
    git clone https://gitlab.eurecom.fr/oai/openairinterface5g.git ~/oai-ran
    cd ~/oai-ran
    
    # Source environment
    source oaienv
    
    # Install dependencies
    cd cmake_targets
    ./build_oai -I --install-optional-packages
    
    echo "OAI environment setup complete"
}

# Build OAI components
build_oai_components() {
    echo "Building OAI components..."
    
    # Build OAI RU (eNB)
    ./build_oai -w USRP -c -C
    
    # Build OAI DU
    ./build_oai -w OAI_DU --ninja
    
    # Build OAI CU
    ./build_oai -w OAI_CU --ninja
    
    echo "OAI components built successfully"
}

# Configuration examples
create_sample_configs() {
    echo "Creating sample configurations..."
    
    # Create RU configuration
    cat > ~/oai-configs/ru.conf << EOF
Active_eNBs = ( "OAI-RU" );
# OAI RU Configuration
RUs = (
{
    local_sdr_addrs = "serial=XYZ123";
    sdr_addrs = "type=usrp";
    max_pdschReferenceSignalPower = -27;
    max_rxgain = 115;
    nb_antennas_tx = 1;
    nb_antennas_rx = 1;
}
);
EOF

    # Create DU configuration
    cat > ~/oai-configs/du.conf << EOF
Active_gNBs = ( "OAI-DU" );
# OAI DU Configuration
gNBs = (
{
    gNB_ID = 0xe00;
    cell_type = "CELL_MACRO_GNB";
    tracking_area_code = 1;
    plmn_list = ( { mcc = 208; mnc = 99; mnc_length = 2; } );
    nr_cellid = 0;
}
);
EOF

    echo "Sample configurations created"
}

# Testing and validation
run_basic_tests() {
    echo "Running basic tests..."
    
    # Unit tests
    cd ~/oai-ran
    make unit_tests
    
    # Integration tests
    ./ci-scripts/basicSimulatorCheck.sh
    
    echo "Basic tests completed"
}

# Main setup function
main() {
    setup_oai_environment
    build_oai_components
    create_sample_configs
    run_basic_tests
    
    echo "OAI RAN setup complete!"
    echo "Configuration files located in: ~/oai-configs/"
}

main "$@"
```

## Contribution Guidelines

### Code Contribution Process

```mermaid
graph TD
    A[Fork Repository] --> B[Create Feature Branch]
    B --> C[Implement Changes]
    C --> D[Write Unit Tests]
    D --> E[Run Local Tests]
    E --> F[Code Review Preparation]
    F --> G[Submit Pull Request]
    G --> H[Automated CI Checks]
    H --> I{CI Results}
    I -->|Fail| J[Fix Issues]
    J --> E
    I -->|Pass| K[Manual Code Review]
    K --> L{Review Outcome}
    L -->|Changes Requested| M[Address Feedback]
    M --> G
    L -->|Approved| N[Merge to Main]
    N --> O[Post-Merge Actions]
    O --> P[Update Documentation]
    P --> Q[Release Notes]
```

### Documentation Standards

```markdown
## Documentation Template

### Project Overview
Brief description of the project and its purpose in the O-RAN ecosystem.

### Architecture
- High-level architecture diagram
- Component interactions
- Data flow descriptions

### Installation
Step-by-step installation instructions:
```bash
# Prerequisites
sudo apt-get install package1 package2

# Clone repository
git clone repository-url

# Build process
make build
```

### Configuration
Configuration examples and explanations:
```yaml
# Sample configuration
parameter1: value1
parameter2: value2
nested_param:
  sub_param1: sub_value1
```

### Usage Examples
Practical usage examples:
```python
# Import and basic usage
from project import Component

component = Component()
result = component.process(data)
```

### API Reference
Detailed API documentation:
- Class descriptions
- Method signatures
- Parameter details
- Return values
- Exception handling

### Testing
Testing guidelines and examples:
```python
# Unit test example
def test_feature():
    # Test implementation
    assert result == expected
```

### Troubleshooting
Common issues and solutions:
- Error messages and causes
- Debugging techniques
- Performance optimization tips

### Contributing
Guidelines for contributions:
- Code style requirements
- Testing requirements
- Documentation standards
- Pull request process
```

This comprehensive catalog provides developers with the information needed to understand, evaluate, and contribute to major O-RAN open source projects.