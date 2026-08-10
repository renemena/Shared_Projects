#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-automation-hub}"

DIRS=(
  "python/network-automation"
  "python/cloud-automation"
  "python/monitoring"
  "python/backup"
  "python/api-integrations"
  "java/APIs"
  "java/microservices"
  "java/integrations"
  "terraform/aws"
  "terraform/azure"
  "terraform/modules"
  "terraform/examples"
  "kubernetes/manifests"
  "kubernetes/helm"
  "kubernetes/aws-eks"
  "kubernetes/azure-aks"
  "kubernetes/on-premises"
  "scripts"
  "docs"
  "examples"
  "tests"
  ".github/ISSUE_TEMPLATE"
)

echo "Creating repository structure in: $ROOT"

for dir in "${DIRS[@]}"; do
  mkdir -p "$ROOT/$dir"
done

for dir in "${DIRS[@]}"; do
  case "$dir" in
    ".github/ISSUE_TEMPLATE") ;;
    *) touch "$ROOT/$dir/.gitkeep" ;;
  esac
done

echo "Structure created successfully."
echo
find "$ROOT" -type d | sort
