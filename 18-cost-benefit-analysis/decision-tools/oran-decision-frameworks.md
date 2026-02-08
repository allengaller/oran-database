# O-RAN Cost-Benefit Analysis Decision Tools

## Overview
This document provides comprehensive decision-making frameworks, analytical tools, and evaluation methodologies for assessing O-RAN deployment costs, benefits, and return on investment across different scenarios and deployment models.

## Decision Framework Architecture

### 1. Multi-Criteria Decision Analysis (MCDA) Framework

```yaml
mcda_framework:
  criteria_hierarchy:
    financial_criteria:
      - capital_expenditure: "Initial investment costs"
      - operational_expenditure: "Ongoing operational costs"
      - total_cost_of_ownership: "TCO over deployment lifecycle"
      - return_on_investment: "ROI calculations and projections"
    
    technical_criteria:
      - performance_benchmarks: "Throughput, latency, reliability metrics"
      - scalability_potential: "Ability to scale network capacity"
      - interoperability_score: "Multi-vendor integration capability"
      - future_proofing: "Technology evolution adaptability"
    
    strategic_criteria:
      - time_to_market: "Deployment speed and agility"
      - competitive_advantage: "Market differentiation potential"
      - risk_mitigation: "Operational and financial risk reduction"
      - innovation_enablement: "New service and capability creation"
  
  weighting_system:
    stakeholder_perspectives:
      - cto_viewpoint: 
          financial_weight: 0.3
          technical_weight: 0.5
          strategic_weight: 0.2
      
      - cfo_viewpoint:
          financial_weight: 0.6
          technical_weight: 0.2
          strategic_weight: 0.2
      
      - cio_viewpoint:
          financial_weight: 0.4
          technical_weight: 0.3
          strategic_weight: 0.3
  
  evaluation_methods:
    - analytic_hierarchy_process: "Pairwise comparison matrices"
    - technique_for_order_preference: "TOPSIS methodology"
    - weighted_sum_model: "Simple additive weighting"
    - outranking_methods: "ELECTRE family approaches"
```

### 2. Investment Decision Trees

