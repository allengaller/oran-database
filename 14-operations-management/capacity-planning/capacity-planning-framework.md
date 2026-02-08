# O-RAN Capacity Planning Framework

## Overview
This document provides a comprehensive capacity planning framework for O-RAN systems, covering load forecasting, scalability design, cost optimization, and resource utilization planning.

## Load Forecasting Models

### Traffic Growth Prediction
```python
# O-RAN traffic forecasting and capacity planning
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class ORANCAPACITYPlanner:
    def __init__(self):
        self.scaler = StandardScaler()
        self.forecast_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.historical_data = None
        
    def load_historical_data(self, data_file):
        """Load historical traffic and performance data"""
        try:
            self.historical_data = pd.read_csv(data_file)
            self.historical_data['timestamp'] = pd.to_datetime(self.historical_data['timestamp'])
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def prepare_features(self, data):
        """Prepare features for machine learning model"""
        # Extract time-based features
        data['hour'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        data['month'] = data['timestamp'].dt.month
        data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
        
        # Lag features for time series
        for lag in [1, 24, 168]:  # 1 hour, 24 hours, 1 week
            data[f'throughput_lag_{lag}'] = data['throughput_mbps'].shift(lag)
            data[f'connected_users_lag_{lag}'] = data['connected_users'].shift(lag)
        
        # Rolling statistics
        for window in [24, 168]:  # 24 hours, 1 week
            data[f'throughput_rolling_mean_{window}'] = data['throughput_mbps'].rolling(window=window).mean()
            data[f'throughput_rolling_std_{window}'] = data['throughput_mbps'].rolling(window=window).std()
        
        return data.dropna()
    
    def train_forecast_model(self):
        """Train the capacity forecasting model"""
        if self.historical_data is None:
            raise ValueError("Historical data not loaded")
        
        # Prepare features
        processed_data = self.prepare_features(self.historical_data.copy())
        
        # Define features and target
        feature_columns = [col for col in processed_data.columns 
                          if col not in ['timestamp', 'throughput_mbps', 'connected_users']]
        X = processed_data[feature_columns]
        y = processed_data['throughput_mbps']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.forecast_model.fit(X_scaled, y)
        
        print(f"Model trained with {len(feature_columns)} features")
        print(f"Feature importance:")
        for feature, importance in zip(feature_columns, self.forecast_model.feature_importances_):
            print(f"  {feature}: {importance:.4f}")
    
    def forecast_capacity(self, forecast_horizon_days=90):
        """Forecast capacity requirements for specified horizon"""
        if self.historical_data is None:
            raise ValueError("Historical data not loaded")
        
        # Get latest data point
        latest_data = self.historical_data.iloc[-1:].copy()
        
        forecasts = []
        current_date = latest_data['timestamp'].iloc[0]
        
        for day in range(forecast_horizon_days):
            current_date += timedelta(days=1)
            
            # Create forecast row
            forecast_row = latest_data.copy()
            forecast_row['timestamp'] = current_date
            
            # Prepare features
            forecast_features = self.prepare_features(forecast_row)
            feature_columns = [col for col in forecast_features.columns 
                             if col not in ['timestamp', 'throughput_mbps', 'connected_users']]
            
            # Make prediction
            X_forecast = self.scaler.transform(forecast_features[feature_columns])
            predicted_throughput = self.forecast_model.predict(X_forecast)[0]
            
            # Store forecast
            forecasts.append({
                'date': current_date,
                'predicted_throughput_mbps': predicted_throughput,
                'predicted_connected_users': int(predicted_throughput * 0.8),  # Assumed ratio
                'capacity_utilization': min(predicted_throughput / 10000 * 100, 100)  # Assuming 10Gbps max
            })
            
            # Update for next iteration (simplified)
            latest_data['throughput_mbps'] = predicted_throughput
        
        return pd.DataFrame(forecasts)
    
    def generate_capacity_recommendations(self, forecast_df):
        """Generate capacity planning recommendations"""
        recommendations = {
            'immediate_actions': [],
            'short_term_planning': [],
            'long_term_strategy': []
        }
        
        # Identify capacity thresholds
        high_utilization_periods = forecast_df[forecast_df['capacity_utilization'] > 80]
        critical_periods = forecast_df[forecast_df['capacity_utilization'] > 95]
        
        if len(critical_periods) > 0:
            recommendations['immediate_actions'].append(
                f"Increase capacity by {len(critical_periods)} periods exceeding 95% utilization"
            )
        
        if len(high_utilization_periods) > 5:
            recommendations['short_term_planning'].append(
                f"Plan capacity expansion for {len(high_utilization_periods)} periods with >80% utilization"
            )
        
        # Trend analysis
        avg_growth_rate = (forecast_df['predicted_throughput_mbps'].iloc[-1] - 
                          forecast_df['predicted_throughput_mbps'].iloc[0]) / len(forecast_df)
        
        if avg_growth_rate > 100:  # Mbps per day
            recommendations['long_term_strategy'].append(
                f"Implement scalable architecture to handle {avg_growth_rate:.0f} Mbps daily growth"
            )
        
        return recommendations

# Usage example
def main():
    planner = ORANCAPACITYPlanner()
    
    # Load historical data (would come from monitoring systems)
    # planner.load_historical_data('historical_traffic_data.csv')
    
    # For demonstration, create sample data
    sample_dates = pd.date_range(start='2024-01-01', periods=365, freq='H')
    sample_data = pd.DataFrame({
        'timestamp': sample_dates,
        'throughput_mbps': np.random.normal(5000, 1000, len(sample_dates)),
        'connected_users': np.random.poisson(500, len(sample_dates))
    })
    
    planner.historical_data = sample_data
    
    # Train model and forecast
    planner.train_forecast_model()
    forecast = planner.forecast_capacity(30)
    
    # Generate recommendations
    recommendations = planner.generate_capacity_recommendations(forecast)
    
    print("Capacity Planning Results:")
    print(forecast.tail())
    print("\nRecommendations:")
    for category, items in recommendations.items():
        print(f"\n{category.upper()}:")
        for item in items:
            print(f"  - {item}")

if __name__ == "__main__":
    main()
```

