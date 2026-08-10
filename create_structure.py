from pathlib import Path
import argparse

DIRECTORIES = [
    "python/network-automation",
    "python/cloud-automation",
    "python/monitoring",
    "python/backup",
    "python/api-integrations",
    "java/APIs",
    "java/microservices",
    "java/integrations",
    "terraform/aws",
    "terraform/azure",
    "terraform/modules",
    "terraform/examples",
    "kubernetes/manifests",
    "kubernetes/helm",
    "kubernetes/aws-eks",
    "kubernetes/azure-aks",
    "kubernetes/on-premises",
    "scripts",
    "docs",
    "examples",
    "tests",
    ".github/ISSUE_TEMPLATE",
]

def create_structure(root_name: str) -> None:
    root = Path(root_name)

    for relative in DIRECTORIES:
        directory = root / relative
        directory.mkdir(parents=True, exist_ok=True)

        if relative != ".github/ISSUE_TEMPLATE":
            (directory / ".gitkeep").touch(exist_ok=True)

    print(f"Repository structure created at: {root.resolve()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create the Infrastructure Automation Hub directory structure."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default="automation-hub",
        help="Root directory name (default: automation-hub)",
    )
    args = parser.parse_args()
    create_structure(args.root)