```python
#!/usr/bin/env python3
"""
O-RAN Investment Decision Tree Analysis
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class DeploymentScenario(Enum):
    GREENFIELD = "Greenfield deployment"
    BROWNFIELD = "Brownfield upgrade"
    HYBRID = "Hybrid approach"

class TechnologyPath(Enum):
    TRADITIONAL_RAN = "Traditional RAN"
    ORAN_DEPLOYMENT = "O-RAN deployment"
    MIXED_ARCHITECTURE = "Mixed architecture"

@dataclass
class DecisionNode:
    name: str
    probability: float
    cost: float
    benefit: float
    children: List['DecisionNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

@dataclass
class ScenarioAnalysis:
    scenario_name: str
    initial_investment: float
    annual_operating_cost: float
    annual_benefits: float
    deployment_timeline: int  # months
    risk_adjustment: float  # 0-1 scale
    market_conditions: str

class ORANDecisionTree:
    def __init__(self):
        self.root = DecisionNode("Root Decision", 1.0, 0, 0)
        self.scenarios = {}
        
    def build_investment_tree(self, scenarios: List[ScenarioAnalysis]) -> DecisionNode:
        """Build comprehensive investment decision tree"""
        
        # Root node - Technology Choice
        technology_choice = DecisionNode("Technology Selection", 1.0, 0, 0)
        
        # Traditional RAN branch
        traditional_ran = self._build_traditional_branch(scenarios)
        technology_choice.children.append(traditional_ran)
        
        # O-RAN branch
        oran_branch = self._build_oran_branch(scenarios)
        technology_choice.children.append(oran_branch)
        
        # Mixed architecture branch
        mixed_branch = self._build_mixed_branch(scenarios)
        technology_choice.children.append(mixed_branch)
        
        return technology_choice
    
    def _build_traditional_branch(self, scenarios: List[ScenarioAnalysis]) -> DecisionNode:
        """Build traditional RAN deployment branch"""
        traditional_root = DecisionNode("Traditional RAN", 0.4, 0, 0)
        
        for scenario in scenarios:
            if scenario.scenario_name == "brownfield_upgrade":
                node = DecisionNode(
                    f"Traditional {scenario.scenario_name}",
                    0.7,
                    scenario.initial_investment * 1.2,  # Higher costs
                    scenario.annual_benefits * 0.8,     # Lower benefits
                    []
                )
                traditional_root.children.append(node)
        
        return traditional_root
    
    def _build_oran_branch(self, scenarios: List[ScenarioAnalysis]) -> DecisionNode:
        """Build O-RAN deployment branch"""
        oran_root = DecisionNode("O-RAN Deployment", 0.4, 0, 0)
        
        for scenario in scenarios:
            node = DecisionNode(
                f"O-RAN {scenario.scenario_name}",
                0.6,
                scenario.initial_investment,
                scenario.annual_benefits * 1.3,  # Higher benefits
                []
            )
            
            # Add risk mitigation sub-branches
            if scenario.risk_adjustment > 0.7:
                low_risk = DecisionNode("Low Risk Path", 0.8, 
                                      node.cost * 0.9, 
                                      node.benefit * 1.1, [])
                node.children.append(low_risk)
            
            oran_root.children.append(node)
        
        return oran_root
    
    def _build_mixed_branch(self, scenarios: List[ScenarioAnalysis]) -> DecisionNode:
        """Build mixed architecture branch"""
        mixed_root = DecisionNode("Mixed Architecture", 0.2, 0, 0)
        
        for scenario in scenarios:
            node = DecisionNode(
                f"Mixed {scenario.scenario_name}",
                0.5,
                scenario.initial_investment * 1.1,
                scenario.annual_benefits * 1.1,
                []
            )
            mixed_root.children.append(node)
        
        return mixed_root
    
    def calculate_expected_values(self, node: DecisionNode) -> Tuple[float, float]:
        """Calculate expected costs and benefits"""
        if not node.children:
            return node.cost, node.benefit
        
        total_expected_cost = node.cost
        total_expected_benefit = node.benefit
        
        for child in node.children:
            child_cost, child_benefit = self.calculate_expected_values(child)
            total_expected_cost += node.probability * child_cost
            total_expected_benefit += node.probability * child_benefit
            
        return total_expected_cost, total_expected_benefit
    
    def perform_sensitivity_analysis(self, base_scenario: ScenarioAnalysis,
                                   sensitivity_ranges: Dict[str, Tuple[float, float]]) -> Dict[str, Any]:
        """Perform sensitivity analysis on key parameters"""
        results = {
            'parameter_analysis': {},
            'break_even_points': {},
            'risk_assessment': {}
        }
        
        parameters = ['initial_investment', 'annual_benefits', 'operating_cost']
        
        for param in parameters:
            min_val, max_val = sensitivity_ranges[param]
            param_results = []
            
            for value in np.linspace(min_val, max_val, 10):
                # Modify scenario parameter
                modified_scenario = ScenarioAnalysis(**vars(base_scenario))
                setattr(modified_scenario, param, value)
                
                # Recalculate ROI
                roi = self._calculate_roi(modified_scenario)
                param_results.append({
                    'value': value,
                    'roi': roi,
                    'payback_period': self._calculate_payback(modified_scenario)
                })
            
            results['parameter_analysis'][param] = param_results
            
            # Find break-even point
            break_even = self._find_break_even(param_results)
            results['break_even_points'][param] = break_even
            
        return results
    
    def _calculate_roi(self, scenario: ScenarioAnalysis) -> float:
        """Calculate ROI for given scenario"""
        total_benefits = scenario.annual_benefits * 5  # 5-year projection
        total_costs = scenario.initial_investment + (scenario.annual_operating_cost * 5)
        roi = ((total_benefits - total_costs) / total_costs) * 100
        return roi
    
    def _calculate_payback(self, scenario: ScenarioAnalysis) -> float:
        """Calculate payback period"""
        annual_net_benefit = scenario.annual_benefits - scenario.annual_operating_cost
        if annual_net_benefit > 0:
            return scenario.initial_investment / annual_net_benefit
        return float('inf')  # No payback if negative net benefit
    
    def _find_break_even(self, results: List[Dict]) -> float:
        """Find break-even point in sensitivity analysis"""
        for i in range(len(results) - 1):
            if results[i]['roi'] < 0 and results[i + 1]['roi'] >= 0:
                return results[i]['value']
        return None

# Usage example
def main():
    # Define scenarios
    scenarios = [
        ScenarioAnalysis(
            scenario_name="greenfield_deployment",
            initial_investment=2000000,
            annual_operating_cost=300000,
            annual_benefits=800000,
            deployment_timeline=18,
            risk_adjustment=0.8,
            market_conditions="favorable"
        ),
        ScenarioAnalysis(
            scenario_name="brownfield_upgrade",
            initial_investment=1500000,
            annual_operating_cost=250000,
            annual_benefits=600000,
            deployment_timeline=12,
            risk_adjustment=0.6,
            market_conditions="moderate"
        )
    ]
    
    # Create decision tree
    decision_tree = ORANDecisionTree()
    tree_root = decision_tree.build_investment_tree(scenarios)
    
    # Calculate expected values
    expected_cost, expected_benefit = decision_tree.calculate_expected_values(tree_root)
    print(f"Expected Cost: ${expected_cost:,.2f}")
    print(f"Expected Benefit: ${expected_benefit:,.2f}")
    
    # Sensitivity analysis
    sensitivity_ranges = {
        'initial_investment': (1000000, 3000000),
        'annual_benefits': (500000, 1000000),
        'operating_cost': (200000, 400000)
    }
    
    sensitivity_results = decision_tree.perform_sensitivity_analysis(
        scenarios[0], sensitivity_ranges
    )
    
    print("\nSensitivity Analysis Results:")
    for param, results in sensitivity_results['parameter_analysis'].items():
        print(f"{param}: Break-even at {sensitivity_results['break_even_points'][param]}")

if __name__ == "__main__":
    main()
```