## Scalability Design Principles

### Horizontal vs Vertical Scaling
```yaml
scaling_strategies:
  horizontal_scaling:
    advantages:
      - "Better fault tolerance"
      - "Linear performance scaling"
      - "Cost-effective for burst loads"
      - "Geographic distribution capability"
    disadvantages:
      - "Increased complexity"
      - "Network overhead"
      - "State synchronization challenges"
      - "Load balancing requirements"
    
    oran_applications:
      - "Near-RT RIC instances"
      - "O-DU clusters"
      - "Load-balanced CU pools"
      - "Distributed monitoring systems"
  
  vertical_scaling:
    advantages:
      - "Simpler management"
      - "Lower network overhead"
      - "Better cache utilization"
      - "Reduced licensing costs"
    disadvantages:
      - "Single point of failure"
      - "Hardware limitations"
      - "Higher per-unit costs"
      - "Limited scalability ceiling"
    
    oran_applications:
      - "Centralized O-CU units"
      - "High-performance RIC nodes"
      - "Database servers"
      - "Core network functions"
```

### Auto-scaling Configuration
```json
{
  "autoscaling_policies": {
    "near_rt_ric": {
      "metric": "cpu_utilization",
      "threshold_high": 70,
      "threshold_low": 30,
      "scale_up_factor": 1.5,
      "scale_down_factor": 0.7,
      "cooldown_period": 300,
      "min_instances": 2,
      "max_instances": 10
    },
    "o_du_cluster": {
      "metric": "connected_ues",
      "threshold_high": 8000,
      "threshold_low": 2000,
      "scale_up_factor": 2,
      "scale_down_factor": 0.5,
      "cooldown_period": 600,
      "min_instances": 3,
      "max_instances": 15
    },
    "cu_pool": {
      "metric": "throughput_gbps",
      "threshold_high": 8,
      "threshold_low": 2,
      "scale_up_factor": 1.3,
      "scale_down_factor": 0.8,
      "cooldown_period": 450,
      "min_instances": 2,
      "max_instances": 8
    }
  }
}
```

