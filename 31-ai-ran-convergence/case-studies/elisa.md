---
title: "Case Study: Elisa (Finland) — AI-RAN Field Trials"
description: "> **Status**: Active field trials since 2025 | **Location**: Helsinki, Finland"
category: "documentation"
language: "en-US"
version: "1.0"
last_updated: "2026-08-25"
keywords: ['AI-RAN', 'RIC', '5G']
---

# Case Study: Elisa (Finland) — AI-RAN Field Trials

> **Status**: Active field trials since 2025 | **Location**: Helsinki, Finland

## Executive Summary

**Elisa**, the leading Finnish telecom operator, has been a pioneer in **AI-driven RAN automation** since 2022. In 2025-2026, Elisa launched **AI-RAN field trials** in Helsinki, combining **NVIDIA Aerial SDK** with their existing **AI-native operations platform** to deliver the first **commercial-grade autonomous RAN** in the Nordics.

Elisa's approach is distinctive because:

1. **AI-first culture** — Elisa has used ML for RAN optimization since 2018
2. **Strong R&D partnerships** — Close ties with Aalto University, Nokia, NVIDIA
3. **Regulatory alignment** — Finland's favorable stance on AI experimentation
4. **Small market, fast iteration** — Enables rapid deployment cycles

---

## Elisa's AI-RAN Journey

### Timeline

| Year | Milestone |
|:---|:---|
| **2018** | First ML-based SON (Self-Organizing Network) deployment |
| **2020** | AI-driven energy saving (30% power reduction) |
| **2022** | O-RAN Near-RT RIC pilot (O-RAN SC) |
| **2023** | xApp marketplace launched internally |
| **2024** | LLM-based RCA (Root Cause Analysis) for NOC |
| **2025** | AI-RAN field trials begin (Helsinki) |
| **2026** | Commercial AI-RAN services (pilot customers) |

---

## Architecture: The Elisa AI-RAN Stack

### High-Level View

```
┌───────────────────────────────────────────────────────────┐
│  Elisa AI-RAN Platform                                      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Tier 1: Strategic AI (Non-RT RIC)                  │ │
│  │  • Telecom-tuned LLM (Qwen2.5-7B-Telecom)           │ │
│  │  • Natural language operator interface              │ │
│  │  • Long-term optimization planning                  │ │
│  └─────────────────────────────────────────────────────┘ │
│                          ↕ A1                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Tier 2: Tactical AI (Near-RT RIC)                  │ │
│  │  • DRL-based xApps (energy, mobility, capacity)     │ │
│  │  • Real-time control (10ms-1s)                       │ │
│  │  • Policy interpretation                             │ │
│  └─────────────────────────────────────────────────────┘ │
│                          ↕ E2                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Tier 3: Reactive AI (O-DU, NVIDIA ARC)             │ │
│  │  • cuMAC scheduler with ML assist                    │ │
│  │  • Subframe-level fast loop                          │ │
│  │  • Safety guardrail enforcement                      │ │
│  └─────────────────────────────────────────────────────┘ │
│                          ↕                                  │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Digital Twin (NVIDIA AODT + Elisa's custom twin)    │ │
│  │  • Helsinki urban RF model                           │ │
│  │  • Real-time sync with production                    │ │
│  │  • Pre-validation of all AI actions                  │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

---

## Key Innovations

### 1. Natural Language NOC (Network Operations Center)

Elisa built an **LLM-powered NOC assistant** that operators can query in natural language:

```
Operator: "Why did cell HEL-007 drop 15% throughput yesterday?"

LLM Agent: 
  "Cell HEL-007 experienced a throughput drop due to 3 factors:
   1. Neighbor cell HEL-008 had increased interference (construction site)
   2. Weather attenuation from heavy rain (measured: 12 mm/hr)
   3. UE density increased 40% (street festival)
   
   Recommended action: Increase HEL-007 power by 2 dB and tilt down 1°.
   Expected improvement: +12% throughput.
   
   Pre-validate in twin? [Y/N]"
