# O-RAN Fundamentals

## Overview
This section covers the fundamental concepts and basic knowledge of O-RAN technology, including its definition, vision, historical evolution, core values, key concepts, and overall architecture. As a cloud platform operations professional, this knowledge will form the foundation of your O-RAN expertise.

## Key Topics

### 1. Architecture Overview
- **Overall Architecture**: Standard architecture diagram defined by O-RAN Alliance, component relationships
- **Functional Modules**: Functional definitions and responsibilities of each network element
- **Network Element Relationships**: Communication and interaction mechanisms between components
- **Standardization Goals**: Interface standardization, functional standardization, deployment standardization

### 2. Core Components
- **Radio Unit (RU)**: Radio frequency processing functions, connected to antennas
- **Distributed Unit (DU)**: Physical layer and part of MAC layer functions
- **Centralized Unit (CU)**: RRC, PDCP and other high-level protocol functions
- **RAN Intelligent Controller (RIC)**: Near-RT RIC and Non-RT RIC functions
- **Service Management and Orchestration (SMO)**: Network service management and orchestration functions

### 3. Interface Standards
- **F1 Interface**: CU-DU interface defined by 3GPP
- **Open Fronthaul Interface (O-FH)**: Standardized fronthaul interface defined by O-RAN Alliance
- **E2 Interface**: Interface between RIC and CU/DU
- **A1 Interface**: Interface between Non-RT RIC and Near-RT RIC
- **O1 Interface**: Management interface between SMO and other network elements

### 4. Disaggregation Options
- **Option 1-8**: Detailed explanation of 8 disaggregation options
- **Functional Boundaries**: Specific functional boundaries of CU, DU, RU at each split point
- **Latency Requirements**: Performance requirements for different disaggregation options
- **Deployment Considerations**: Deployment considerations in terms of technology, cost, operations

## Learning Objectives

1. **Understand the O-RAN reference architecture** and how it differs from traditional RAN
2. **Identify key network elements** and their functional responsibilities
3. **Grasp the interface standards** and their significance in multi-vendor environments
4. **Evaluate disaggregation options** and their implications for network design

## Prerequisites
- Basic understanding of cloud computing concepts
- Familiarity with network virtualization technologies
- Knowledge of 5G network architecture fundamentals

## References
- [O-RAN Alliance Website](https://www.o-ran.org/)
- [CSDN Blog - O-RAN Introduction](https://blog.csdn.net/qq_36666115/article/details/143654450)
- [Electronic Enthusiast Network - O-RAN Reference Architecture and How to Disaggregate RAN](https://www.elecfans.com/d/1237946.html)