## Financial Modeling Tools

### 1. Total Cost of Ownership (TCO) Calculator

```excel
# TCO Calculation Framework
# This would typically be implemented in Excel/Google Sheets

TCO_COMPONENTS:
  capital_expenditure:
    - hardware_costs: "=SUM(B2:B10)"  # Server, storage, networking
    - software_licensing: "=SUM(C2:C10)"  # Operating systems, databases
    - integration_costs: "=SUM(D2:D10)"  # Professional services
    - training_expenses: "=SUM(E2:E10)"  # Staff training and certification
  
  operational_expenditure:
    - personnel_costs: "=F2*F3*12"  # FTE * Monthly salary * 12
    - facility_costs: "=SUM(G2:G5)"  # Power, cooling, space
    - maintenance_support: "=H2*H3"  # Annual support contracts
    - network_operations: "=SUM(I2:I4)"  # Monitoring, management tools
  
  opportunity_costs:
    - downtime_losses: "=J2*J3*J4"  # Hours * Revenue/hour * Probability
    - competitive_disadvantage: "=K2"  # Market share erosion estimates

TCO_FORMULA: "=SUM(CapEx_range) + SUM(OpEx_range)*5 + SUM(Opportunity_range)"
ROI_CALCULATION: "=(Benefits_range - TCO_FORMULA)/TCO_FORMULA*100"
PAYBACK_PERIOD: "=TCO_FORMULA/(Annual_Benefits - Annual_OpEx)"
```

### 2. Net Present Value (NPV) Analysis

