# Task 1: Monitoring Demonstration

## 1. Overview of Monitoring

Monitoring is the systematic process of collecting, analyzing, and visualizing quantitative data from computing systems, network infrastructure, and software applications to assess health, ensure performance standards, and maintain reliability.

```
 +-----------------+       +--------------------+       +----------------------+
 | Monitored Target| ----> | Time-Series Engine | ----> | Visuals & Alerting   |
 |  (Applications/ | Pull  |   (Prometheus)     |       |  (Grafana / Alerts)  |
 |   Containers)   |       |                    |       |                      |
 +-----------------+       +--------------------+       +----------------------+
```

### Core Dimensions of Monitoring
1. **Metrics**: Real-time numerical measurements recorded at regular intervals (time-series).
2. **Logs**: Timestamped records of discrete events emitted by systems or applications.
3. **Alerts**: Automated threshold notifications dispatched to engineers when health or performance bounds are exceeded.
4. **Resource Utilization**:
   - **CPU Utilization**: Percentage and duration of processor execution time allocated to processes.
   - **Memory Utilization**: Resident Set Size (RSS), virtual memory, and buffer allocations.
5. **Application Health**: Liveness and readiness indicators identifying whether a service is running and ready to handle traffic.

---

## 2. Hands-on Lab Environment Setup

The monitoring environment is built using **Docker Compose**, running containerized instances of **Prometheus** (time-series database & metrics scraper) and **Grafana** (visualization platform).

### Docker Compose Architecture (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: session20-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./alert_rules.yml:/etc/prometheus/alert_rules.yml:ro
      - prometheus_data:/prometheus
    networks:
      - monitoring-network

  grafana:
    image: grafana/grafana:latest
    container_name: session20-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus
    networks:
      - monitoring-network

networks:
  monitoring-network:
    name: 04-grafana_default
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
```

### Starting the Stack

The stack is started in detached mode using `docker compose`:

```bash
docker compose up -d --build
```

### Verification of Running Containers
- Network `04-grafana_default` created.
- Container `session20-prometheus` started and bound to port `9090`.
- Container `session20-grafana` started and bound to port `3000`.

![Docker Compose Deployment Execution](<Screenshot 2026-10-05 173600.png>)

---

## 3. Metrics Collection & Prometheus Querying

Prometheus uses a **pull-based scraping model** over HTTP `/metrics`. It stores samples as time series identified by metric name and key-value label pairs:

$$\text{metric\_name}\{\text{label\_name} = \text{"label\_value"}\}\quad \text{timestamp} \quad \text{value}$$

### 3.1 Prometheus Configuration (`prometheus.yml`)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 5s
    static_configs:
      - targets: ['prometheus:9090']
```

### 3.2 Executing PromQL Queries

In the Prometheus Web Expression Browser (`http://localhost:9090`), the following queries were executed:

#### 1. Application Health (`up`)
- **Query**: `up`
- **Result**: `up{instance="prometheus:9090", job="prometheus"} => 1`
- **Significance**:
  - `1`: The target was reachable and successfully scraped during the last interval.
  - `0`: The target is unreachable, unresponsive, or returning HTTP error status codes.

#### 2. CPU Utilization (`process_cpu_seconds_total`)
- **Query**: `process_cpu_seconds_total`
- **Result**: `process_cpu_seconds_total{instance="prometheus:9090", job="prometheus"} => 2.06`
- **Significance**:
  - A cumulative counter measuring total user and system CPU time spent in seconds.
  - To derive active percentage CPU utilization over 1 minute:
    $$\text{CPU Usage (\%)} = \text{rate}(\text{process\_cpu\_seconds\_total}[1m]) \times 100$$

![Prometheus Querying Up and CPU Metrics](<Screenshot 2026-10-05 173527.png>)

---

## 4. Grafana Dashboards & Visualizations

Grafana connects to Prometheus via an HTTP Data Source (`http://prometheus:9090`) to render intuitive, real-time graphical representations of operational telemetry.

### 4.1 Dashboard Configuration

A new dashboard was designed with two essential operational panels:

| Panel Name | Panel Type | PromQL Query | Displayed Value | Operational Meaning |
| :--- | :--- | :--- | :--- | :--- |
| **CPU** | Gauge Panel | `process_cpu_seconds_total` (or CPU rate) | **2.13** | Visualizes current CPU consumption against operational thresholds (green/yellow/red). |
| **state** | Stat Panel | `up` | **1** | Instant visual indicator of service operational status (1 = Healthy / UP). |

![Grafana Visualization Dashboard](<Screenshot 2026-10-05 173452.png>)

---

## 5. Alerts & Threshold Management

Monitoring becomes proactive through automated alerting. Prometheus evaluates rules periodically and pushes firing alerts to Alertmanager for routing, grouping, and notification (Slack, PagerDuty, Email).

### Alert Rule Specifications (`alert_rules.yml`)

```yaml
groups:
  - name: application_health_alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service instance {{ $labels.instance }} is down"
          description: "Service {{ $labels.job }} at {{ $labels.instance }} has been unreachable for more than 1 minute."

      - alert: HighCpuUsage
        expr: rate(process_cpu_seconds_total[1m]) * 100 > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage on {{ $labels.instance }} is above 80% (current value: {{ $value }}%)."

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes > 500000000
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High memory utilization on {{ $labels.instance }}"
          description: "Process resident memory has exceeded 500MB on {{ $labels.instance }}."
```

### Alert States Lifecycle
1. **Inactive**: Threshold criteria are not met; system is operating normally.
2. **Pending**: Threshold breached, but waiting for the `for:` duration to prevent false alarms due to transient spikes.
3. **Firing**: Threshold breached continuously for the defined duration; alert sent to Alertmanager.
