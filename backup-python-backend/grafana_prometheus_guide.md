# Grafana + Prometheus Quick Start for Polaris

This document provides a minimal, production-friendly guide to visualize Polaris backend metrics and set alert rules.

Prerequisites:
- Prometheus scraping the backend at /api/metrics (alias added) or /api/system/prometheus-metrics
- Grafana 9+ with Prometheus data source

Prometheus scrape config example:
- job_name: polaris-backend
  metrics_path: /api/metrics
  scrape_interval: 15s
  static_configs:
    - targets: ['<BACKEND_HOST>:443']

Panels (JSON snippets):
1) Request rate (req/s)
{
  "title": "API Request Rate",
  "type": "stat",
  "targets": [{"expr":"sum(rate(http_requests_total[5m]))"}]
}

2) Error rate (%)
{
  "title": "API Error Rate %",
  "type": "gauge",
  "targets": [{"expr":"sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100"}],
  "fieldConfig": {"defaults":{"min":0,"max":100}}
}

3) p95 latency (ms)
{
  "title": "API Latency p95 (ms)",
  "type": "stat",
  "targets": [{"expr":"histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) * 1000"}]
}

4) CPU and Memory (psutil)
{
  "title": "Container CPU %",
  "type": "stat",
  "targets": [{"expr":"avg(polaris_cpu_percent)"}]
}
{
  "title": "Container Memory %",
  "type": "stat",
  "targets": [{"expr":"avg(polaris_memory_percent)"}]
}

Alerts (Prometheus rules examples):
- name: polaris.rules
  rules:
  - alert: HighErrorRate
    expr: sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) > 0.02
    for: 10m
    labels: {severity: critical}
    annotations: {summary: "High 5xx error rate", description: "Error rate >2% for 10m"}
  - alert: HighLatencyP95
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 0.6
    for: 10m
    labels: {severity: warning}
    annotations: {summary: "High p95 latency", description: ">600ms for 10m"}

Notes:
- Replace <BACKEND_HOST> with your ingress host; if TLS-terminated, use appropriate scheme/port.
- Fine-tune thresholds to match SLOs.
- Wire alerts to your alertmanager/on-call channel.
