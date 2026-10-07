# Task 2: Observability Documentation

## 1. What is Observability?

**Observability** is a measure of how well internal states of a system can be inferred from knowledge of its external outputs (telemetry data).

While traditional **Monitoring** tells you *when something is wrong* ("Is the system working?"), **Observability** enables you to understand *why it went wrong* ("What caused this specific request to fail in our distributed architecture?").

```
  +-----------------------------------------------------------------------+
  |                             OBSERVABILITY                             |
  |                                                                       |
  |     +----------------+   +----------------+   +----------------+      |
  |     |    METRICS     |   |      LOGS      |   |     TRACES     |      |
  |     |                |   |                |   |                |      |
  |     |  Aggregable    |   | Timestamped    |   | Request path   |      |
  |     |  numeric time- |   | contextual     |   | across micro-  |      |
  |     |  series data   |   | event streams  |   | services       |      |
  |     +----------------+   +----------------+   +----------------+      |
  |            |                     |                     |              |
  |       "Is there a           "What caused          "Where is the       |
  |        problem?"             the problem?"         bottleneck?"       |
  +-----------------------------------------------------------------------+
```

---

## 2. The Three Pillars of Observability

### 2.1 Metrics
- **Definition**: Numerically measurable data points aggregated over set intervals of time. Metrics are lightweight, computationally cheap to store, and highly indexable.
- **Data Model**: Metric Name, Key-Value Labels (Dimensions), Timestamp, and Floating-Point Value.
  - *Example*: `http_requests_total{method="POST", status="500", service="payment"} 142`
- **Metric Types**:
  1. **Counter**: Monotonically increasing number (e.g., total requests, errors, CPU seconds).
  2. **Gauge**: Value that can go up or down arbitrarily (e.g., memory usage, temperature, queue size).
  3. **Histogram**: Samples observations into configurable buckets and counts occurrences (e.g., request duration).
  4. **Summary**: Calculates configurable quantiles (p50, p90, p99) over sliding time windows.
- **Strengths**: Low storage overhead, fast alerting, excellent for trend analysis and anomaly detection.
- **Limitations**: Lacks granular individual request context and execution details.

### 2.2 Logs
- **Definition**: Timestamped, structured or unstructured text messages emitted when specific code paths execute.
- **Data Model**: JSON or text payload with timestamp, log level (`INFO`, `WARN`, `ERROR`), source host, process ID, and message context.
  - *Example*:
    ```json
    {
      "timestamp": "2026-10-07T22:15:30.124Z",
      "level": "ERROR",
      "service": "order-service",
      "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
      "message": "Database connection pool exhausted during transaction commit",
      "error_code": "DB_TIMEOUT"
    }
    ```
- **Strengths**: Provides exact stack traces, exception messages, and line-of-code context required for deep root-cause debugging.
- **Limitations**: High volume, high storage cost, difficult to aggregate without structured schema.

### 2.3 Traces
- **Definition**: End-to-end representation of a request's path as it traverses distributed microservices, databases, caches, and third-party APIs.
- **Core Building Blocks**:
  - **Trace**: The complete execution tree of a request, identified by a unique `Trace ID`.
  - **Span**: A single contiguous unit of work or segment within a trace (e.g., an HTTP call, SQL query execution). Spans contain start time, duration, parent span ID, and metadata tags.
- **Strengths**: Pinpoints latency bottlenecks, clarifies dependency topology, and reveals failure cascading in microservice architectures.
- **Limitations**: Instrumentation overhead, requires context propagation headers (`W3C Trace Context` or `B3`), high volume requiring sampling.

---

## 3. Comparison of the Three Pillars

| Dimension | Metrics | Logs | Traces |
| :--- | :--- | :--- | :--- |
| **Primary Question** | *Is something degrading or breaking?* | *What specific error occurred?* | *Where across services did latency happen?* |
| **Data Nature** | Numerical, time-series | Textual / JSON event records | Graph / Directed Acyclic Graph (DAG) of Spans |
| **Storage Cost** | Low | High | High (managed via sampling) |
| **Alertability** | **Highest** (instant threshold alerts) | Medium (log pattern matching) | Medium (SLO violation alerts) |
| **Root-Cause Depth** | Low (indicates symptom) | **High** (precise stack traces) | **High** (distributed flow & context) |

---

## 4. Why Observability is Required in Modern Systems

