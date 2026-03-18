param(
    [Parameter(Mandatory=$true)][string]$MsiPath,
    [Parameter(Mandatory=$true)][string]$RootPassword,
    [int]$Port = 3306,
    [string]$ServiceName = "MariaDB",
    [string]$DataDir = "C:\\ProgramData\\MariaDB\\data"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $MsiPath)) {
    throw "MariaDB MSI not found: $MsiPath"
}

$arguments = @(
    "/i",
    "`"$MsiPath`"",
    "/qn",
    "SERVICENAME=$ServiceName",
    "PASSWORD=$RootPassword",
    "PORT=$Port",
    "DATADIR=`"$DataDir`""
)

$process = Start-Process -FilePath "msiexec.exe" -ArgumentList $arguments -Wait -PassThru
if ($process.ExitCode -ne 0) {
    throw "MariaDB silent install failed with code $($process.ExitCode)"
}

Set-Service -Name $ServiceName -StartupType Automatic
Start-Service -Name $ServiceName
Write-Host "MariaDB installed and service started: $ServiceName"
