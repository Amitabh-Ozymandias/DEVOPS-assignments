# Task 3: GitOps Concepts & Demonstration

## 1. What is GitOps?

**GitOps** is an operational framework that takes DevOps best practices used for application development—such as version control, code review, automated testing, and CI/CD pipelines—and applies them to infrastructure automation and application delivery.

Coined by Alexis Richardson (Weaveworks) in 2017, GitOps centers on four foundational principles:

1. **Declarative Descriptions**: Entire system state (infrastructure, network, applications) is described declaratively in manifests (e.g., Kubernetes YAML, Kustomize, Helm).
2. **Versioned Desired State in Git**: Git serves as the single, authoritative **source of truth**. All changes occur via Git pull requests and commits.
3. **Automated Pull & Application**: Approved changes in Git are automatically pulled and applied to target environments by an in-cluster software agent.
4. **Continuous Reconciliation & Self-Healing**: Software agents continuously monitor running cluster state against Git. If drift occurs (e.g., accidental manual change), the agent reconciles the cluster back to the state declared in Git.

```
       +-------------------------------------------------------------+
       |                        GITOPS ENGINE                        |
       |                                                             |
       |    +--------------------+         +--------------------+    |
       |    |  Desired State     |         |   Actual State     |    |
       |    |   (in Git Repo)    |         | (in Live Cluster)  |    |
       |    +--------------------+         +--------------------+    |
       |              \                       /                      |
       |               \                     /                       |
       |                v                   v                        |
       |            +---------------------------+                    |
       |            |   Reconciliation Agent    |                    |
       |            |      (Argo CD / Flux)     |                    |
       |            +---------------------------+                    |
       |                          |                                  |
       |            Drift Detected? Self-Heals!                      |
       |            Pulls updates automatically                      |
       +-------------------------------------------------------------+
```

---

## 2. Core Tenets of GitOps

### 2.1 Git as the Single Source of Truth
- Every environment (Development, Staging, Production) is represented as a branch or directory in a Git repository.
- Changes cannot be made by running ad-hoc `kubectl apply` commands directly on clusters.
- All modifications require Pull Requests (PRs), code reviews, security scans, and peer approval before merging.
- **Auditability & Rollback**: Every state transition has a cryptographic Git commit hash with author attribution. Rolling back an entire production release is as simple as running `git revert <commit-hash>`.

### 2.2 Declarative vs Imperative Configuration
- **Imperative**: Tells the system *how* to do something through steps (`kubectl run nginx`, `docker run -d -p 80:80 nginx`). If run twice, it may fail or produce side effects.
- **Declarative**: Tells the system *what* the end state should be (`kind: Deployment`, `replicas: 3`, `image: nginx:latest`). The system engine figures out the required transitions to reach that state.

### 2.3 Continuous Reconciliation Loop
A continuous feedback loop compares **Actual State** ($S_{\text{actual}}$) with **Desired State** ($S_{\text{desired}}$):

$$\Delta = S_{\text{desired}} - S_{\text{actual}}$$

- If $\Delta = 0$: System is **Synced** and **Healthy**.
- If $\Delta \neq 0$: System is **OutOfSync** (Configuration Drift).
  - With **Auto-Sync** and **Self-Healing** enabled, the GitOps controller executes reconciliation to converge $S_{\text{actual}} \rightarrow S_{\text{desired}}$.

---

## 3. GitOps Workflow

```
                                      CI / CD PIPELINE
 1. Developer Pushes Code
    +-----------------+        2. CI Builds & Tests
    | Developer Repo  | --------------------------> [ GitHub Actions / Jenkins ]
    +-----------------+                                       |
                                                              | 3. Push Container Image
                                                              v
                                                   +----------------------+
                                                   | Container Registry   |
                                                   | (Docker Hub / ECR)   |
                                                   +----------------------+
                                                              |
                               4. Update Manifest Tag         |
                                                              v
                                                   +----------------------+
                                                   | Config Repo (GitOps) |
                                                   | (Desired State)      |
                                                   +----------------------+
                                                              |
                                                              | 5. Pulls & Reconciles
                                                              v
                                              +-------------------------------+
                                              | In-Cluster GitOps Operator    |
                                              |       (Argo CD / Flux)        |
                                              +-------------------------------+
                                                              |
                                                              | 6. Applies Declarative
                                                              |    Manifests
                                                              v
                                              +-------------------------------+
                                              |    Kubernetes Cluster         |
                                              |    (Live Actual State)        |
                                              +-------------------------------+
```

### Traditional CI/CD (Push) vs GitOps (Pull)

| Feature | Traditional CI/CD (Push Model) | GitOps (Pull Model) |
| :--- | :--- | :--- |
| **Execution Trigger** | CI server pushes directly to cluster | In-cluster operator pulls changes from Git |
| **Cluster Access Keys** | CI pipeline requires cluster admin credentials | No outside credentials stored in CI server |
| **Firewall / Security** | Cluster API server must be open to CI agents | Inward-facing; operator pulls outbound via HTTPS |
| **Drift Management** | Blind to manual cluster modifications | Continuously detects and self-heals cluster drift |

---

## 4. Kubernetes + GitOps: The Perfect Match

Kubernetes was designed from its inception around a **declarative API model** and **control loops**:
1. Every Kubernetes resource is declared via YAML specifications (`spec`) and monitored via runtime status (`status`).
2. Kubernetes controllers (Deployment controller, ReplicaSet controller) are continuous reconciliation loops.
3. Adding a GitOps operator (Argo CD or Flux) extends Kubernetes' native reconciliation loop to bridge external Git repositories with internal cluster state.

---

## 5. GitOps Hands-on Demo Architecture (Argo CD)

### 5.1 Declarative Application Manifest (`gitops/app-manifests.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-web-app
  namespace: production
  labels:
    app: sample-web-app
    tier: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sample-web-app
  template:
    metadata:
      labels:
        app: sample-web-app
    spec:
      containers:
      - name: web
        image: nginx:1.25.3-alpine
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "250m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 2
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: sample-web-app-svc
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: sample-web-app
  ports:
  - port: 80
    targetPort: 80
    name: http
```

### 5.2 Argo CD Application Custom Resource (`gitops/argocd-application.yaml`)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: sample-web-app
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
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
    syncOptions:
      - CreateNamespace=true
```

### 5.3 Step-by-Step Execution Walkthrough

#### Step 1: Deploy Argo CD to Kubernetes Cluster
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

#### Step 2: Register the GitOps Application
```bash
kubectl apply -f gitops/argocd-application.yaml
```

#### Step 3: Drift Detection & Automated Self-Healing in Action
1. **Manual Drift Injection**: A developer attempts an unauthorized manual change in the cluster:
   ```bash
   kubectl scale deployment sample-web-app -n production --replicas=10
   ```
2. **GitOps Detection**: Within seconds, the Argo CD reconciliation controller detects a divergence between Git (`replicas: 3`) and the live cluster (`replicas: 10`).
3. **Self-Healing Enforcement**: Because `selfHeal: true` is configured, Argo CD automatically overrides the cluster state and scales the Deployment back down to `3` replicas, maintaining Git as the absolute authority.