1. **Shift to Microservices & Cloud-Native Architectures**: Monoliths could be debugged via single log files. Microservices involve hundreds of distributed network hops where failures cascade across services.
2. **Solving the "Unknown-Unknowns"**: Traditional monitoring handles *known-knowns* (pre-defined dashboards for known failure modes). Observability enables ad-hoc querying to diagnose unanticipated edge cases (*unknown-unknowns*).
3. **Drastic Reduction in MTTR (Mean Time to Resolution)**:
   - Metric alert detects degradation $\rightarrow$ Distributed trace identifies the failing downstream service $\rightarrow$ Correlated log pinpoints the exact null pointer exception.
4. **SLI / SLO / SLA Enforcement**: Provides rigorous telemetry required to maintain Service Level Objectives (SLOs) and error budgets.
5. **Capacity Planning & Cost Optimization**: Uncovers underutilized or overprovisioned infrastructure and inefficient database queries.

---

## 5. Common Tools Ecosystem

| Category | Open-Source Standards | Enterprise / Managed Platforms |
| :--- | :--- | :--- |
| **Metrics Collection & Storage** | **Prometheus**, Thanos, VictoriaMetrics, Cortex | Amazon CloudWatch, Datadog, New Relic |
| **Log Ingestion & Analysis** | **Grafana Loki**, Fluent Bit, Promtail, Vector, Elasticsearch (ELK / EFK) | Splunk, Datadog Log Management, AWS CloudWatch Logs |
| **Distributed Tracing** | **Jaeger**, Zipkin, Grafana Tempo | Dynatrace, Honeycomb, Lightstep |
| **Standardized Telemetry API** | **OpenTelemetry (OTel)** (Collector, SDKs, APIs) | AWS Distro for OpenTelemetry (ADOT) |
| **Unified Visualization** | **Grafana** | Datadog Dashboards, Kibana |

---

## 6. Kubernetes Observability Architecture

Kubernetes introduces dynamic, ephemeral orchestration where pods frequently start, stop, reschedule, and autoscale across cluster nodes. Observability in Kubernetes requires instrumentation across multiple layers:

```
+-------------------------------------------------------------------------+
|                        Kubernetes Cluster                               |
|                                                                         |
|  +--------------------+   +---------------------+   +----------------+  |
|  |   Control Plane    |   |  Node-Level Daemon  |   |   Workloads    |  |
|  |                    |   |                     |   |   (Pods)       |  |
|  | - kube-apiserver   |   | - kubelet (cAdvisor)|   | - App Metrics  |  |
|  | - etcd             |   | - node-exporter     |   | - App Logs     |  |
|  | - kube-controller  |   | - Fluent Bit        |   | - OTel Spans   |  |
|  | - kube-scheduler   |   |   (DaemonSet)       |   | - K8s Probes   |  |
|  +--------------------+   +---------------------+   +----------------+  |
|            |                         |                       |          |
|            v                         v                       v          |
|      kube-state-metrics        Host Telemetry           Log Collectors  |
+-------------------------------------------------------------------------+
                                       |
                                       v
                     +-----------------------------------+
                     | Prometheus / Loki / Tempo Backend |
                     +-----------------------------------+
```

### 6.1 Cluster & Node Telemetry Components
1. **cAdvisor (Container Advisor)**:
   - Embedded natively within the `kubelet`.
   - Collects container-level CPU, memory, filesystem, and network statistics directly from Linux cgroups (`container_cpu_usage_seconds_total`, `container_memory_working_set_bytes`).
2. **kube-state-metrics (KSM)**:
   - Listens to the Kubernetes API server and generates metrics on the health and state of objects (Deployments, Pods, ReplicaSets, Nodes, PVs).
   - *Example*: `kube_pod_status_phase`, `kube_deployment_status_replicas_available`.
3. **Node Exporter**:
   - Deployed as a `DaemonSet` on every cluster node.
   - Gathers underlying hardware and Linux OS metrics (disk I/O, network bandwidth, host CPU/memory).

### 6.2 Log Collection Pattern in Kubernetes
- Containers emit logs to `stdout` and `stderr`.
- The container runtime (containerd/CRI-O) writes these streams to `/var/log/pods/` on the node host filesystem.
- A **DaemonSet log forwarder** (such as **Fluent Bit** or **Promtail**) tails the host directory, enriches records with Kubernetes pod/namespace/container metadata, and forwards them to a centralized backend (Elasticsearch or Grafana Loki).

### 6.3 Kubernetes Health Checks (Probes)
- **Liveness Probe**: Determines if the application container needs to be restarted.
- **Readiness Probe**: Determines if the pod is ready to accept incoming service traffic (keeps pod out of Service endpoints until healthy).
- **Startup Probe**: Protects slow-starting legacy applications by disabling liveness/readiness checks until initial boot completes.
