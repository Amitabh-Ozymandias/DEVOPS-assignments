# Session 20: Monitoring, Observability & GitOps

This repository contains the comprehensive submission for **Session 20: Monitoring, Observability & GitOps**. It covers the hands-on monitoring stack setup with Prometheus and Grafana, in-depth documentation of the three pillars of observability and Kubernetes observability architecture, and GitOps workflows powered by declarative configuration and continuous reconciliation.

---

## Table of Contents
1. [Deliverables Summary](#deliverables-summary)
2. [Task 1: Monitoring Demonstration](#task-1-monitoring-demonstration)
   - [Monitoring Stack Architecture](#monitoring-stack-architecture)
   - [Docker Compose Deployment](#docker-compose-deployment)
   - [Prometheus Metrics Scraping & PromQL](#prometheus-metrics-scraping--promql)
   - [Grafana Dashboard Visualization](#grafana-dashboard-visualization)
   - [Alert Rules & Alertmanager](#alert-rules--alertmanager)
3. [Task 2: Observability Documentation](#task-2-observability-documentation)
   - [What is Observability?](#what-is-observability)
   - [The Three Major Pillars](#the-three-major-pillars)
   - [Why Observability is Required](#why-observability-is-required)
   - [Common Tools Ecosystem](#common-tools-ecosystem)
   - [Kubernetes Observability Architecture](#kubernetes-observability-architecture)
4. [Task 3: GitOps Concepts & Demonstration](#task-3-gitops-concepts--demonstration)
   - [Core Principles of GitOps](#core-principles-of-gitops)
   - [Git as the Single Source of Truth](#git-as-the-single-source-of-truth)
   - [Continuous Reconciliation & Self-Healing](#continuous-reconciliation--self-healing)
   - [GitOps Pull Pipeline Workflow](#gitops-pull-pipeline-workflow)
   - [Kubernetes + GitOps Demo (Argo CD)](#kubernetes--gitops-demo-argo-cd)
5. [Evidence & Screenshots](#evidence--screenshots)
6. [Repository Structure](#repository-structure)

---

## Deliverables Summary

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Monitoring Demo** | [`01-monitoring-demo.md`](01-monitoring-demo.md) | Prometheus + Grafana stack, metric scraping, CPU/memory, app health, and alerting rules. |
| **Observability Documentation** | [`02-observability-documentation.md`](02-observability-documentation.md) | In-depth breakdown of Metrics, Logs, Traces, why observability is required, tooling, and K8s observability. |
| **GitOps Demo** | [`03-gitops-demo.md`](03-gitops-demo.md) | GitOps principles, declarative configuration, reconciliation loops, and Argo CD manifests. |
| **Screenshots** | Embedded below in [Evidence & Screenshots](#evidence--screenshots) | Prometheus query executions, Grafana operational dashboard, and Docker Compose stack runtime. |
| **README.md** | [`README.md`](README.md) / [`Submission.md`](Submission.md) | Complete session guide and consolidated documentation. |

---

## Task 1: Monitoring Demonstration

### Monitoring Stack Architecture
The monitoring demonstration is built using containerized microservices managed via Docker Compose:
- **Prometheus** (`session20-prometheus` on port `9090`): Time-series metrics engine collecting target health and resource metrics.
- **Grafana** (`session20-grafana` on port `3000`): Data visualization and dashboard platform connected to Prometheus as an HTTP data source.

```
       +--------------------------------------------------------+
       |                  Docker Host Network                   |
       |                                                        |
       |  +--------------------+        +--------------------+  |
       |  |     Prometheus     |        |      Grafana       |  |
       |  | (Port 9090:9090)   | <----- | (Port 3000:3000)   |  |
       |  | session20-         |  Pulls | session20-grafana  |  |
       |  | prometheus         |  data  |                    |  |
       |  +--------------------+        +--------------------+  |
       |            ^                                           |
       |            | Scrapes /metrics                          |
       |            |                                           |
       |  +--------------------+                                |
       |  | Scrape Target      |                                |
       |  | (localhost:9090)   |                                |
       |  +--------------------+                                |
       +--------------------------------------------------------+
```

### Docker Compose Deployment
The stack was deployed using `docker compose up -d --build` within the project directory:

```bash
docker compose up -d --build
```

**Runtime Output Verification:**
- Network `04-grafana_default` was created.
- Container `session20-prometheus` was created and started in detached mode.
- Container `session20-grafana` was created and started in detached mode.

![Docker Compose Deployment Execution](<Screenshot 2026-10-05 173600.png>)

### Prometheus Metrics Scraping & PromQL

Prometheus periodically polls targets configured in `prometheus.yml`. In the Prometheus Expression Browser (`http://localhost:9090`), the following critical metrics were evaluated:

1. **Application Health (`up`)**:
   - **PromQL**: `up`
   - **Evaluated Value**: `1` for target `instance="prometheus:9090", job="prometheus"`
   - **Meaning**: The application target is alive, accepting HTTP connections, and returning valid telemetry.

2. **CPU Utilization (`process_cpu_seconds_total`)**:
   - **PromQL**: `process_cpu_seconds_total`
   - **Evaluated Value**: `2.06` seconds for target `instance="prometheus:9090", job="prometheus"`
   - **Meaning**: Total cumulative user and system CPU execution time consumed by the process.

![Prometheus Metrics Queries](<Screenshot 2026-10-05 173527.png>)

### Grafana Dashboard Visualization
A live operations dashboard was created in Grafana (`http://localhost:3000`) consuming the Prometheus data source:

1. **CPU Gauge Panel**:
   - Displays real-time CPU metric (**2.13**) with color-graded operational ranges (green indicates safe operating bounds).
2. **State Stat Panel**:
   - Displays application state (**1**), indicating healthy operational status.

![Grafana Operational Dashboard](<Screenshot 2026-10-05 173452.png>)

### Alert Rules & Alertmanager
To transition from passive monitoring to automated alerting, Prometheus alert rules are defined below:

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
          description: "Service has been unreachable for more than 1 minute."

      - alert: HighCpuUsage
        expr: rate(process_cpu_seconds_total[1m]) * 100 > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU utilization has exceeded 80%."

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes > 500000000
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High memory utilization on {{ $labels.instance }}"
          description: "Process memory consumption has exceeded 500MB."
```

---

## Task 2: Observability Documentation

### What is Observability?
Observability is the ability to infer the internal states of a complex system based on the external telemetry data it emits.

- **Monitoring**: Focuses on **symptoms** and answerable questions ("Is the service down? Is latency above 500ms?").
- **Observability**: Focuses on **interrogating unknown-unknowns** in distributed systems ("Why did this specific customer's request fail across microservices A, B, and C?").

### The Three Major Pillars

```
+--------------------------------------------------------------------------+
|                  THE THREE PILLARS OF OBSERVABILITY                      |
|                                                                          |
|   1. METRICS               2. LOGS                   3. TRACES           |
|   -----------------        -----------------         -----------------   |
|   - Numeric time-series    - Event records with      - End-to-end flow   |
|   - Aggregatable & fast    timestamp & context       across services     |
|   - Low storage cost       - Line-of-code debugging  - Identifies        |
|   - Best for Alerting      - High storage cost       latency & hops      |
|                                                                          |
|   Examples:                Examples:                 Examples:           |
|   - CPU / Memory usage     - Stack traces            - Request latency   |
|   - Request throughput     - Authentication failure  - DB query duration |
|   - Error rates            - Audit events            - Microservice hop  |
+--------------------------------------------------------------------------+
```

1. **Metrics**: Aggregatable numeric data points sampled at discrete intervals. Metric types include **Counters** (e.g., total requests), **Gauges** (e.g., memory in use), **Histograms** (e.g., request latency distributions), and **Summaries**.
2. **Logs**: Timestamped contextual records generated during code execution. Structured logging (JSON format) allows indexing fields like `trace_id`, `user_id`, and `error_code`.
3. **Traces**: Graph of interconnected **Spans** representing a single user request's complete path through microservices, databases, and message brokers.

### Why Observability is Required
1. **Modern Microservice Complexity**: Distributed services communicate across network boundaries; failures cascade rapidly.
2. **Diagnosing "Unknown-Unknowns"**: Static pre-configured dashboards cannot predict novel failure modes.
3. **Minimizing MTTR (Mean Time to Resolution)**: Engineers can drill down from an alert metric $\rightarrow$ to the distributed trace $\rightarrow$ to the exact log stack trace.
4. **SLO & Error Budget Tracking**: Essential for measuring Service Level Indicators (SLIs) against reliability commitments.

### Common Tools Ecosystem
- **Metrics**: Prometheus, Thanos, VictoriaMetrics, Datadog.
- **Logs**: Grafana Loki, Fluent Bit, Promtail, Elasticsearch / Logstash / Kibana (ELK / EFK).
- **Traces**: Jaeger, Zipkin, Grafana Tempo, OpenTelemetry (OTel Collector).
- **Visualization**: Grafana.

### Kubernetes Observability Architecture
In Kubernetes clusters, observability requires telemetry at three distinct levels:
1. **Cluster State**: `kube-state-metrics` queries the Kubernetes API server for the condition of Deployments, ReplicaSets, and Pod statuses.
2. **Container & Node Resources**:
   - `cAdvisor` (built into the `kubelet`) gathers container cgroup statistics (`container_cpu_usage_seconds_total`, `container_memory_working_set_bytes`).
   - `node-exporter` (DaemonSet) collects underlying Linux host hardware metrics.
3. **Log Aggregation**: Fluent Bit / Promtail runs as a `DaemonSet` on every node, tailing `/var/log/pods/` and shipping enriched streams to Loki or Elasticsearch.
4. **Health Probes**:
   - `livenessProbe`: Restarts unhealthy pods.
   - `readinessProbe`: Isolates pods from load balancer endpoints until ready to serve traffic.
   - `startupProbe`: Prevents premature restarts during slow application startup.

---

## Task 3: GitOps Concepts & Demonstration

### Core Principles of GitOps
GitOps is a modern operational paradigm where Git is the **single source of truth** for all declarative infrastructure and application manifests.

```
+-------------------------------------------------------------------------+
|                            GITOPS LIFECYCLE                             |
|                                                                         |
|  [ Git Repository ]                                                     |
|  - Source of Truth               1. Detects Drift / New Commit          |
|  - Declarative YAML manifests  =================================> [+]   |
|                                                                    |    |
|                                                           [ Argo CD / ] |
|                                                           [ Flux CD   ] |
|                                                                    |    |
|  [ Kubernetes Cluster ]          2. Automatically Reconciles       |    |
|  - Live Infrastructure         <================================= [+]   |
|  - Actual State (Self-Healed)                                           |
+-------------------------------------------------------------------------+
```

### Git as the Single Source of Truth
- No direct `kubectl` writes to the production cluster.
- All configuration changes require a Pull Request, code review, security scans, and merge commit.
- Immediate rollback capability: Reverting a Git commit (`git revert <hash>`) automatically triggers a rollback in the cluster.

### Continuous Reconciliation & Self-Healing
GitOps controllers (such as **Argo CD** or **Flux**) run continuously inside the cluster:
1. Compare live cluster state ($S_{\text{actual}}$) against Git repository manifests ($S_{\text{desired}}$).
2. If discrepancies occur (drift):
   - **Out of Sync** is flagged.
   - If **Automated Self-Healing** is enabled, the controller automatically brings the cluster back into alignment with Git.

### Traditional Push vs GitOps Pull

| Capability | Traditional CI/CD (Push) | GitOps (Pull) |
| :--- | :--- | :--- |
| **Trigger Mechanism** | External CI server executes commands | In-cluster agent watches Git repo |
| **Credential Storage** | Cluster credentials stored on external CI runner | Zero external cluster credentials required |
| **Drift Correction** | None; manual cluster changes go undetected | Continuous active reconciliation and self-healing |

### Kubernetes + GitOps Demo (Argo CD)
The declarative configuration demonstrates a microservice deployment synchronized by Argo CD:
- **Application Manifests**: Declarative Deployment (3 replicas) and Service definitions with health probes and resource limits (detailed in [`03-gitops-demo.md`](03-gitops-demo.md)).
- **Argo CD Application Custom Resource**: Configured with automated sync and continuous self-healing:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: sample-web-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/Amitabh-Ozymandias/Devops-assignments.git'
    targetRevision: HEAD
    path: 20-monitoring-observability/gitops
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

## Evidence & Screenshots

### Screenshot 1: Docker Compose Monitoring Stack Startup
Shows the local launch of `session20-prometheus` and `session20-grafana` inside the `04-grafana_default` network:

![Docker Compose Deployment Execution](<Screenshot 2026-10-05 173600.png>)

---

### Screenshot 2: Prometheus Metrics & Health Queries
Shows Prometheus successfully scraping the internal metric endpoint and evaluating `up` and `process_cpu_seconds_total`:

![Prometheus Metrics Queries](<Screenshot 2026-10-05 173527.png>)

---

### Screenshot 3: Grafana Operational Dashboard
Shows the real-time operational dashboard with a Gauge panel for CPU utilization and a Stat panel for service state:

![Grafana Operational Dashboard](<Screenshot 2026-10-05 173452.png>)

---

## Repository Structure

```
20-monitoring-observability/
│
├── README.md                           # Master submission & session guide
├── Submission.md                       # Formatted assignment submission file
├── 01-monitoring-demo.md               # Task 1: Monitoring Demonstration
├── 02-observability-documentation.md   # Task 2: Observability Documentation
├── 03-gitops-demo.md                   # Task 3: GitOps Concepts & Demonstration
│
├── Screenshot 2026-10-05 173452.png    # Grafana Dashboard (CPU Gauge & State)
├── Screenshot 2026-10-05 173527.png    # Prometheus Query Execution (up, CPU)
└── Screenshot 2026-10-05 173600.png    # Docker Compose Container Deployment
```
