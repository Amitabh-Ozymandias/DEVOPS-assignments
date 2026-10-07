# 01 - IAM (Identity and Access Management) — Governance

## What is IAM?

AWS Identity and Access Management (IAM) is a **global** AWS service that controls **who** (authentication) can do **what** (authorization) on **which** AWS resources. IAM is free to use and is the foundation of security for every AWS account.

When you create an AWS account you get a **root user** with unrestricted access. IAM lets you create identities with only the permissions they need, so the root user can be locked away.

```text
        Principal (who?)            Policy (what?)              Resource (which?)
  ┌───────────────────────┐   ┌──────────────────────┐   ┌──────────────────────────┐
  │ User / Group / Role   │──▶│ Allow s3:GetObject   │──▶│ arn:aws:s3:::my-bucket/* │
  └───────────────────────┘   └──────────────────────┘   └──────────────────────────┘
```

## Users

An **IAM user** represents a single person or application that interacts with AWS.

- Has a permanent identity in the account.
- Can have **console access** (username + password, ideally with MFA).
- Can have **programmatic access** (access key ID + secret access key) for the CLI/SDK.
- Has **no permissions by default** — permissions must be granted through policies.

```bash
aws iam create-user --user-name dev-alice
aws iam create-access-key --user-name dev-alice
```

## Groups

An **IAM group** is a collection of users. Policies attached to a group apply to every user in it.

- Simplifies permission management (e.g. `Developers`, `Admins`, `ReadOnly`).
- A user can belong to multiple groups (up to 10).
- Groups **cannot** be nested, and a group is not a principal (you can't log in as a group).

```bash
aws iam create-group --group-name Developers
aws iam add-user-to-group --group-name Developers --user-name dev-alice
```

## Roles

An **IAM role** is an identity with permissions but **no long-term credentials**. Anyone or anything that is trusted can *assume* the role and receive **temporary credentials** from AWS STS.

A role has two policies:

| Policy | Purpose |
|---|---|
| **Trust policy** | *Who* is allowed to assume the role (e.g. `ec2.amazonaws.com`, another account, a federated user) |
| **Permissions policy** | *What* the role can do once assumed |

Typical uses:
- An **EC2 instance profile** so an app on EC2 can read S3 without stored keys.
- A **Lambda execution role**.
- **Cross-account access** between AWS accounts.
- **Federation** (SSO / IAM Identity Center, GitHub Actions OIDC).

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "ec2.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
```

## Policies

A **policy** is a JSON document that defines permissions.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadDemoBucket",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-demo-bucket",
        "arn:aws:s3:::my-demo-bucket/*"
      ],
      "Condition": { "Bool": { "aws:SecureTransport": "true" } }
    }
  ]
}
```

| Element | Meaning |
|---|---|
| `Effect` | `Allow` or `Deny` |
| `Action` | API operations, e.g. `s3:PutObject`, `ec2:*` |
| `Resource` | ARNs the statement applies to |
| `Principal` | Who (only in resource-based / trust policies) |
| `Condition` | Optional constraints (IP, MFA, tags, time…) |

**Policy types**

- **AWS managed policies** — created by AWS (e.g. `AmazonS3ReadOnlyAccess`).
- **Customer managed policies** — created and versioned by you, reusable.
- **Inline policies** — embedded directly in one user/group/role.
- **Resource-based policies** — attached to a resource (S3 bucket policy, KMS key policy, SQS queue policy).
- **Permissions boundaries** — maximum permissions an identity can ever get.
- **Service Control Policies (SCPs)** — guardrails across accounts in AWS Organizations.
- **Session policies** — limit permissions for one assumed-role session.

## Permissions

How AWS evaluates a request:

```text
1. By default, everything is DENIED (implicit deny).
2. An explicit DENY anywhere → request DENIED.
3. Otherwise, an explicit ALLOW in an applicable policy → request ALLOWED.
4. No allow found → DENIED.
```

> **Explicit Deny always wins** over any Allow.

Permissions can be granted **identity-based** (attached to user/group/role) or **resource-based** (attached to the resource). For cross-account access, both sides usually need to allow the action.

## Least Privilege

The **principle of least privilege** means granting only the permissions required to perform a task — nothing more.

How to apply it:
- Start with minimal permissions and add as needed (not the other way round).
- Scope `Action` and `Resource` narrowly — avoid `"Action": "*"` and `"Resource": "*"`.
- Use **conditions** (source IP, MFA, tags, VPC endpoint).
- Use **IAM Access Analyzer** to generate policies from CloudTrail activity and find unused permissions.
- Review **last accessed** data and remove unused permissions regularly.

## IAM Best Practices

1. **Lock away the root user** — enable MFA, delete root access keys, use it only for the few tasks that require it.
2. **Enable MFA** for all human users.
3. **Use IAM Identity Center (SSO)** / federation for humans instead of long-lived IAM users.
4. **Use roles and temporary credentials** for workloads (EC2, Lambda, ECS, CI/CD via OIDC).
5. **Never hard-code or commit access keys**; rotate any keys that must exist.
6. **Grant least privilege** and use groups to assign permissions.
7. **Use a strong password policy.**
8. **Use permissions boundaries and SCPs** as guardrails.
9. **Monitor with CloudTrail**, IAM Access Analyzer and credential reports.
10. **Remove unused users, roles, keys and permissions.**

## Common Use Cases

| Use case | IAM feature |
|---|---|
| Give developers access to dev resources only | Group + customer managed policy |
| EC2 app reads from S3 without keys | IAM role + instance profile |
| Lambda writes to DynamoDB | Lambda execution role |
| CI/CD (GitHub Actions) deploys to AWS | OIDC identity provider + role |
| Access from another AWS account | Cross-account role with trust policy |
| Company SSO login to AWS | IAM Identity Center / SAML federation |
| Restrict whole accounts in an org | Service Control Policies |
| Terraform runs with limited rights | Dedicated role/user scoped to required services |

## References

- https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html
- https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
