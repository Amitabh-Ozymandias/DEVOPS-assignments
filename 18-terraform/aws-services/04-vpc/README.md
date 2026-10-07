# 04 - VPC (Virtual Private Cloud) — Networking

## What is VPC?

Amazon VPC is a **logically isolated virtual network** inside AWS where you launch resources (EC2, RDS, Lambda in VPC, load balancers…). You control the IP address range, subnets, routing, gateways and firewalls — just like a traditional data-center network.

- A VPC belongs to **one region** and spans **all AZs** in that region.
- Every region has a **default VPC** (with public subnets) for quick starts.
- You can create custom VPCs (default quota: 5 per region).

```text
 Region ap-south-1 ── VPC 10.0.0.0/16
 ┌──────────────────────────────────────────────────────────────────┐
 │        AZ ap-south-1a                    AZ ap-south-1b          │
 │ ┌───────────────────────────┐   ┌───────────────────────────┐    │
 │ │ Public subnet 10.0.1.0/24 │   │ Public subnet 10.0.2.0/24 │    │
 │ │  [ALB]  [NAT Gateway]     │   │  [ALB]                    │    │
 │ └───────────────────────────┘   └───────────────────────────┘    │
 │ ┌───────────────────────────┐   ┌───────────────────────────┐    │
 │ │Private subnet 10.0.11.0/24│   │Private subnet 10.0.12.0/24│    │
 │ │  [EC2 app]  [RDS]         │   │  [EC2 app]  [RDS standby] │    │
 │ └───────────────────────────┘   └───────────────────────────┘    │
 └───────────────────────────────┬──────────────────────────────────┘
                                 │
                        Internet Gateway ─── Internet
```

## CIDR

**CIDR (Classless Inter-Domain Routing)** notation defines an IP range: `10.0.0.0/16` = network address + prefix length.

| CIDR | Total IPs | Typical use |
|---|---|---|
| `/16` | 65,536 | Whole VPC (largest allowed) |
| `/20` | 4,096 | Large subnet |
| `/24` | 256 | Common subnet size |
| `/28` | 16 | Smallest allowed subnet |

Formula: number of IPs = 2^(32 − prefix).

- Use **private (RFC 1918)** ranges: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`.
- Plan ranges so they **don't overlap** with other VPCs or on-prem networks (needed for peering/VPN/Transit Gateway).
- You can add secondary CIDRs and IPv6 blocks later.
- AWS reserves **5 IPs in every subnet**: first 4 (network, VPC router, DNS, future use) and the last (broadcast). A `/24` gives 251 usable IPs.

## Subnets

A **subnet** is a range of IPs within the VPC, tied to **exactly one AZ**.
- Subnet CIDR must be a subset of the VPC CIDR and not overlap other subnets.
- Spread subnets across multiple AZs for high availability.
- Each subnet is associated with one route table and one network ACL.
- Whether a subnet is "public" or "private" depends on its **route table**, not a setting on the subnet itself.

## Route Tables

A **route table** contains rules (routes) that decide where network traffic from a subnet is sent.

| Destination | Target | Meaning |
|---|---|---|
| `10.0.0.0/16` | `local` | Traffic within the VPC (always present) |
| `0.0.0.0/0` | `igw-xxxx` | Internet traffic via Internet Gateway (public subnet) |
| `0.0.0.0/0` | `nat-xxxx` | Internet traffic via NAT Gateway (private subnet) |
| `pl-xxxx` (S3) | `vpce-xxxx` | S3 via gateway VPC endpoint |

- Every VPC has a **main route table**; subnets without explicit association use it.
- The **most specific route** (longest prefix match) wins.

## Internet Gateway

An **Internet Gateway (IGW)** is a horizontally scaled, highly available VPC component that enables communication between the VPC and the internet.
- One IGW per VPC.
- Performs 1:1 NAT for instances with public IPv4 addresses.
- Required for a subnet to be public: route `0.0.0.0/0 → IGW` **and** the instance needs a public/Elastic IP.
- No bandwidth limits and no hourly charge.

## NAT Gateway

A **NAT Gateway** lets instances in **private subnets** initiate **outbound** connections to the internet (e.g. OS updates, external APIs) while **blocking inbound** connections initiated from the internet.
- Deployed in a **public subnet** with an **Elastic IP**.
- Private subnet route: `0.0.0.0/0 → nat-gw`.
- Managed by AWS, scales automatically; it is **AZ-scoped**, so deploy one per AZ for HA.
- Charged per hour + per GB processed (a common cost surprise).
- Use **VPC endpoints** for S3/DynamoDB and other AWS services to avoid NAT data charges.

## Security Groups

A **security group** is a **stateful** firewall attached to an ENI (instance level).
- Allow rules only.
- Return traffic automatically allowed.
- All rules evaluated together.
- Can reference other security groups (e.g. "DB SG allows 3306 from App SG").

## Network ACLs

A **Network ACL (NACL)** is a **stateless** firewall at the **subnet** level.
- Supports **allow and deny** rules.
- Rules evaluated **in order by rule number** (lowest first); first match wins.
- **Stateless** — you must allow return traffic explicitly (ephemeral ports 1024–65535).
- Default NACL allows everything; a newly created custom NACL denies everything.

### Security Group vs Network ACL

| Feature | Security Group | Network ACL |
|---|---|---|
| Level | Instance / ENI | Subnet |
| State | **Stateful** | **Stateless** |
| Rules | Allow only | Allow and Deny |
| Evaluation | All rules together | In number order, first match |
| Applies to | Instances it's attached to | All instances in the subnet |
| Typical use | Primary access control | Extra layer, block specific IPs |

## Public vs Private Subnet

| | Public subnet | Private subnet |
|---|---|---|
| Route to internet | `0.0.0.0/0 → Internet Gateway` | `0.0.0.0/0 → NAT Gateway` (or none) |
| Inbound from internet | Possible (with public IP + SG rule) | Not possible |
| Outbound to internet | Directly via IGW | Via NAT Gateway only |
| Typical resources | Load balancers, NAT gateways, bastion hosts | App servers, databases, caches, internal services |

**Best practice:** put only internet-facing entry points in public subnets; keep application and data tiers private.

## Other VPC Features (good to know)

- **VPC Peering** / **Transit Gateway** — connect VPCs.
- **Site-to-Site VPN** / **Direct Connect** — connect on-premises networks.
- **VPC Endpoints** — private access to AWS services (Gateway: S3/DynamoDB; Interface: PrivateLink).
- **VPC Flow Logs** — capture IP traffic metadata for troubleshooting and security.

## References

- https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html
- https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
