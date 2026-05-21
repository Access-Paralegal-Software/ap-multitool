# prepare_bundle.ps1 - Prepare the APMultitool installer folder layout
# Run from repository root: powershell -File packaging/windows/prepare_bundle.ps1

$version = python -c "from core import __version__, __channel__; print(f'v{__version__}{__channel__}')" 2>$null
if (-not $version) {
    $version = "v1.0.0-beta1"
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  APMultitool Windows Installer-Ready Bundler" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Paths
$bundleDir = "dist\APMultitool_Bundle"
$distDir = "dist"

# 2. Rebuild binaries
Write-Host "[1/3] Triggering clean PyInstaller build pipeline..." -ForegroundColor Yellow
if (Test-Path -Path $bundleDir) {
    Remove-Item -Path $bundleDir -Recurse -Force
}

# Run build_windows script to generate individual binaries
& powershell -File scripts/build_windows.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller compilation failed, aborting bundler script."
    Exit $LASTEXITCODE
}

# 3. Create bundle layout
Write-Host "[2/3] Preparing unified bundle directory at '$bundleDir'..." -ForegroundColor Yellow
New-Item -Path $bundleDir -ItemType Directory -Force | Out-Null

# Copy main executables
$guiExe = "$distDir\Access_Paralegal_Multitool.exe"
$cliExe = "$distDir\apmultitool.exe"

if (-not (Test-Path -Path $guiExe) -or -not (Test-Path -Path $cliExe)) {
    Write-Error "One or more compiled binaries are missing in dist/ folder. Aborting."
    Exit 1
}

Copy-Item -Path $guiExe -Destination $bundleDir
Copy-Item -Path $cliExe -Destination $bundleDir

# Copy GUI assets
Copy-Item -Path "logo_small.png" -Destination $bundleDir
Copy-Item -Path "water_texture.png" -Destination $bundleDir

# Create a draft LICENSE file
$licenseContent = @"
Access Paralegal Multitool License
Copyright (c) 2026 Access Paralegal Systems

Redistribution and use in binary form, without modification, are permitted
solely for local internal operations of Access Paralegal and related entities.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
"@
$licenseContent | Out-File -FilePath "$bundleDir\LICENSE" -Encoding utf8

# 4. Generate README/Handoff for the bundle
Write-Host "[3/3] Creating bundle guides and launchers..." -ForegroundColor Yellow

$readmeContent = @"
========================================================================
APMultitool Windows Application Bundle
========================================================================

This folder contains a fully self-contained distribution of APMultitool
including both the Desktop GUI and the Command Line Interface (CLI).

Build Version:
- $version

LAUNCHING:
- GUI App: Double-click 'Access_Paralegal_Multitool.exe'
- CLI App: Open cmd/powershell in this folder and run './apmultitool'

DISTRIBUTION AND INSTALLER NEXT STEPS:
To create a true, user-friendly installer (.exe/.msi), configure Inno Setup
(or WiX) to compile this directory structure:
1. Target Install Location: C:\Users\<Username>\AppData\Local\Programs\APMultitool
2. Shortcuts: Link to 'Access_Paralegal_Multitool.exe'
3. Registry / PATH integration: Add the directory to user environment variable PATH.
"@
$readmeContent | Out-File -FilePath "$bundleDir\README_BUNDLE.txt" -Encoding utf8

# Create a test CLI launcher batch file for convenience
$batContent = '@echo off' + "`r`n" + 'cmd /k "%~dp0apmultitool.exe" --help'
$batContent | Out-File -FilePath "$bundleDir\launch_cli_help.bat" -Encoding ascii

Write-Host "OK Unified Bundle prepared successfully at: $bundleDir" -ForegroundColor Green
Write-Host "Structure inside bundle:" -ForegroundColor Cyan
Get-ChildItem -Path $bundleDir | Select-Object Name, Length | Format-Table | Out-String | Write-Host
Write-Host "==========================================================" -ForegroundColor Cyan
