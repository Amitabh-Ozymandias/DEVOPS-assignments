# Session 20: Monitoring, Observability & GitOps - Submission

## Student Information
- **Course**: DevOps Program
- **Session**: Session 20 - Monitoring, Observability & GitOps
- **Repository**: [Devops-assignments/20-monitoring-observability](https://github.com/Amitabh-Ozymandias/Devops-assignments/tree/main/20-monitoring-observability)

---

## Deliverables Checklist
- [x] **Task 1: Monitoring Demo** (Metrics, Logs, Alerts, CPU, Memory, Health) - See [`01-monitoring-demo.md`](01-monitoring-demo.md)
- [x] **Task 2: Observability Documentation** (3 Pillars, Why Required, Common Tools, Kubernetes Observability) - See [`02-observability-documentation.md`](02-observability-documentation.md)
- [x] **Task 3: GitOps Demo** (Principles, Git as source of truth, Declarative configs, Reconciliation, K8s + Argo CD) - See [`03-gitops-demo.md`](03-gitops-demo.md)
- [x] **Screenshots Embedded & Documented**
- [x] **README.md** - See [`README.md`](README.md)

---

## Task 1: Monitoring Demonstration Summary

A local monitoring stack composed of **Prometheus** and **Grafana** was orchestrated using Docker Compose.

### 1.1 Stack Deployment
- Started Prometheus (`session20-prometheus`) on port `9090` and Grafana (`session20-grafana`) on port `3000`.

![Docker Compose Deployment](<Screenshot 2026-10-05 173600.png>)

### 1.2 Prometheus Telemetry Scrape & PromQL Queries
- Verified target scrape health via `up` metric (returned `1`).
- Verified process CPU metrics via `process_cpu_seconds_total` (returned `2.06`).

![Prometheus Metrics Queries](<Screenshot 2026-10-05 173527.png>)

### 1.3 Grafana Visualization Dashboard
- Created custom dashboard with:
  - Gauge panel visualizing **CPU** utilization (`2.13`).
  - Stat panel visualizing application **state** health (`1`).

![Grafana Visualization Dashboard](<Screenshot 2026-10-05 173452.png>)

---

## Task 2: Observability Summary

The complete documentation of Observability principles, comparison of the three pillars, tooling landscape, and Kubernetes observability patterns is located in [`02-observability-documentation.md`](02-observability-documentation.md).

### Core Pillars
1. **Metrics**: Aggregatable numeric time-series data for fast alerting and trend tracking (Prometheus, Datadog).
2. **Logs**: Timestamped contextual event output for granular root-cause analysis (Loki, Fluent Bit, ELK).
3. **Traces**: Distributed request propagation flows across microservices for latency and bottleneck detection (Jaeger, OpenTelemetry).

### Kubernetes Observability Architecture
- **Host & Node Telemetry**: `cAdvisor` (embedded in kubelet) and `node-exporter` (DaemonSet).
- **Control Plane & Object State**: `kube-state-metrics`.
- **Log Streaming**: Fluent Bit / Promtail DaemonSets tailing `/var/log/pods/`.
- **Application Probes**: Liveness, Readiness, and Startup probes.

---

## Task 3: GitOps Summary

The full GitOps conceptual documentation and Argo CD demonstration manifests are located in [`03-gitops-demo.md`](03-gitops-demo.md).

### Key Concepts
- **Git as Single Source of Truth**: All infrastructure and application state stored declaratively in version control.
- **Continuous Reconciliation**: In-cluster controllers (Argo CD) continuously compare desired state against actual state and self-heal configuration drift automatically.
- **Pull vs Push**: In-cluster GitOps operators eliminate the need to expose cluster API credentials to external CI runners.

---

## Quick Reference Links
- [Master README](README.md)
- [Task 1: Monitoring Demo](01-monitoring-demo.md)
- [Task 2: Observability Documentation](02-observability-documentation.md)
- [Task 3: GitOps Demo](03-gitops-demo.md)
