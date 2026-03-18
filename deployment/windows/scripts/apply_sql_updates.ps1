param(
    [Parameter(Mandatory=$true)][string]$MigrationScript,
    [Parameter(Mandatory=$true)][string]$RootPassword,
    [string]$Host = "127.0.0.1",
    [int]$Port = 3306,
    [string]$User = "root",
    [string]$DbName = "konach_new"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $MigrationScript)) {
    throw "Migration script not found: $MigrationScript"
}

$python = Join-Path $PSScriptRoot "..\..\..\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$args = @(
    $MigrationScript,
    "--host", $Host,
    "--port", "$Port",
    "--user", $User,
    "--password", $RootPassword,
    "--db-name", $DbName
)

$proc = Start-Process -FilePath $python -ArgumentList $args -Wait -PassThru
if ($proc.ExitCode -ne 0) {
    throw "SQL migration update failed with code $($proc.ExitCode)"
}

Write-Host "SQL updates applied successfully"
