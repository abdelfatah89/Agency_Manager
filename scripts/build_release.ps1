param(
    [string]$ReleaseRoot = "release",
    [string]$Version = "1.0.0"
)

$ErrorActionPreference = "Stop"

function Invoke-And-Assert {
    param(
        [scriptblock]$Script,
        [string]$ErrorMessage
    )

    & $Script
    if ($LASTEXITCODE -ne 0) {
        throw "$ErrorMessage (exit code: $LASTEXITCODE)"
    }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot ".." )).Path
Set-Location $repoRoot

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

Write-Host "[1/5] Running compile checks..."
Invoke-And-Assert -Script { & $python -m compileall main.py services src scripts admin_license_tool } -ErrorMessage "Compile checks failed"

# Ensure old running EXEs do not lock target files during rebuild.
Get-Process -Name "KONACH" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "LicenseAdminTool" -ErrorAction SilentlyContinue | Stop-Process -Force

if (Test-Path (Join-Path $repoRoot "dist\KONACH.exe")) {
    Remove-Item -Path (Join-Path $repoRoot "dist\KONACH.exe") -Force -ErrorAction SilentlyContinue
}
if (Test-Path (Join-Path $repoRoot "dist\LicenseAdminTool.exe")) {
    Remove-Item -Path (Join-Path $repoRoot "dist\LicenseAdminTool.exe") -Force -ErrorAction SilentlyContinue
}

Write-Host "[2/5] Building main client EXE..."
Invoke-And-Assert -Script { & $python -m PyInstaller --clean --noconfirm AgencyManager.spec } -ErrorMessage "Main client EXE build failed"

Write-Host "[3/5] Building admin license tool EXE..."
Invoke-And-Assert -Script { & $python -m PyInstaller --clean --noconfirm LicenseAdminTool.spec } -ErrorMessage "Admin license tool EXE build failed"

$releasePath = Join-Path $repoRoot $ReleaseRoot
$clientPath = Join-Path $releasePath "client_app"
$adminPath = Join-Path $releasePath "admin_license_tool"
$installPath = Join-Path $clientPath "install"

Write-Host "[4/5] Preparing release folders..."
if (Test-Path $releasePath) {
    Remove-Item -Path $releasePath -Recurse -Force
}

$null = New-Item -ItemType Directory -Force -Path $clientPath
$null = New-Item -ItemType Directory -Force -Path $adminPath
$null = New-Item -ItemType Directory -Force -Path $installPath
$null = New-Item -ItemType Directory -Force -Path (Join-Path $clientPath "sql")
$null = New-Item -ItemType Directory -Force -Path (Join-Path $clientPath "config")
$null = New-Item -ItemType Directory -Force -Path (Join-Path $clientPath "logs")
$null = New-Item -ItemType Directory -Force -Path (Join-Path $adminPath "config")

Copy-Item -Path (Join-Path $repoRoot "dist\KONACH.exe") -Destination (Join-Path $clientPath "KONACH.exe")
Copy-Item -Path (Join-Path $repoRoot "dist\LicenseAdminTool.exe") -Destination (Join-Path $adminPath "LicenseAdminTool.exe")

Copy-Item -Path (Join-Path $repoRoot "deployment\windows\inno\AgencyManager.iss") -Destination $installPath
Copy-Item -Path (Join-Path $repoRoot "deployment\windows\scripts\*.ps1") -Destination $installPath
Copy-Item -Path (Join-Path $repoRoot "scripts\bootstrap_database.py") -Destination $installPath
Copy-Item -Path (Join-Path $repoRoot "scripts\run_sql_migrations.py") -Destination $installPath
Copy-Item -Path (Join-Path $repoRoot "scripts\run_sql_migrations_with_root.py") -Destination $installPath
Copy-Item -Path (Join-Path $repoRoot "sql\*.sql") -Destination (Join-Path $clientPath "sql")
Copy-Item -Path (Join-Path $repoRoot ".env.example") -Destination (Join-Path $clientPath "config\.env.example")
Copy-Item -Path (Join-Path $repoRoot "config\license_public_key.pem") -Destination (Join-Path $clientPath "config\license_public_key.pem")
Copy-Item -Path (Join-Path $repoRoot "admin_license_tool\requirements.txt") -Destination (Join-Path $adminPath "config\requirements.txt")
Copy-Item -Path (Join-Path $repoRoot "config\license_public_key.pem") -Destination (Join-Path $adminPath "config\license_public_key.pem")

Copy-Item -Path (Join-Path $repoRoot "release_assets\README_AR_EN.md") -Destination (Join-Path $clientPath "README_AR_EN.md")
Copy-Item -Path (Join-Path $repoRoot "release_assets\README_ADMIN_TOOL.md") -Destination (Join-Path $adminPath "README_ADMIN_TOOL.md")
Copy-Item -Path (Join-Path $repoRoot "release_assets\INSTALLATION_REPORT.md") -Destination (Join-Path $releasePath "INSTALLATION_REPORT.md")
Copy-Item -Path (Join-Path $repoRoot "release_assets\FINAL_GLOBAL_CHECK_REPORT.md") -Destination (Join-Path $releasePath "FINAL_GLOBAL_CHECK_REPORT.md")
Copy-Item -Path (Join-Path $repoRoot "release_assets\POST_INSTALL_VALIDATION_CHECKLIST.md") -Destination (Join-Path $releasePath "POST_INSTALL_VALIDATION_CHECKLIST.md")
Copy-Item -Path (Join-Path $repoRoot "release_assets\SQL_MIGRATION_UPDATE_STRATEGY.md") -Destination (Join-Path $releasePath "SQL_MIGRATION_UPDATE_STRATEGY.md")

Write-Host "[5/5] Writing release manifest..."
@"
KONACH Release Version: $Version
Generated At: $(Get-Date -Format o)
Client EXE: client_app/KONACH.exe
Admin EXE: admin_license_tool/LicenseAdminTool.exe
"@ | Set-Content -Path (Join-Path $releasePath "RELEASE_MANIFEST.txt") -Encoding UTF8

Write-Host "Release completed at: $releasePath"