## Cost Optimization Strategies

### Resource Utilization Analysis
```bash
#!/bin/bash
# O-RAN resource utilization and cost optimization analyzer

analyze_resource_utilization() {
    echo "Analyzing O-RAN resource utilization..."
    
    # Collect resource metrics
    collect_cpu_metrics() {
        echo "CPU Utilization Analysis:"
        top -bn1 | grep "Cpu(s)" | awk '{print "Average CPU: " $2+$4 "%"}'
        
        # Per-process analysis
        echo "Top CPU consumers:"
        ps aux --sort=-%cpu | head -10 | awk '{print $11 ": " $3 "%"}'
    }
    
    collect_memory_metrics() {
        echo "Memory Utilization Analysis:"
        free -h | grep "Mem:"
        echo "Memory utilization: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
        
        # Memory pressure analysis
        echo "Memory pressure indicators:"
        cat /proc/meminfo | grep -E "(MemAvailable|MemFree|SwapTotal|SwapFree)"
    }
    
    collect_storage_metrics() {
        echo "Storage Utilization Analysis:"
        df -h | grep -E "(ora|data)"
        echo "I/O statistics:"
        iostat -x 1 5 | grep -A 10 "Device"
    }
    
    # Execute analysis
    collect_cpu_metrics
    collect_memory_metrics
    collect_storage_metrics
    
    # Generate optimization recommendations
    generate_optimization_report
}

generate_optimization_report() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local report_file="/var/reports/resource-optimization-${timestamp}.md"
    
    cat > "$report_file" << EOF
# O-RAN Resource Optimization Report
Generated: $(date)

## Current Resource Utilization
$(analyze_resource_utilization)

## Optimization Recommendations

### Immediate Actions (0-30 days)
- [ ] Right-size over-provisioned instances
- [ ] Implement resource quotas and limits
- [ ] Enable auto-scaling policies
- [ ] Optimize container resource requests

### Short-term Improvements (1-3 months)
- [ ] Implement resource monitoring and alerting
- [ ] Conduct capacity planning exercises
- [ ] Optimize application configurations
- [ ] Review and adjust provisioning strategies

### Long-term Strategy (3-12 months)
- [ ] Implement comprehensive observability
- [ ] Develop predictive capacity planning
- [ ] Optimize architectural patterns
- [ ] Establish resource efficiency KPIs

## Cost Impact Analysis
Estimated monthly savings: $X,XXX - $XX,XXX
ROI timeline: X-X months
Implementation effort: Medium-High

## Next Steps
1. Review current resource allocation
2. Prioritize optimization initiatives
3. Implement monitoring and alerting
4. Execute optimization plan in phases
EOF
    
    echo "Optimization report generated: $report_file"
}
```

## Performance Benchmarking

