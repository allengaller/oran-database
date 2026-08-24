# O-RAN Interface Standards System

## Overview

O-RAN defines a comprehensive set of open interfaces that enable interoperability between disaggregated RAN components. This directory documents each major interface, its protocol stack, functional scope, and deployment considerations.

## Documents

- [F1 Interface](./f1-interface.md) - F1 interface between O-CU and O-DU (3GPP TS 38.473)
- [O-FH Interface](./o-fh-interface.md) - Open Fronthaul interface between O-DU and O-RU (O-RAN WG4)
- [E2 Interface](./e2-interface.md) - E2 interface between Near-RT RIC and E2 Node (O-RAN WG3)
- [A1 Interface](./a1-interface.md) - A1 interface between Non-RT RIC and Near-RT RIC (O-RAN WG2)
- [O1 Interface](./o1-interface.md) - O1 management interface (O-RAN WG10)
- [O2 Interface](./o2-interface.md) - O2 interface for O-Cloud management (O-RAN WG6)
- [OAM Interface](./oam-interface.md) - Operations, Administration, and Maintenance interfaces

## Interface Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SMO / Non-RT RIC                         │
│                         │  A1                                │
│                         ▼                                   │
│              ┌──────────────────┐                          │
│              │   Near-RT RIC    │                          │
│              │   (xApps)        │                          │
│              └────────┬─────────┘                          │
│                       │ E2                                  │
│         ┌─────────────┼─────────────┐                      │
│         │             │             │                      │
│    ┌────▼───┐    ┌────▼───┐    ┌───▼────┐                 │
│    │ O-CU-CP│    │ O-CU-UP│    │  O-DU  │                 │
│    └────┬───┘    └────────┘    └───┬────┘                 │
│         │ F1                       │ O-FH                  │
│         └──────────►──────────────┘                        │
│                                  ┌───▼────┐                │
│                                  │  O-RU  │                │
│                                  └────────┘                │
│  O1 (SMO ↔ all managed entities)                          │
│  O2 (SMO ↔ O-Cloud infrastructure)                        │
└─────────────────────────────────────────────────────────────┘
```

## Interface Summary

| Interface | Between | Protocol | Key Standard |
|-----------|---------|----------|--------------|
| F1 | O-CU ↔ O-DU | SCTP | 3GPP TS 38.473 |
| O-FH | O-DU ↔ O-RU | eCPRI/IEEE 1914.3 | O-RAN WG4 |
| E2 | Near-RT RIC ↔ E2 Node | SCTP (E2AP) | O-RAN WG3 |
| A1 | Non-RT RIC ↔ Near-RT RIC | REST/HTTP (JSON) | O-RAN WG2 |
| O1 | SMO ↔ Managed Entities | NETCONF/YANG | O-RAN WG10 |
| O2 | SMO ↔ O-Cloud | REST/HTTP (TOSCA) | O-RAN WG6 |

## Relationship to Other Sections

- Working groups responsible: [06-working-groups](../06-working-groups/)
- Standards compliance: [09-standards-compliance](../09-standards-compliance/)
- Functional split options: [04-disaggregation-options](../04-disaggregation-options/)
- Cloud integration: [05-cloud-integration](../05-cloud-integration/)