```

**Technical stack**:
- **LLM**: Qwen2.5-7B-Telecom (fine-tuned on Elisa's internal data)
- **Tools**: TimesFM (traffic prediction), RCA engine (root cause), AODT (simulation)
- **Safety**: All actions pre-validated in twin before execution

### 2. Energy-Saving xApp (Flagship Use Case)

Elisa's most successful xApp is **AI-driven energy saving**:

```python
# energy_saver_xapp.py — Elisa's production xApp
class EnergySaverXApp:
    """Reduces cell site power consumption while maintaining SLA."""
    
    def __init__(self, e2_client, kpi_monitor, digital_twin):
        self.e2 = e2_client
        self.kpis = kpi_monitor
        self.twin = digital_twin
        self.drl_policy = load_policy('energy_saver_v2026.1')
    
    def optimize(self, cell_id: str):
        # Step 1: Get current state
        state = self.kpis.get_cell_state(cell_id)
        
        # Step 2: DRL policy suggests action
        action = self.drl_policy.predict(state)
        # Action space: {power_delta_db, sleep_mode, carrier_shutdown}
        
        # Step 3: Pre-validate in digital twin
        prediction = self.twin.simulate_action(cell_id, action, duration_min=30)
        
        # Step 4: Safety check — will SLA be maintained?
        if prediction.drop_rate > 0.01:  # Elisa SLA: <1% drop rate
            self._log_rejected(cell_id, action, reason="sla_violation_predicted")
            return
        
        # Step 5: Execute via E2
        self.e2.send_control(cell_id, action)
        self._log_executed(cell_id, action, prediction)
    
    def _log_rejected(self, cell_id, action, reason):
        metrics.xapp_rejections.labels(self.name, reason).inc()
    
    def _log_executed(self, cell_id, action, prediction):
        metrics.xapp_executions.labels(self.name).inc()
        audit_log.write({
            'timestamp': datetime.utcnow(),
            'xapp': 'energy-saver',
            'cell_id': cell_id,
            'action': action.dict(),
            'prediction': prediction.dict()
        })
```

**Results** (2026):
- **30% energy reduction** during off-peak hours
- **Zero SLA violations** (all actions pre-validated)
- **Payback period**: 8 months (energy savings vs. GPU compute cost)

### 3. Predictive Maintenance with Digital Twin

Elisa uses AODT to **predict equipment failures** before they happen:

```python
# predictive_maintenance.py
class PredictiveMaintenanceAgent:
    def __init__(self, twin: AODTClient, telemetry: TelemetryClient):
        self.twin = twin
        self.telemetry = telemetry
        self.failure_model = load_model('failure_predictor_v2026.1')
    
    def analyze_cell(self, cell_id: str) -> HealthReport:
        # Get 30 days of telemetry
        history = self.telemetry.get_history(cell_id, days=30)
        
        # Compare live behavior to twin prediction
        twin_prediction = self.twin.predict_current_behavior(cell_id)
        live_state = self.telemetry.get_current(cell_id)
        
        # Compute divergence
        divergence = compute_divergence(twin_prediction, live_state)
        
        # Failure model predicts time-to-failure
        ttf_hours = self.failure_model.predict(history, divergence)
        
        return HealthReport(
            cell_id=cell_id,
            health_score=min(1.0, ttf_hours / 720),  # 30 days = 1.0
            predicted_failure_hours=ttf_hours,
            recommendation=self._recommend(ttf_hours)
        )
    
    def _recommend(self, ttf_hours: float) -> str:
        if ttf_hours < 24:
            return "IMMEDIATE: Schedule field visit within 24h"
        elif ttf_hours < 168:  # 1 week
            return "URGENT: Schedule field visit this week"
        elif ttf_hours < 720:  # 30 days
            return "PLANNED: Include in next monthly maintenance"
        else:
            return "HEALTHY: No action required"
