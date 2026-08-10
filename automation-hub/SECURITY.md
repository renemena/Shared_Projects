# Security Policy

Security is a core requirement of this repository.

## Never Commit Secrets

Do not commit:

- Passwords
- API tokens
- AWS Access Keys
- Azure credentials
- Private keys
- SSH private keys
- VPN pre-shared keys
- Certificates containing private keys
- Production configuration files with sensitive information
- Customer or company confidential data

Use placeholders instead:

```text
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AZURE_CLIENT_ID=<your-client-id>
AZURE_TENANT_ID=<your-tenant-id>
DEVICE_PASSWORD=<your-password>
API_TOKEN=<your-token>
```

## Recommended Secret Handling

Prefer:

- Environment variables
- AWS IAM Roles
- Azure Managed Identities
- Azure Key Vault
- AWS Secrets Manager
- Kubernetes Secrets integrated with a secure secret manager
- CI/CD secret stores

## Reporting a Vulnerability

Do not publish sensitive vulnerability details in a public Issue.

If GitHub Private Vulnerability Reporting is enabled, use it.

Otherwise, contact the repository maintainers privately through the available repository contact channel.

Include:

- Affected component
- Impact
- Reproduction steps
- Suggested remediation, if known

## Infrastructure Safety

Terraform plans, Kubernetes manifests, and automation scripts can modify or delete infrastructure.

Always validate changes in laboratory, development, or staging environments before production deployment.
