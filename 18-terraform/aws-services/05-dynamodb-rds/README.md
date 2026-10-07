# 05 - DynamoDB & RDS — Database Services

AWS offers purpose-built databases. The two most common are **DynamoDB** (managed NoSQL) and **RDS** (managed relational).

---

# Part A — Amazon DynamoDB

## What is DynamoDB?

Amazon DynamoDB is a **fully managed, serverless, key-value and document NoSQL database** that delivers single-digit millisecond performance at any scale. There are no servers to patch or provision; data is automatically replicated across **3 AZs** in a region.

## NoSQL

**NoSQL** ("not only SQL") databases store data in non-tabular, flexible models instead of fixed relational schemas.

| | Relational (SQL) | NoSQL (DynamoDB) |
|---|---|---|
| Schema | Fixed, defined up front | Flexible, only keys are required |
| Data model | Tables with rows/columns, joins | Items (key-value / JSON documents), no joins |
| Scaling | Mostly vertical | Horizontal (partitioning) |
| Query language | SQL | API (`GetItem`, `Query`, `Scan`) / PartiQL |
| Design approach | Normalize, then query | Design around **access patterns** |

## Tables

A **table** is a collection of items. You define only the **primary key** when creating it; every other attribute is schemaless.

**Capacity modes:**
- **On-demand** — pay per request, no capacity planning (good for unpredictable traffic).
- **Provisioned** — set RCUs/WCUs, optionally with auto scaling (cheaper for steady traffic).

## Items

An **item** is a single record in a table (like a row), up to **400 KB**. Each item is uniquely identified by its primary key, and different items can have different attributes.

```json
{
  "CustomerId": "C1001",
  "OrderDate":  "2026-10-07",
  "OrderId":    "O-55321",
  "Total":      1499.50,
  "Items":      ["keyboard", "mouse"],
  "Shipped":    false
}
```

## Attributes

An **attribute** is a fundamental data element (like a column, but per item).

| Category | Types |
|---|---|
| Scalar | String (S), Number (N), Binary (B), Boolean (BOOL), Null |
| Document | List (L), Map (M) — nested up to 32 levels |
| Set | String Set (SS), Number Set (NS), Binary Set (BS) |

## Partition Key

The **partition key** (hash key) is the first part of the primary key.
- DynamoDB hashes its value to decide which **physical partition** stores the item.
- With a **simple primary key** (partition key only), it must be unique per item.
- Choose a **high-cardinality** key (e.g. `UserId`, `OrderId`) to spread load evenly and avoid "hot partitions".

## Sort Key

The **sort key** (range key) is the optional second part of a **composite primary key** (partition key + sort key).
- Items with the same partition key are stored together, ordered by sort key.
- The combination must be unique.
- Enables range queries: `begins_with`, `between`, `>`, `<`.

```text
Table: Orders   PK = CustomerId   SK = OrderDate
┌────────────┬────────────┬──────────┬────────┐
│ CustomerId │ OrderDate  │ OrderId  │ Total  │
├────────────┼────────────┼──────────┼────────┤
│ C1001      │ 2026-09-01 │ O-50001  │ 250    │
│ C1001      │ 2026-10-07 │ O-55321  │ 1499.5 │
│ C2002      │ 2026-10-05 │ O-54990  │ 89     │
└────────────┴────────────┴──────────┴────────┘
Query: CustomerId = "C1001" AND OrderDate BETWEEN "2026-09-01" AND "2026-10-31"
```

**Secondary indexes** add alternate query patterns:
- **GSI (Global Secondary Index)** — different partition + sort key, created any time.
- **LSI (Local Secondary Index)** — same partition key, different sort key, created only with the table.

**Other features:** DynamoDB Streams (change data capture), TTL (auto-expire items), Global Tables (multi-region active-active), PITR backups (up to 35 days), DAX (in-memory cache), transactions, encryption at rest by default.

## DynamoDB Use Cases

- Serverless backends (API Gateway + Lambda + DynamoDB).
- User profiles, sessions and shopping carts.
- Gaming leaderboards and player state.
- IoT and time-series event data.
- Ad-tech, real-time bidding, high-traffic retail.
- Metadata stores and Terraform state locking (legacy pattern).

---

# Part B — Amazon RDS (Relational Database Service)

## Relational Database

A **relational database** stores data in **tables** made of rows and columns with a **predefined schema**. Tables are linked through **primary and foreign keys**, queried with **SQL**, and support **ACID transactions** and **joins** — ideal for structured data with complex relationships.