### Capacity Testing Framework
```python
# O-RAN capacity and performance benchmarking
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
import statistics

class ORANCapacityBenchmark:
    def __init__(self, target_endpoint, test_duration=300):
        self.target_endpoint = target_endpoint
        self.test_duration = test_duration
        self.results = {
            'throughput': [],
            'latency': [],
            'error_rates': [],
            'concurrent_users': []
        }
    
    def run_load_test(self, concurrent_users, request_rate=None):
        """Run load test with specified concurrent users"""
        print(f"Running load test with {concurrent_users} concurrent users...")
        
        start_time = time.time()
        test_results = []
        
        def worker(user_id):
            user_results = []
            while time.time() - start_time < self.test_duration:
                try:
                    request_start = time.time()
                    response = requests.get(self.target_endpoint, timeout=30)
                    request_end = time.time()
                    
                    result = {
                        'user_id': user_id,
                        'response_time': (request_end - request_start) * 1000,  # ms
                        'status_code': response.status_code,
                        'success': response.status_code == 200
                    }
                    user_results.append(result)
                    
                    # Control request rate if specified
                    if request_rate:
                        time.sleep(1.0 / request_rate)
                        
                except Exception as e:
                    user_results.append({
                        'user_id': user_id,
                        'error': str(e),
                        'success': False
                    })
            
            return user_results
        
        # Run test with concurrent users
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(worker, i) for i in range(concurrent_users)]
            for future in futures:
                test_results.extend(future.result())
        
        # Analyze results
        successful_requests = [r for r in test_results if r.get('success', False)]
        failed_requests = [r for r in test_results if not r.get('success', True)]
        
        if successful_requests:
            avg_latency = statistics.mean([r['response_time'] for r in successful_requests])
            throughput = len(successful_requests) / self.test_duration
            
            self.results['throughput'].append(throughput)
            self.results['latency'].append(avg_latency)
            self.results['error_rates'].append(len(failed_requests) / len(test_results) * 100)
            self.results['concurrent_users'].append(concurrent_users)
        
        print(f"Test completed. Throughput: {throughput:.2f} req/sec, "
              f"Latency: {avg_latency:.2f}ms, Error Rate: {(len(failed_requests)/len(test_results)*100):.2f}%")
    
    def run_capacity_sweep(self, user_counts=[10, 50, 100, 200, 500]):
        """Run capacity test across different user counts"""
        print("Running capacity sweep test...")
        
        for user_count in user_counts:
            self.run_load_test(user_count)
            time.sleep(30)  # Cool-down period
    
    def generate_capacity_report(self):
        """Generate comprehensive capacity analysis report"""
        if not any(self.results['throughput']):
            return "No test results available"
        
        max_throughput_idx = self.results['throughput'].index(max(self.results['throughput']))
        max_users = self.results['concurrent_users'][max_throughput_idx]
        max_throughput = self.results['throughput'][max_throughput_idx]
        
        report = f"""
# O-RAN Capacity Benchmark Report

## Summary
- Maximum sustainable throughput: {max_throughput:.2f} requests/second
- Optimal concurrent users: {max_users}
- Average latency at peak: {self.results['latency'][max_throughput_idx]:.2f}ms
- Error rate at peak: {self.results['error_rates'][max_throughput_idx]:.2f}%

## Detailed Results
"""
        
        for i in range(len(self.results['concurrent_users'])):
            report += f"""
### {self.results['concurrent_users'][i]} Concurrent Users
- Throughput: {self.results['throughput'][i]:.2f} req/sec
- Average Latency: {self.results['latency'][i]:.2f}ms
- Error Rate: {self.results['error_rates'][i]:.2f}%
"""
        
        # Capacity recommendations
        report += """
## Capacity Planning Recommendations

Based on the test results, the system can handle:
- Normal operations: Up to {} concurrent users
- Peak loads: Up to {} concurrent users with acceptable performance
- Scaling threshold: Consider scaling at {} concurrent users

Recommended capacity buffers:
- Safety margin: 20-30% above peak usage
- Growth planning: Plan for 2x current capacity within 12 months
""".format(int(max_users * 0.7), max_users, int(max_users * 0.8))
        
        return report

# Usage example
def main():
    benchmark = ORANCapacityBenchmark("http://localhost:8080/api/status")
    benchmark.run_capacity_sweep([10, 50, 100, 200])
    report = benchmark.generate_capacity_report()
    print(report)

if __name__ == "__main__":
    main()
```

This comprehensive capacity planning framework provides the tools and methodologies needed to effectively plan, monitor, and optimize O-RAN system capacity while maintaining cost efficiency and performance requirements.