# 02 - EC2 (Elastic Compute Cloud) — Compute

## What is EC2?

Amazon EC2 provides **resizable virtual servers (instances)** in the AWS cloud. You choose the operating system, CPU, memory, storage and networking, launch in minutes, and pay only for what you use.

EC2 is a **regional** service; each instance runs in a single **Availability Zone (AZ)** inside a VPC subnet.

```text
                         ┌──────────────── VPC ────────────────┐
  Internet ──▶ IGW ──▶   │  Subnet (AZ-a)                      │
                         │   ┌────────────────────────────┐    │
                         │   │ EC2 instance (from an AMI) │    │
                         │   │  ├─ Security Group         │    │
                         │   │  ├─ EBS root volume        │    │
                         │   │  └─ Key pair (SSH)         │    │
                         │   └────────────────────────────┘    │
                         └─────────────────────────────────────┘
```

## AMI (Amazon Machine Image)

An **AMI** is a template used to launch an instance. It contains:
- The OS and pre-installed software (e.g. Amazon Linux 2023, Ubuntu 24.04, Windows Server).
- Block device mapping (which EBS snapshots become volumes).
- Launch permissions (public, private, shared with accounts).

Sources: AWS-provided, **AWS Marketplace**, community AMIs, or **custom AMIs** you create from a configured instance ("golden image"). AMIs are region-specific but can be copied across regions.

## Instance Types

Instance types define the hardware. Naming: `m7g.large` → family `m`, generation `7`, attribute `g` (Graviton/ARM), size `large`.

| Family | Optimized for | Examples | Use cases |
|---|---|---|---|
| General purpose | Balanced CPU/memory | `t3`, `t4g`, `m7i`, `m7g` | Web servers, dev/test |
| Compute optimized | High CPU | `c7i`, `c7g` | Batch, gaming, HPC |
| Memory optimized | Large RAM | `r7i`, `x2idn` | In-memory DBs, caching |
| Storage optimized | High local I/O | `i4i`, `d3` | NoSQL, data warehousing |
| Accelerated computing | GPU / ML chips | `p5`, `g6`, `inf2`, `trn1` | ML training/inference |

`t` instances are **burstable** (CPU credits) — cheap for spiky, low-average workloads.

**Purchasing options:** On-Demand, Savings Plans / Reserved Instances (1–3 yr commitment, big discount), Spot Instances (up to ~90% off, can be interrupted), Dedicated Hosts/Instances.

## Key Pairs

A **key pair** (public + private key) is used to securely connect to instances.
- AWS stores the **public key** and injects it into the instance (`~/.ssh/authorized_keys`).
- You keep the **private key** (`.pem`) — AWS does not keep a copy.
- Linux: used for SSH. Windows: used to decrypt the Administrator password.

```bash
chmod 400 my-key.pem
ssh -i my-key.pem ec2-user@<public-ip>
```

Alternatives without opening port 22: **EC2 Instance Connect** and **SSM Session Manager**.

## Security Groups

A **security group** is a **stateful virtual firewall** at the instance (ENI) level.
- Only **allow** rules (no deny rules).
- **Stateful** — return traffic is automatically allowed.
- Inbound denied and outbound allowed by default.
- Sources can be CIDR blocks or **other security groups**.

| Type | Protocol | Port | Source |
|---|---|---|---|
| SSH | TCP | 22 | My IP (`203.0.113.10/32`) |
| HTTP | TCP | 80 | `0.0.0.0/0` |
| HTTPS | TCP | 443 | `0.0.0.0/0` |

## EBS (Elastic Block Store)

**EBS** provides persistent **network-attached block storage** for EC2.
- A volume lives in one AZ and is attached to an instance in the same AZ.
- Persists independently of the instance (unless "delete on termination" is set — default for root volumes).
- **Snapshots** are incremental backups stored in S3; used to restore or copy volumes across AZs/regions.
- Supports encryption with KMS.

| Volume type | Kind | Use |
|---|---|---|
| `gp3` / `gp2` | General-purpose SSD | Boot volumes, most workloads |
| `io2` / `io1` | Provisioned IOPS SSD | Critical databases |
| `st1` | Throughput HDD | Big data, logs |
| `sc1` | Cold HDD | Infrequent access |

**Instance store** is different: temporary disks physically attached to the host — data is lost when the instance stops/terminates.

## Public vs Private IP

| | Private IP | Public IP | Elastic IP |
|---|---|---|---|
| Reachable from | Inside the VPC (and peered/VPN networks) | Internet | Internet |
| Assigned | Always, from subnet CIDR | Optional, from AWS pool | Allocated to your account |
| Persists on stop/start | Yes | **No — changes** | Yes (static) |
| Cost | Free | Charged (public IPv4) | Charged |

A private IP stays with the instance for its lifetime. A public IP is released when an instance stops — use an **Elastic IP** (or better, a load balancer / DNS) when you need a stable address.

## Instance Lifecycle

```text
          launch
            │
            ▼
        ┌─────────┐   reboot    ┌───────────┐
        │ pending │────────────▶│  running  │◀──────┐
        └─────────┘             └───────────┘       │
                                  │       │         │ start
                           stop   │       │ terminate
                                  ▼       ▼         │
                           ┌──────────┐ ┌─────────────┐
                           │ stopping │ │shutting-down│
                           └──────────┘ └─────────────┘
                                  │            │
                                  ▼            ▼
                           ┌──────────┐ ┌────────────┐
                           │ stopped  │ │ terminated │
                           └──────────┘ └────────────┘
                                  └───────────┘ (start → pending)
```

| State | Billing for compute | Notes |
|---|---|---|
| `pending` | No | Booting |
| `running` | **Yes** | Ready to use |
| `stopping` / `stopped` | No (EBS still billed) | EBS data kept; public IP released |
| `hibernated` | No | RAM saved to EBS, faster resume |
| `shutting-down` / `terminated` | No | Permanent; root EBS deleted by default |

## Common Use Cases

- Hosting web applications and APIs.
- Application servers behind an **Elastic Load Balancer** with **Auto Scaling**.
- Dev/test environments and CI build agents.
- Batch processing, HPC and big-data jobs (often on Spot).
- ML training/inference on GPU instances.
- Self-managed databases or legacy apps (lift-and-shift migration).
- Bastion hosts / jump boxes.

## References

- https://docs.aws.amazon.com/ec2/
- https://aws.amazon.com/ec2/instance-types/
