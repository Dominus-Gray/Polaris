# RP CRM-lite Prometheus Dashboard Configuration

This document provides Prometheus queries and Grafana panel configurations for monitoring the RP CRM-lite system.

## RP CRM-lite Metrics

### Available Metrics

1. **polaris_rp_leads_created_total** - Total RP leads created, labeled by `rp_type`
2. **polaris_rp_leads_updated_total** - Total RP lead updates, labeled by `status_from` and `status_to`
3. **polaris_rp_package_previews_total** - Total RP package previews, labeled by `rp_type`
4. **polaris_rp_requirements_seeded_total** - Total RP requirements seeded, labeled by `rp_type`

### Grafana Dashboard Panels

#### 1. Total RP Leads Created (Counter)
```promql
sum(polaris_rp_leads_created_total)
```

#### 2. RP Leads Created by Type (Pie Chart)
```promql
sum by (rp_type) (polaris_rp_leads_created_total)
```

#### 3. RP Lead Status Changes (Time Series)
```promql
rate(polaris_rp_leads_updated_total[5m])
```

#### 4. Package Preview Activity (Counter)
```promql
sum(polaris_rp_package_previews_total)
```

#### 5. Top RP Types by Activity (Bar Graph)
```promql
sum by (rp_type) (
  polaris_rp_leads_created_total + 
  polaris_rp_package_previews_total + 
  polaris_rp_requirements_seeded_total
)
```

#### 6. RP Lead Conversion Funnel (Stat Panels)
- **New Leads**: `sum(increase(polaris_rp_leads_updated_total{status_to="new"}[24h]))`
- **Working Leads**: `sum(increase(polaris_rp_leads_updated_total{status_to="working"}[24h]))`
- **Contacted Leads**: `sum(increase(polaris_rp_leads_updated_total{status_to="contacted"}[24h]))`
- **Approved Leads**: `sum(increase(polaris_rp_leads_updated_total{status_to="approved"}[24h]))`

#### 7. Requirements Seeding Activity (Time Series)
```promql
rate(polaris_rp_requirements_seeded_total[5m])
```

### Sample Grafana Dashboard JSON Configuration

```json
{
  "dashboard": {
    "title": "RP CRM-lite Monitoring",
    "panels": [
      {
        "title": "Total RP Leads Created",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(polaris_rp_leads_created_total)",
            "legendFormat": "Total Leads"
          }
        ]
      },
      {
        "title": "RP Leads by Type",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (rp_type) (polaris_rp_leads_created_total)",
            "legendFormat": "{{rp_type}}"
          }
        ]
      },
      {
        "title": "Lead Status Changes (5min rate)",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(polaris_rp_leads_updated_total[5m])",
            "legendFormat": "{{status_from}} → {{status_to}}"
          }
        ]
      },
      {
        "title": "Package Preview Activity",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(polaris_rp_package_previews_total)",
            "legendFormat": "Total Previews"
          }
        ]
      }
    ]
  }
}
```

### Prometheus Alerts

#### High Lead Creation Rate
```yaml
- alert: HighRPLeadCreation
  expr: rate(polaris_rp_leads_created_total[5m]) > 2
  for: 2m
  labels:
    severity: info
  annotations:
    summary: "High RP lead creation rate detected"
    description: "RP leads are being created at a rate of {{ $value }} per second"
```

#### Stalled Leads Alert
```yaml
- alert: StalledRPLeads
  expr: increase(polaris_rp_leads_updated_total{status_to="new"}[1h]) > increase(polaris_rp_leads_updated_total{status_to="working"}[1h]) * 5
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "High number of stalled RP leads"
    description: "Many leads remain in 'new' status without progression"
```

### Quick Setup Instructions

1. **Access Metrics Endpoint**: 
   ```bash
   curl http://your-backend/api/metrics | grep polaris_rp
   ```

2. **Add to Prometheus Config** (`prometheus.yml`):
   ```yaml
   scrape_configs:
     - job_name: 'polaris-backend'
       static_configs:
         - targets: ['your-backend:8001']
       metrics_path: '/api/metrics'
       scrape_interval: 30s
   ```

3. **Import Dashboard**: Use the JSON configuration above in Grafana

4. **Set Up Alerts**: Add the alert rules to your Prometheus rules file

### Usage Scenarios

1. **Business Intelligence**: Track which RP types are most popular
2. **Process Monitoring**: Monitor lead conversion rates and identify bottlenecks
3. **System Health**: Ensure RP features are being used and functioning correctly
4. **Capacity Planning**: Understand usage patterns to plan for scaling

These metrics provide comprehensive visibility into the RP CRM-lite system performance and usage patterns.