```python
#!/usr/bin/env python3
"""
O-RAN NPV and Financial Analysis Tool
"""

import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class CashFlow:
    year: int
    cash_flow: float
    discount_rate: float = 0.1  # 10% default
    
    def present_value(self) -> float:
        """Calculate present value of cash flow"""
        return self.cash_flow / ((1 + self.discount_rate) ** self.year)

class FinancialAnalyzer:
    def __init__(self, discount_rate: float = 0.1):
        self.discount_rate = discount_rate
        self.cash_flows: List[CashFlow] = []
        
    def add_cash_flow(self, year: int, amount: float):
        """Add cash flow for specific year"""
        cash_flow = CashFlow(year, amount, self.discount_rate)
        self.cash_flows.append(cash_flow)
        
    def calculate_npv(self) -> float:
        """Calculate Net Present Value"""
        npv = sum(cf.present_value() for cf in self.cash_flows)
        return npv
    
    def calculate_irr(self) -> float:
        """Calculate Internal Rate of Return"""
        if not self.cash_flows:
            return 0
            
        # Extract cash flows by year
        years = sorted(list(set(cf.year for cf in self.cash_flows)))
        cash_flow_by_year = {year: 0 for year in years}
        
        for cf in self.cash_flows:
            cash_flow_by_year[cf.year] += cf.cash_flow
            
        # Convert to array format for IRR calculation
        cf_array = [cash_flow_by_year[year] for year in sorted(years)]
        
        # Handle case where all cash flows are negative
        if all(cf <= 0 for cf in cf_array):
            return -1  # Negative infinity equivalent
            
        try:
            irr = np.irr(cf_array)
            return irr if not np.isnan(irr) else 0
        except:
            return 0
    
    def calculate_payback_period(self) -> float:
        """Calculate payback period"""
        cumulative_cf = 0
        for cf in sorted(self.cash_flows, key=lambda x: x.year):
            cumulative_cf += cf.cash_flow
            if cumulative_cf >= 0:
                return cf.year + (abs(cumulative_cf - cf.cash_flow) / cf.cash_flow)
        return float('inf')  # Never pays back
    
    def monte_carlo_simulation(self, iterations: int = 1000) -> Dict[str, Any]:
        """Perform Monte Carlo simulation for risk analysis"""
        npv_results = []
        irr_results = []
        
        for _ in range(iterations):
            # Randomize key parameters within reasonable ranges
            randomized_flows = []
            for cf in self.cash_flows:
                # ±20% variation in cash flows
                randomized_amount = cf.cash_flow * np.random.normal(1, 0.2)
                randomized_flows.append(CashFlow(cf.year, randomized_amount, self.discount_rate))
            
            # Calculate metrics for this iteration
            temp_analyzer = FinancialAnalyzer(self.discount_rate)
            temp_analyzer.cash_flows = randomized_flows
            
            npv_results.append(temp_analyzer.calculate_npv())
            irr_results.append(temp_analyzer.calculate_irr())
        
        return {
            'npv_statistics': {
                'mean': np.mean(npv_results),
                'std_dev': np.std(npv_results),
                'percentile_5': np.percentile(npv_results, 5),
                'percentile_95': np.percentile(npv_results, 95)
            },
            'irr_statistics': {
                'mean': np.mean(irr_results),
                'std_dev': np.std(irr_results),
                'percentile_5': np.percentile(irr_results, 5),
                'percentile_95': np.percentile(irr_results, 95)
            },
            'probability_positive_npv': sum(1 for npv in npv_results if npv > 0) / len(npv_results)
        }

# Usage example for O-RAN deployment
def analyze_oran_deployment():
    analyzer = FinancialAnalyzer(discount_rate=0.12)
    
    # Initial investment (Year 0)
    analyzer.add_cash_flow(0, -2500000)  # Capital expenditure
    
    # Operating costs and benefits (Years 1-10)
    for year in range(1, 11):
        operating_cost = -400000 * (1.03 ** (year - 1))  # 3% annual inflation
        benefits = 900000 * (1.05 ** (year - 1))  # 5% annual growth
        net_cash_flow = benefits + operating_cost
        analyzer.add_cash_flow(year, net_cash_flow)
    
    # Calculate financial metrics
    npv = analyzer.calculate_npv()
    irr = analyzer.calculate_irr()
    payback = analyzer.calculate_payback_period()
    
    print("O-RAN Deployment Financial Analysis:")
    print(f"Net Present Value: ${npv:,.2f}")
    print(f"Internal Rate of Return: {irr:.2%}")
    print(f"Payback Period: {payback:.1f} years")
    
    # Risk analysis
    risk_analysis = analyzer.monte_carlo_simulation(iterations=1000)
    print(f"\nRisk Analysis (1000 iterations):")
    print(f"Probability of Positive NPV: {risk_analysis['probability_positive_npv']:.1%}")
    print(f"NPV 5th Percentile: ${risk_analysis['npv_statistics']['percentile_5']:,.2f}")
    print(f"NPV 95th Percentile: ${risk_analysis['npv_statistics']['percentile_95']:,.2f}")

if __name__ == "__main__":
    analyze_oran_deployment()
```

## Comparative Analysis Frameworks

### 1. Vendor Comparison Matrix

