param(
    [string]$Root = "automation-hub"
)

$Directories = @(
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
    ".github/ISSUE_TEMPLATE"
)

Write-Host "Creating repository structure in: $Root"

foreach ($Directory in $Directories) {
    $Path = Join-Path $Root $Directory
    New-Item -ItemType Directory -Force -Path $Path | Out-Null

    if ($Directory -ne ".github/ISSUE_TEMPLATE") {
        New-Item -ItemType File -Force -Path (Join-Path $Path ".gitkeep") | Out-Null
    }
}

Write-Host "Structure created successfully."
Get-ChildItem -Path $Root -Directory -Recurse | Select-Object -ExpandProperty FullName
