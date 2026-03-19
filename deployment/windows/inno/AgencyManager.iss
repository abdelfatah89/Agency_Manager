; Inno Setup template for KONACH production deployment.
; MySQL server setup is manual (AppServ-managed).
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
Source: "..\..\..\dist\KONACH\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion
Source: "..\..\..\sql\*"; DestDir: "{app}\sql"; Flags: recursesubdirs createallsubdirs
Source: "..\..\..\.env.example"; DestDir: "{app}\config"; DestName: ".env.example"; Flags: ignoreversion

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
