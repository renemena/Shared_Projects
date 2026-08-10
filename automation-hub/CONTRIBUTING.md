# Contributing Guide

Thank you for your interest in contributing to this repository.

This project is intended to be a collaborative environment for infrastructure automation across AWS, Azure, Kubernetes, and On-Premises environments.

## Ways to Contribute

You can contribute by:

- Adding automation projects
- Improving existing code
- Creating Terraform modules
- Adding Kubernetes manifests or Helm charts
- Developing Python or Java integrations
- Improving documentation
- Adding tests
- Reporting bugs
- Suggesting new features
- Improving security practices

## Recommended Workflow

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Commit using a descriptive message.
5. Push your branch.
6. Open a Pull Request.

Example:

```bash
git checkout -b feature/aws-vpc-module
git add .
git commit -m "feat: add reusable AWS VPC module"
git push origin feature/aws-vpc-module
```

## Branch Naming

Recommended prefixes:

```text
feature/
fix/
docs/
refactor/
test/
security/
```

Examples:

```text
feature/azure-vnet-module
fix/python-backup-timeout
docs/kubernetes-installation
security/remove-hardcoded-secret
```

## Commit Messages

Prefer clear and concise messages.

Examples:

```text
feat: add Azure VM deployment module
fix: handle SSH timeout in backup script
docs: add EKS deployment instructions
refactor: split network parser into modules
test: add Terraform validation workflow
security: remove hardcoded credentials
```

## Code Requirements

Before submitting a Pull Request:

- Do not include real credentials or secrets.
- Remove customer names and confidential data.
- Document prerequisites and dependencies.
- Add examples where practical.
- Test the implementation.
- Keep changes focused.
- Follow the existing directory structure.
- Prefer reusable and modular code.

## Project Documentation

Each significant project should include its own `README.md` describing:

- Purpose
- Architecture
- Requirements
- Dependencies
- Configuration
- Usage
- Examples
- Security considerations
- Known limitations

## Pull Requests

A Pull Request should explain:

- What is being changed
- Why the change is necessary
- How it was tested
- Potential operational impact
- Related Issue, if applicable

Large changes should preferably start with an Issue for discussion.
