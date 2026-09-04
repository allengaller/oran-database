---
title: "O-RAN Disaggregation Options"
description: "This section covers the disaggregation and functional split options of the O-RAN architecture, including fronthaul splits, performance impact, deployment scenarios, and cost-benefit analysis."
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-09-03"
keywords: ['O-RAN', 'Functional Split', 'Disaggregation', 'Fronthaul', '7.2x']
---

# O-RAN Disaggregation Options

## Overview

One of the defining features of O-RAN is the disaggregation of RAN functions across O-RU, O-DU, and O-CU. Choosing where to split the protocol stack involves trade-offs between fronthaul bandwidth, latency, hardware cost, and deployment flexibility. This directory documents the available split options and their practical implications.

## Documents

- [Functional Splits](./functional-splits.md) - Overview of 3GPP/O-RAN functional split options (Split 1–8)
- [Fronthaul Splits](./fronthaul-splits.md) - Deep dive into Split 7.2x and other fronthaul split variants
- [Performance Impact](./performance-impact.md) - Latency, bandwidth, and processing implications of each split
- [Deployment Scenarios](./deployment-scenarios.md) - Split selection for macro, small cell, rural, and enterprise deployments
- [Cost-Benefit Analysis](./cost-benefit-analysis.md) - TCO comparison of different disaggregation options

## Split Options Overview

| Split | Boundary | Fronthaul BW (100 MHz, 4T4R) | Latency Sensitivity | Pooling Gain |
|-------|----------|------------------------------|---------------------|--------------|
| Split 8 | PHY–RF | Very high (CPRI) | Extreme | None |
| Split 7.2x | Low-PHY–High-PHY | ~10–25 Gbps | High (<250 µs) | DU pooling |
| Split 6 | MAC–PHY | Moderate | Medium | Partial |
| Split 2 | PDCP–RLC | ~4 Gbps | Low | Full CU/DU pooling |

## Key Considerations

1. **Transport network capability** - available fronthaul bandwidth and latency budget
2. **Compute placement** - which functions benefit most from cloud pooling
3. **Vendor ecosystem** - O-RU support for the chosen split (7.2x is the O-RAN default)
4. **Spectrum and bandwidth** - wider channels increase fronthaul load exponentially

## Relationship to Other Sections

- Core components: [02-core-components](../02-core-components/)
- O-FH interface: [03-interface-standards](../03-interface-standards/o-fh-interface.md)
- Cloud integration: [05-cloud-integration](../05-cloud-integration/)
- Cost analysis: [18-cost-benefit-analysis](../18-cost-benefit-analysis/)
