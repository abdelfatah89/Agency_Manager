; Inno Setup template for KONACH production deployment with MariaDB bootstrap.
#define AppName "KONACH Agency Manager"
#define AppVersion "1.0.0"
#define AppExeName "KONACH.exe"

[Setup]
AppId={{9E3D5D19-49A5-4F35-9EA7-B5AFA3E2DD7B}
AppName={#AppName}
AppVersion={#AppVersion}
DefaultDirName={autopf}\KONACH
DefaultGroupName=KONACH
OutputDir=.
OutputBaseFilename=KONACH_Setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "..\..\..\dist\KONACH.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\..\sql\*"; DestDir: "{app}\sql"; Flags: recursesubdirs createallsubdirs
Source: "..\..\scripts\*.ps1"; DestDir: "{app}\installer_scripts"; Flags: ignoreversion
Source: "..\..\..\scripts\bootstrap_database.py"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\..\..\scripts\run_sql_migrations.py"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\..\..\scripts\run_sql_migrations_with_root.py"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\..\..\mariadb\mariadb-x64.msi"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Run]
; Install MariaDB silently (first install path). On upgrade, this should no-op if already installed.
Filename: "powershell.exe"; \
    Parameters: "-NoProfile -ExecutionPolicy Bypass -File \"{app}\installer_scripts\install_mariadb.ps1\" -MsiPath \"{tmp}\mariadb-x64.msi\" -RootPassword \"{code:GetDbRootPassword}\" -Port 3306"; \
    StatusMsg: "Installing MariaDB..."; Flags: runhidden waituntilterminated

; Configure DB + app user + run schema migrations.
Filename: "powershell.exe"; \
    Parameters: "-NoProfile -ExecutionPolicy Bypass -File \"{app}\installer_scripts\configure_app_database.ps1\" -RootPassword \"{code:GetDbRootPassword}\" -BootstrapScript \"{app}\scripts\bootstrap_database.py\""; \
    StatusMsg: "Configuring application database..."; Flags: runhidden waituntilterminated

; On upgrade, apply incremental SQL updates only.
Filename: "powershell.exe"; \
  Parameters: "-NoProfile -ExecutionPolicy Bypass -File \"{app}\installer_scripts\apply_sql_updates.ps1\" -MigrationScript \"{app}\scripts\run_sql_migrations_with_root.py\" -RootPassword \"{code:GetDbRootPassword}\""; \
    StatusMsg: "Applying SQL updates..."; Flags: runhidden waituntilterminated

Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DbRootPassword: String;

function GetDbRootPassword(Param: String): String;
begin
  Result := DbRootPassword;
end;

procedure InitializeWizard;
begin
  DbRootPassword := InputBox('Database Root Password', 'Enter MariaDB root password for setup/upgrade:', '');
end;
