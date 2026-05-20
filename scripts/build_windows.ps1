# build_windows.ps1 — Windows PyInstaller build automation script for APMultitool
# Run this from the repository root: powershell -File scripts/build_windows.ps1

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  APMultitool Windows Build Automation Pipeline" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check dependencies
Write-Host "[1/4] Checking Python environment & PyInstaller..." -ForegroundColor Yellow
$usePythonModule = $false
$pyinstallerCheck = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyinstallerCheck) {
    # Check if we can run via python -m PyInstaller
    & python -m PyInstaller --version 2>&1 | Out-Null
    if ($? -or $LASTEXITCODE -eq 0) {
        $usePythonModule = $true
        Write-Host "Found PyInstaller via 'python -m PyInstaller' module." -ForegroundColor Green
    } else {
        Write-Error "PyInstaller was not found in the current environment path or as a Python module. Please run 'pip install pyinstaller' first."
        Exit 1
    }
}

# 2. Clean build and dist caches
Write-Host "[2/4] Cleaning previous build caches..." -ForegroundColor Yellow
if (Test-Path -Path "build") {
    Remove-Item -Path "build" -Recurse -Force
}
if (Test-Path -Path "dist") {
    Remove-Item -Path "dist" -Recurse -Force
}
Write-Host "Build directories cleaned successfully." -ForegroundColor Green

# 3. Compile binaries using the spec file
Write-Host "[3/4] Running PyInstaller compilation..." -ForegroundColor Yellow
if ($usePythonModule) {
    & python -m PyInstaller ap_multitool.spec --noconfirm
} else {
    & pyinstaller ap_multitool.spec --noconfirm
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "PyInstaller completed compilation successfully!" -ForegroundColor Green
} else {
    Write-Error "PyInstaller compilation failed."
    Exit $LASTEXITCODE
}

# 4. Verify outputs
Write-Host "[4/4] Verifying build outputs..." -ForegroundColor Yellow
$guiExe = "dist/Access_Paralegal_Multitool.exe"
$cliExe = "dist/apmultitool.exe"

$allPassed = $true
if (Test-Path -Path $guiExe) {
    Write-Host "✅ Created GUI Executable: $guiExe" -ForegroundColor Green
} else {
    Write-Host "❌ GUI Executable Missing: $guiExe" -ForegroundColor Red
    $allPassed = $false
}

if (Test-Path -Path $cliExe) {
    Write-Host "✅ Created CLI Executable: $cliExe" -ForegroundColor Green
} else {
    Write-Host "❌ CLI Executable Missing: $cliExe" -ForegroundColor Red
    $allPassed = $false
}

Write-Host "==========================================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "  Build completed successfully! Binaries located in ./dist" -ForegroundColor Green
} else {
    Write-Host "  Build completed with missing outputs. Please check errors." -ForegroundColor Red
}
Write-Host "==========================================================" -ForegroundColor Cyan
