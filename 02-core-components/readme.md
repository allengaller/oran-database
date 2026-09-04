---
title: "O-RAN Core Components"
description: "This section documents the core functional components of the O-RAN architecture, including O-CU, O-DU, O-RU, RIC, and SMO, with their roles, functions, and deployment considerations."
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-09-03"
keywords: ['O-RAN', 'O-CU', 'O-DU', 'O-RU', 'RIC', 'SMO']
---

# O-RAN Core Components

## Overview

O-RAN disaggregates the traditional base station into open, interoperable components. This directory documents each core component of the O-RAN architecture — its functional scope, internal structure, interfaces, and deployment considerations.

## Documents

- [O-RU (Open Radio Unit)](./o-ru.md) - Radio unit handling RF and lower physical layer processing
- [O-DU (Open Distributed Unit)](./o-du.md) - Distributed unit handling RLC, MAC, and higher physical layer
- [O-CU (Open Centralized Unit)](./o-cu.md) - Centralized unit handling RRC, SDAP, and PDCP
- [O-CU-CP / O-CU-UP](./o-cucp-cuup.md) - Control plane and user plane separation of the O-CU
- [O-RIC (RAN Intelligent Controller)](./o-ric.md) - Near-RT and Non-RT RIC for intelligent network control
- [SMO (Service Management and Orchestration)](./smo.md) - End-to-end management, orchestration, and Non-RT RIC hosting

## Component Architecture Overview

```
┌─────────────────────────────────────────────┐
│        SMO (incl. Non-RT RIC / rApps)       │
└───────────────────┬─────────────────────────┘
                    │
            ┌───────▼────────┐
            │  Near-RT RIC   │
            │    (xApps)     │
            └───────┬────────┘
                    │
        ┌───────────┼────────────┐
        │           │            │
   ┌────▼────┐ ┌────▼────┐  ┌───▼───┐
   │ O-CU-CP │ │ O-CU-UP │  │ O-DU  │
   └─────────┘ └─────────┘  └───┬───┘
                                │
                            ┌───▼───┐
                            │ O-RU  │
                            └───────┘
```

## Component Summary

| Component | Layer Functions | Key Interfaces | Typical Deployment |
|-----------|-----------------|----------------|--------------------|
| O-RU | RF, Low-PHY | O-FH | Cell site |
| O-DU | RLC, MAC, High-PHY | O-FH, F1, E2 | Edge / regional cloud |
| O-CU-CP | RRC, PDCP-C | F1-C, E1, E2, NG-C | Regional / central cloud |
| O-CU-UP | SDAP, PDCP-U | F1-U, E1, NG-U | Regional / central cloud |
| Near-RT RIC | 10ms–1s control loops | E2, A1, O1 | Edge cloud |
| SMO / Non-RT RIC | >1s orchestration & policies | A1, O1, O2 | Central cloud |

## Relationship to Other Sections

- Overall architecture: [01-architecture-system](../01-architecture-system/)
- Interface specifications: [03-interface-standards](../03-interface-standards/)
- Functional split options: [04-disaggregation-options](../04-disaggregation-options/)
- RIC development: [07-ric-development](../07-ric-development/)
