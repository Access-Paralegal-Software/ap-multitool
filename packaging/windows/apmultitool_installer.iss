; apmultitool_installer.iss — Inno Setup script for APMultitool
; Designed for local/non-elevated installations by default, with optional PATH registration.

#define AppName "APMultitool"
#ifndef AppVersion
#define AppVersion "1.0.0"
#endif
#ifndef AppVersionSuffix
#define AppVersionSuffix "-beta1"
#endif
#define AppPublisher "Access Paralegal Systems"
#define AppURL "https://accessparalegal.com"
#define AppExeName "Access_Paralegal_Multitool.exe"
#define AppCliName "apmultitool.exe"

[Setup]
AppId={{D0DF16A3-78B1-40EA-B366-D0DF16A3DF53}}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}{#AppVersionSuffix}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription=APMultitool Windows Setup Installer
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
VersionInfoTextVersion=v{#AppVersion}{#AppVersionSuffix}
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName=Access Paralegal
DisableProgramGroupPage=yes
LicenseFile=..\..\dist\APMultitool_Bundle\LICENSE
OutputDir=..\..\dist
OutputBaseFilename=APMultitool_Setup_v{#AppVersion}{#AppVersionSuffix}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName} (Remove Only)

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "addtopath"; Description: "Add APMultitool to local environment PATH (recommended for CLI)"; GroupDescription: "System Integration:"; Flags: unchecked

[Files]
Source: "..\..\dist\APMultitool_Bundle\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{#AppName} CLI Help"; Filename: "{cmd}"; Parameters: "/k """"{app}\{#AppCliName}"""" --help"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
; Standard Add to PATH registry write (HKCU environment)
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName: "Path"; ValueData: "{olddata};{app}"; Flags: preservestringtype; Tasks: addtopath; Check: NeedsAddPath

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
#ifdef UNICODE
  #define AW "W"
#else
  #define AW "A"
#endif

const
  WM_SETTINGCHANGE = $001a;
  SMTO_ABORTIFHUNG = 2;

function SendMessageTimeout(hWnd: HWND; Msg: Cardinal; wParam: Longint; lParam: String; fuFlags: Cardinal; uTimeout: Cardinal; var lpdwResult: Longint): Longint;
  external 'SendMessageTimeout{#AW}@user32.dll stdcall';

// Check if app directory is already in user path
function NeedsAddPath(): Boolean;
var
  OldPath: String;
  AppPath: String;
begin
  if RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OldPath) then
  begin
    AppPath := ExpandConstant('{app}');
    // Normalize string searching: check with and without semi-colons
    Result := (Pos(AppPath, OldPath) = 0);
  end
  else
  begin
    Result := True;
  end;
end;

// Broadcast changes to active Windows shells
procedure BroadcastEnvironmentChange();
var
  ResultAddr: Longint;
begin
  SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, ResultAddr);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    BroadcastEnvironmentChange();
  end;
end;

// Clean up PATH entries on uninstallation
procedure CurUninstallStepChanged(UninstallStep: TUninstallStep);
var
  OldPath: String;
  AppPath: String;
  P: Integer;
begin
  if UninstallStep = usPostUninstall then
  begin
    if RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OldPath) then
    begin
      AppPath := ExpandConstant('{app}');
      
      // Look for AppPath surrounded by semicolons or at the ends
      P := Pos(';' + AppPath + ';', OldPath);
      if P > 0 then
      begin
        Delete(OldPath, P, Length(';' + AppPath));
        RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OldPath);
      end
      else
      begin
        P := Pos(';' + AppPath, OldPath);
        if P > 0 then
        begin
          Delete(OldPath, P, Length(';' + AppPath));
          RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OldPath);
        end
        else
        begin
          P := Pos(AppPath + ';', OldPath);
          if P > 0 then
          begin
            Delete(OldPath, P, Length(AppPath + ';'));
            RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OldPath);
          end
          else
          begin
            P := Pos(AppPath, OldPath);
            if P > 0 then
            begin
              Delete(OldPath, P, Length(AppPath));
              RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OldPath);
            end;
          end;
        end;
      end;
      
      // Update environment
      BroadcastEnvironmentChange();
    end;
  end;
end;