```

**Impact**:
- **40% reduction** in truck rolls (unnecessary site visits)
- **25% reduction** in unplanned outages
- **ROI**: €3.2M saved annually (across 3000 cell sites)

---

## Helsinki Urban RF Model

### Why Helsinki Matters

Helsinki is an ideal testbed for AI-RAN:

- **Dense urban** — Many cells in close proximity (interference-rich)
- **Harsh weather** — -30°C to +30°C range, snow, rain
- **Tech-savvy population** — High 5G adoption, 5G-only devices
- **Regulatory sandbox** — Finnish Transport and Communications Agency (Traficom) allows experimentation

### Custom Twin Model

Elisa built a **high-fidelity Helsinki-specific digital twin**:

- **3D building models** from city GIS data
- **Vegetation models** (trees attenuate differently summer vs. winter)
- **Weather integration** (Finnish Meteorological Institute API)
- **Traffic patterns** from city cameras (anonymized)

```python
# helsinki_twin.py
class HelsinkiDigitalTwin:
    def __init__(self):
        self.gis = load_gis('helsinki_buildings_2026.geojson')
        self.vegetation = load_seasonal_vegetation('helsinki_parks')
        self.weather = WeatherAPI(api_key=os.environ['FMI_API_KEY'])
        self.traffic = TrafficAPI(endpoint='https://digitransit.fi/api')
    
    def compute_path_loss(self, tx_pos, rx_pos, frequency_hz):
        # Physics-based ray tracing
        base_loss = ray_tracing_path_loss(
            self.gis, tx_pos, rx_pos, frequency_hz
        )
        
        # Vegetation attenuation (seasonal)
        veg_loss = self.vegetation.compute_attenuation(tx_pos, rx_pos)
        
        # Weather attenuation (rain, snow)
        current_weather = self.weather.get_current()
        weather_loss = self._weather_attenuation(current_weather, frequency_hz)
        
        return base_loss + veg_loss + weather_loss
```

---

## Business Model

### Revenue Streams from AI-RAN

1. **Internal cost reduction** — Energy savings, reduced truck rolls
2. **B2B edge AI services** — Selling compute to Helsinki enterprises
3. **Data monetization** — Aggregated, anonymized network insights
4. **Consulting** — Selling AI-RAN expertise to other Nordic operators

### B2B Edge AI Pilot Customers (2026)

| Customer | Industry | Use Case |
|:---|:---|:---|
| **Helsinki City Transport** | Public transit | Real-time bus arrival prediction |
| **Kone (elevators)** | Industrial IoT | Predictive maintenance of building elevators |
| **Stockmann (retail)** | Retail | Foot traffic analytics in city center |
| **Nokia Bell Labs** | Research | 6G research data collection |

---

## Challenges and Learnings

### Technical

1. **Weather affects AI accuracy** — DRL policies trained on summer data fail in winter
   - **Solution**: Seasonal retraining (4 models per year)
2. **Twin freshness** — Helsinki construction sites change RF environment weekly
   - **Solution**: Weekly GIS updates from city data
3. **GPU power budget** — L4 GPU + heating in -30°C requires careful thermal design
   - **Solution**: Waste heat from GPU used to heat cabinet (innovative!)

### Operational

1. **Union concerns** — Operators worried AI would replace NOC engineers
   - **Solution**: Upskilling program, AI as "co-pilot" not replacement
2. **Regulatory uncertainty** — GDPR interpretation for AI decision logs
   - **Solution**: Early engagement with Finnish Data Protection Ombudsman
3. **Vendor lock-in risk** — Too much dependence on NVIDIA
   - **Solution**: Multi-vendor strategy, evaluating Intel + AMD alternatives

---

## Metrics and Results (2026)

| Metric | Before AI-RAN | After AI-RAN | Improvement |
|:---|:---|:---|:---|
| **Energy consumption** | 100% baseline | 70% | -30% |
| **Network availability** | 99.95% | 99.99% | +0.04% |
| **NOC tickets** | 1000/month | 400/month | -60% |
| **Mean time to repair** | 4 hours | 1.5 hours | -62% |
| **Truck rolls** | 200/month | 120/month | -40% |
| **Customer NPS** | 62 | 71 | +9 points |

---

## K8S Engineer Takeaways

If you're building an AI-RAN platform like Elisa:

1. **Start with a single xApp** — Energy saving is the lowest-risk, highest-ROI
2. **Build digital twin early** — Essential for safety and validation
3. **LLM for NOC** — Natural language interface dramatically improves operator efficiency
4. **Seasonal retraining** — If your environment changes (weather, construction), retrain models
5. **Audit everything** — GDPR compliance requires explainable AI decisions
6. **Multi-vendor** — Don't lock into a single hardware/software vendor

---

## References

- [Elisa AI-RAN Case Study (2026)](https://elisa.fi/en/ai-ran)
- [Aalto University 6G Research](https://www.aalto.fi/en/6g)
- [NVIDIA Aerial SDK](https://developer.nvidia.com/aerial)
- [Finnish Transport and Communications Agency (Traficom)](https://www.traficom.fi/)
- [O-RAN Alliance](https://www.o-ran.org/)