**Amazon RDS** is a **managed** service that runs relational databases for you: AWS handles provisioning, OS and engine patching, backups, monitoring, failover and scaling, while you manage schema, queries and data.

## Supported Engines

| Engine | Notes |
|---|---|
| **Amazon Aurora** (MySQL- & PostgreSQL-compatible) | AWS-built, up to 5x MySQL / 3x PostgreSQL throughput, storage auto-grows to 128 TiB, Aurora Serverless v2 |
| **MySQL** | Popular open-source |
| **PostgreSQL** | Advanced open-source |
| **MariaDB** | MySQL fork |
| **Oracle** | BYOL or license included |
| **Microsoft SQL Server** | Express, Web, Standard, Enterprise |
| **IBM Db2** | Standard / Advanced |

## DB Instances

A **DB instance** is an isolated database environment running in the cloud — the basic building block of RDS.
- **Instance class** determines CPU/memory: e.g. `db.t4g.micro` (burstable), `db.m7g` (general), `db.r7g` (memory optimized).
- **Storage**: General Purpose SSD (`gp3`), Provisioned IOPS (`io1`/`io2`), with **storage auto scaling**.
- Lives in a **DB subnet group** (subnets across ≥ 2 AZs) in your VPC.
- Configured via **parameter groups** (engine settings) and **option groups**.
- Accessed via an **endpoint** DNS name, e.g. `mydb.abc123.ap-south-1.rds.amazonaws.com:3306`.

## Security

- **Network isolation**: run in **private subnets**, set *Publicly accessible = No*.
- **Security groups**: allow the DB port (3306/5432/…) only from the application's security group.
- **Encryption at rest** with KMS (covers storage, backups, snapshots, replicas) — must be enabled at creation.
- **Encryption in transit** with SSL/TLS.
- **Authentication**: master user, **IAM database authentication**, Kerberos/AD; store credentials in **AWS Secrets Manager** with automatic rotation.
- **Auditing/monitoring**: CloudTrail (API calls), CloudWatch, Enhanced Monitoring, Performance Insights, engine audit logs.

## Backups

| Type | How | Retention | Restore |
|---|---|---|---|
| **Automated backups** | Daily snapshot + transaction logs | 1–35 days (0 disables) | **Point-in-time recovery** to any second in the window (to a new instance) |
| **Manual snapshots** | User-initiated | Until you delete them | Restore to a new instance; can copy/share across regions/accounts |

Backups are stored in S3 (managed by AWS). **AWS Backup** can centralize backup policies.

## Multi-AZ

**Multi-AZ** provides **high availability and durability**:
- RDS keeps a **synchronous standby replica** in a different AZ.
- On failure (instance, AZ, storage) or during maintenance, RDS **automatically fails over** — the endpoint DNS points to the standby (typically 60–120 s).
- The standby **does not serve reads** (in the classic one-standby deployment).
- **Multi-AZ DB cluster** option: one writer + two readable standbys, faster failover.

## Read Replicas

**Read replicas** provide **read scalability**:
- **Asynchronous** replication from the primary.
- Up to 15 replicas (MySQL, MariaDB, PostgreSQL; Aurora up to 15 within a cluster).
- Each has its own endpoint — the application sends read traffic (reports, analytics) to replicas.
- Can be **same-region or cross-region** (also useful for DR).
- Can be **promoted** to a standalone database.

### Multi-AZ vs Read Replica

| | Multi-AZ | Read Replica |
|---|---|---|
| Main purpose | High availability / failover | Read scaling |
| Replication | Synchronous | Asynchronous |
| Serves reads? | No (classic standby) | Yes |
| Automatic failover | Yes | No (manual promotion) |
| Region | Same region | Same or cross-region |

## RDS Use Cases

- Web and mobile application backends (e-commerce, CMS, SaaS).
- Transactional (OLTP) systems: banking, orders, inventory, ERP/CRM.
- Applications needing complex queries, joins and strong consistency.
- Migrating on-premises Oracle/SQL Server/MySQL databases to AWS (with AWS DMS).
- Reporting with read replicas.

---

## DynamoDB vs RDS — When to Use Which?

| Choose **DynamoDB** when… | Choose **RDS** when… |
|---|---|
| Access patterns are known and key-based | You need ad-hoc SQL queries and joins |
| You need massive scale with consistent ms latency | Data is highly relational with constraints |
| You want serverless, zero administration | You need a specific engine (MySQL, PostgreSQL, Oracle…) |
| Schema changes often | Strong schema and complex transactions are required |
| Traffic is spiky / unpredictable | Existing app expects a relational database |

## References

- https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html
