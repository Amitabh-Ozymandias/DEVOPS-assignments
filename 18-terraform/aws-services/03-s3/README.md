# 03 - S3 (Simple Storage Service) — Storage

## What is S3?

Amazon S3 is **object storage** with virtually unlimited capacity, designed for **99.999999999% (11 nines) durability** and high availability. Data is accessed over HTTPS via the S3 API, CLI, SDKs or console.

Unlike a file system (EBS/EFS), S3 has no real folders or in-place edits — you store and retrieve **whole objects** identified by a key.

```text
  Region: ap-south-1
  └── Bucket: my-demo-bucket                (globally unique name)
      ├── Object: index.html                (key = "index.html")
      ├── Object: images/logo.png           (key = "images/logo.png")
      └── Object: logs/2026/10/07/app.log   ("/" is just part of the key)
```

## Buckets

A **bucket** is a container for objects.
- Name is **globally unique** across all AWS accounts, 3–63 chars, lowercase letters, numbers, hyphens, dots.
- Created in a **specific region** (data stays there unless you replicate it).
- Default limit of 10,000 buckets per account (raisable).
- Configuration lives at bucket level: versioning, encryption, policies, lifecycle, logging, replication, Block Public Access, static website hosting.

```bash
aws s3 mb s3://my-demo-bucket --region ap-south-1
aws s3 ls
```

## Objects

An **object** = data + metadata + key.

| Part | Description |
|---|---|
| Key | Full name/path, e.g. `images/logo.png` |
| Value | The data (0 bytes up to **5 TB**) |
| Version ID | If versioning is enabled |
| Metadata | System (Content-Type, size, ETag) and user-defined (`x-amz-meta-*`) |
| Tags | Up to 10 key-value pairs (used for lifecycle, access control, cost) |

- Single `PUT` up to 5 GB; use **multipart upload** for files > 100 MB (required > 5 GB).
- S3 provides **strong read-after-write consistency**.

```bash
aws s3 cp ./index.html s3://my-demo-bucket/
aws s3 sync ./site s3://my-demo-bucket/site
```

## Storage Classes

| Class | Use for | Availability Zones | Retrieval |
|---|---|---|---|
| **S3 Standard** | Frequently accessed data | ≥ 3 | Instant |
| **S3 Intelligent-Tiering** | Unknown/changing access patterns (auto-moves data) | ≥ 3 | Instant |
| **S3 Express One Zone** | Ultra-low latency, single-digit ms | 1 | Instant |
| **S3 Standard-IA** | Infrequent access, rapid when needed | ≥ 3 | Instant (retrieval fee) |
| **S3 One Zone-IA** | Re-creatable infrequent data | 1 | Instant (retrieval fee) |
| **S3 Glacier Instant Retrieval** | Archive accessed ~quarterly | ≥ 3 | Milliseconds |
| **S3 Glacier Flexible Retrieval** | Archive, occasional restores | ≥ 3 | Minutes – 12 hours |
| **S3 Glacier Deep Archive** | Long-term retention (7–10+ yrs) | ≥ 3 | 12 – 48 hours |

The colder the class, the cheaper the storage and the higher the retrieval cost/time.

## Versioning

**Versioning** keeps multiple variants of an object in the same bucket.
- States: *Unversioned* (default) → *Enabled* → *Suspended* (can't go back to unversioned).
- Every overwrite creates a new version ID; old versions are retained.
- A delete adds a **delete marker** instead of removing data — you can restore by deleting the marker.
- Protects against accidental overwrite/delete; required for **replication**.
- Combine with **MFA Delete** and **Object Lock** (WORM) for stronger protection.

```hcl
resource "aws_s3_bucket_versioning" "demo" {
  bucket = aws_s3_bucket.demo.id
  versioning_configuration { status = "Enabled" }
}
```

## Lifecycle Policies

**Lifecycle rules** automate moving or deleting objects to save cost.
- **Transition actions** — move objects to a cheaper class after N days.
- **Expiration actions** — delete objects (or old versions) after N days.
- Can filter by prefix and/or tags; can abort incomplete multipart uploads.

```json
{
  "Rules": [{
    "ID": "archive-logs",
    "Filter": { "Prefix": "logs/" },
    "Status": "Enabled",
    "Transitions": [
      { "Days": 30,  "StorageClass": "STANDARD_IA" },
      { "Days": 90,  "StorageClass": "GLACIER" }
    ],
    "Expiration": { "Days": 365 },
    "NoncurrentVersionExpiration": { "NoncurrentDays": 30 }
  }]
}
```

## Encryption

**In transit:** HTTPS/TLS (enforce with a bucket policy condition `aws:SecureTransport`).

**At rest** — all new objects are encrypted by default (SSE-S3) since January 2023:

| Option | Key managed by | Notes |
|---|---|---|
| **SSE-S3** | AWS (S3-managed AES-256) | Default, no cost |
| **SSE-KMS** | AWS KMS key (AWS or customer managed) | Audit via CloudTrail, key policies; use S3 Bucket Keys to cut KMS cost |
| **DSSE-KMS** | KMS, dual-layer | For strict compliance |
| **SSE-C** | Customer supplies the key per request | AWS doesn't store the key |
| **Client-side** | You encrypt before upload | Full control |

## Bucket Policies

A **bucket policy** is a **resource-based JSON policy** attached to a bucket, used to grant or deny access to principals (including other accounts or the public).

Example — deny any non-HTTPS request:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyInsecureTransport",
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": [
      "arn:aws:s3:::my-demo-bucket",
      "arn:aws:s3:::my-demo-bucket/*"
    ],
    "Condition": { "Bool": { "aws:SecureTransport": "false" } }
  }]
}
```

Related controls:
- **Block Public Access** — account/bucket-level safety switch (on by default) that overrides public policies/ACLs.
- **Object Ownership / ACLs** — ACLs are disabled by default (*Bucket owner enforced*); use policies instead.
- **IAM policies** — identity-based access to buckets.
- **Pre-signed URLs** — temporary access to a specific object.

## Common Use Cases

- Backup, restore and disaster recovery.
- Data lakes and analytics (Athena, EMR, Redshift Spectrum, Glue).
- Static website hosting (often behind CloudFront).
- Storing application assets: images, videos, user uploads.
- Log storage (CloudTrail, ALB, VPC Flow Logs).
- Long-term archive and compliance (Glacier, Object Lock).
- Software/artifact distribution, CI/CD artifacts.
- **Terraform remote state** backend (with locking).

## References

- https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html
- https://aws.amazon.com/s3/storage-classes/