```yaml
vendor_comparison_framework:
  evaluation_dimensions:
    technical_capabilities:
      - interface_compliance: "O-RAN standards adherence"
      - performance_benchmarks: "Throughput, latency, connection density"
      - scalability_support: "Maximum supported sites and capacity"
      - integration_complexity: "Ease of multi-vendor integration"
    
    financial_aspects:
      - pricing_model: "Licensing, subscription, usage-based"
      - total_cost_estimate: "5-year TCO projection"
      - payment_terms: "Upfront vs分期付款 options"
      - support_costs: "Maintenance and support pricing"
    
    operational_factors:
      - deployment_timeline: "Time to production deployment"
      - skill_requirements: "Staff training and certification needs"
      - support_quality: "24/7 support availability and response times"
      - upgrade_path: "Future technology migration support"
  
  scoring_methodology:
    weighted_scoring:
      technical_score: "=SUMPRODUCT(Technical_ratings, Technical_weights)"
      financial_score: "=SUMPRODUCT(Financial_ratings, Financial_weights)"
      operational_score: "=SUMPRODUCT(Operational_ratings, Operational_weights)"
      overall_score: "=(Technical*0.4) + (Financial*0.3) + (Operational*0.3)"
```

### 2. Deployment Scenario Analysis

```python
#!/usr/bin/env python3
"""
O-RAN Deployment Scenario Comparison Tool
"""

from typing import Dict, List, Any
from dataclasses import dataclass
import pandas as pd

@dataclass
class DeploymentScenario:
    name: str
    description: str
    capex: float
    opex_annual: float
    timeline_months: int
    risk_level: str  # low, medium, high
    complexity: str  # simple, moderate, complex
    vendor_lock_in: str  # none, partial, high
    scalability: str  # limited, moderate, excellent

class ScenarioComparator:
    def __init__(self):
        self.scenarios: List[DeploymentScenario] = []
        self.weights = {
            'cost_efficiency': 0.3,
            'time_to_value': 0.2,
            'risk_mitigation': 0.2,
            'flexibility': 0.2,
            'future_readiness': 0.1
        }
        
    def add_scenario(self, scenario: DeploymentScenario):
        """Add deployment scenario for comparison"""
        self.scenarios.append(scenario)
        
    def evaluate_scenarios(self) -> pd.DataFrame:
        """Evaluate all scenarios using multi-criteria analysis"""
        evaluation_data = []
        
        for scenario in self.scenarios:
            scores = self._calculate_scenario_scores(scenario)
            evaluation_data.append({
                'Scenario': scenario.name,
                'Description': scenario.description,
                'CAPEX': scenario.capex,
                'OPEX_Annual': scenario.opex_annual,
                'Timeline': scenario.timeline_months,
                'Cost_Efficiency': scores['cost_efficiency'],
                'Time_Value': scores['time_to_value'],
                'Risk_Score': scores['risk_mitigation'],
                'Flexibility': scores['flexibility'],
                'Future_Readiness': scores['future_readiness'],
                'Overall_Score': scores['overall']
            })
        
        return pd.DataFrame(evaluation_data)
    
    def _calculate_scenario_scores(self, scenario: DeploymentScenario) -> Dict[str, float]:
        """Calculate weighted scores for each evaluation criterion"""
        
        # Cost efficiency (lower is better)
        cost_ratio = scenario.capex / scenario.opex_annual
        cost_efficiency = self._normalize_score(cost_ratio, reverse=True)
        
        # Time to value (faster is better)
        time_score = self._normalize_score(scenario.timeline_months, reverse=True)
        
        # Risk mitigation (lower risk is better)
        risk_mapping = {'low': 1.0, 'medium': 0.7, 'high': 0.4}
        risk_score = risk_mapping.get(scenario.risk_level, 0.5)
        
        # Flexibility (less vendor lock-in is better)
        lockin_mapping = {'none': 1.0, 'partial': 0.7, 'high': 0.4}
        flexibility_score = lockin_mapping.get(scenario.vendor_lock_in, 0.5)
        
        # Future readiness (better scalability is better)
        scalability_mapping = {'limited': 0.4, 'moderate': 0.7, 'excellent': 1.0}
        future_score = scalability_mapping.get(scenario.scalability, 0.5)
        
        # Calculate overall weighted score
        overall = (
            cost_efficiency * self.weights['cost_efficiency'] +
            time_score * self.weights['time_to_value'] +
            risk_score * self.weights['risk_mitigation'] +
            flexibility_score * self.weights['flexibility'] +
            future_score * self.weights['future_readiness']
        )
        
        return {
            'cost_efficiency': cost_efficiency,
            'time_to_value': time_score,
            'risk_mitigation': risk_score,
            'flexibility': flexibility_score,
            'future_readiness': future_score,
            'overall': overall
        }
    
    def _normalize_score(self, value: float, reverse: bool = False) -> float:
        """Normalize score to 0-1 range"""
        # This is a simplified normalization - in practice, you'd use actual ranges
        normalized = min(max(value / 100, 0), 1)
        return 1 - normalized if reverse else normalized
    
    def generate_recommendation(self) -> Dict[str, Any]:
        """Generate deployment recommendation based on analysis"""
        df = self.evaluate_scenarios()
        
        if df.empty:
            return {"recommendation": "No scenarios available for analysis"}
        
        # Find best overall score
        best_scenario = df.loc[df['Overall_Score'].idxmax()]
        
        # Analyze trade-offs
        trade_offs = self._analyze_trade_offs(df)
        
        return {
            "recommended_scenario": best_scenario['Scenario'],
            "reasoning": f"Based on multi-criteria analysis with emphasis on cost efficiency ({self.weights['cost_efficiency']*100}%) and time to value ({self.weights['time_to_value']*100}%)",
            "key_metrics": {
                "CAPEX": f"${best_scenario['CAPEX']:,.0f}",
                "Annual_OPEX": f"${best_scenario['OPEX_Annual']:,.0f}",
                "Deployment_Timeline": f"{best_scenario['Timeline']} months",
                "Overall_Score": f"{best_scenario['Overall_Score']:.2f}"
            },
            "trade_offs": trade_offs,
            "sensitivity_note": "Scores are weighted averages - adjust weights based on organizational priorities"
        }
    
    def _analyze_trade_offs(self, df: pd.DataFrame) -> List[str]:
        """Analyze key trade-offs between scenarios"""
        trade_offs = []
        
        # Cost vs Speed trade-off
        cost_leader = df.loc[df['CAPEX'].idxmin()]['Scenario']
        speed_leader = df.loc[df['Timeline'].idxmin()]['Scenario']
        if cost_leader != speed_leader:
            trade_offs.append(f"Cost leader ({cost_leader}) differs from speed leader ({speed_leader})")
        
        # Risk vs Flexibility trade-off
        low_risk_scenarios = df[df['Risk_Score'] > 0.8]['Scenario'].tolist()
        high_flexibility_scenarios = df[df['Flexibility'] > 0.8]['Scenario'].tolist()
        
        if low_risk_scenarios and high_flexibility_scenarios:
            common_scenarios = set(low_risk_scenarios) & set(high_flexibility_scenarios)
            if not common_scenarios:
                trade_offs.append("Low-risk scenarios differ from high-flexibility scenarios")
        
        return trade_offs[:3]  # Limit to top 3 trade-offs

# Usage example
def main():
    comparator = ScenarioComparator()
    
    # Add deployment scenarios
    scenarios = [
        DeploymentScenario(
            name="Phased Traditional",
            description="Gradual upgrade from existing RAN infrastructure",
            capex=1800000,
            opex_annual=320000,
            timeline_months=24,
            risk_level="low",
            complexity="moderate",
            vendor_lock_in="high",
            scalability="limited"
        ),
        DeploymentScenario(
            name="Greenfield O-RAN",
            description="Complete O-RAN deployment in new coverage areas",
            capex=2200000,
            opex_annual=280000,
            timeline_months=18,
            risk_level="medium",
            complexity="complex",
            vendor_lock_in="none",
            scalability="excellent"
        ),
        DeploymentScenario(
            name="Hybrid Approach",
            description="Mix of traditional and O-RAN in existing footprint",
            capex=2000000,
            opex_annual=300000,
            timeline_months=15,
            risk_level="medium",
            complexity="high",
            vendor_lock_in="partial",
            scalability="moderate"
        )
    ]
    
    for scenario in scenarios:
        comparator.add_scenario(scenario)
    
    # Evaluate scenarios
    results_df = comparator.evaluate_scenarios()
    print("Deployment Scenario Comparison:")
    print(results_df.to_string(index=False))
    
    # Generate recommendation
    recommendation = comparator.generate_recommendation()
    print(f"\nRecommendation: {recommendation['recommended_scenario']}")
    print(f"Reasoning: {recommendation['reasoning']}")
    print("Key Metrics:")
    for metric, value in recommendation['key_metrics'].items():
        print(f"  {metric}: {value}")

if __name__ == "__main__":
    main()
```

These decision tools provide comprehensive frameworks for evaluating O-RAN deployment options, comparing vendors, and making informed investment decisions based on quantitative analysis and multi-criteria evaluation.