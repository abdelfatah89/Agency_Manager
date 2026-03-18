param(
    [Parameter(Mandatory=$true)][string]$RootPassword,
    [string]$Host = "127.0.0.1",
    [int]$Port = 3306,
    [string]$RootUser = "root",
    [string]$DbName = "konach_new",
    [string]$AppUser = "konach_app",
    [string]$AppPassword = "",
    [Parameter(Mandatory=$true)][string]$BootstrapScript
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BootstrapScript)) {
    throw "bootstrap_database.py not found: $BootstrapScript"
}

$python = Join-Path $PSScriptRoot "..\..\..\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$args = @(
    $BootstrapScript,
    "--root-host", $Host,
    "--root-port", "$Port",
    "--root-user", $RootUser,
    "--root-password", $RootPassword,
    "--db-name", $DbName,
    "--app-user", $AppUser
)

if ($AppPassword) {
    $args += @("--app-password", $AppPassword)
}

$proc = Start-Process -FilePath $python -ArgumentList $args -Wait -PassThru
if ($proc.ExitCode -ne 0) {
    throw "Database bootstrap failed with code $($proc.ExitCode)"
}

Write-Host "Database configured and schema initialized"
