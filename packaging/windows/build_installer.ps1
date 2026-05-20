# build_installer.ps1 — Windows Installer Build Orchestrator
# Run from repository root: powershell -File packaging/windows/build_installer.ps1
param (
    [string]$AppVersion = "1.0.0",
    [string]$ReleaseChannel = "-alpha1",
    [string]$SignCertThumbprint = ""
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  APMultitool Windows Installer Compiler Pipeline" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Trigger Bundle Preparation
Write-Host "[1/5] Preparing application distribution bundle..." -ForegroundColor Yellow
if (-not (Test-Path -Path "packaging/windows/prepare_bundle.ps1")) {
    Write-Error "Could not find prepare_bundle.ps1 at packaging/windows/prepare_bundle.ps1. Aborting."
    Exit 1
}

& powershell -File packaging/windows/prepare_bundle.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Error "Bundle preparation failed. Aborting installer compilation."
    Exit $LASTEXITCODE
}

# 2. Validate Bundle Outputs
Write-Host "[2/5] Validating bundle files..." -ForegroundColor Yellow
$bundleDir = "dist\APMultitool_Bundle"
$requiredFiles = @(
    "$bundleDir\Access_Paralegal_Multitool.exe",
    "$bundleDir\apmultitool.exe",
    "$bundleDir\logo_small.png",
    "$bundleDir\water_texture.png",
    "$bundleDir\LICENSE",
    "$bundleDir\README_BUNDLE.txt"
)

$missingCount = 0
foreach ($file in $requiredFiles) {
    if (-not (Test-Path -Path $file)) {
        Write-Host "❌ Missing required file: $file" -ForegroundColor Red
        $missingCount++
    } else {
        Write-Host "✅ Verified file: $file" -ForegroundColor Green
    }
}

if ($missingCount -gt 0) {
    Write-Error "Bundle validation failed. Missing $missingCount files. Aborting."
    Exit 1
}
Write-Host "Bundle validation completed successfully." -ForegroundColor Green

# 2.5. Pre-Installer Codesigning Hook
if ($SignCertThumbprint) {
    Write-Host "[2.5/5] Executing Codesigning on Bundle Binaries..." -ForegroundColor Yellow
    $signtoolPath = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe"
    if (Test-Path $signtoolPath) {
        foreach ($exe in @("$bundleDir\Access_Paralegal_Multitool.exe", "$bundleDir\apmultitool.exe")) {
            & $signtoolPath sign /sha1 $SignCertThumbprint /t http://timestamp.digicert.com /fd SHA256 $exe
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Signed: $exe" -ForegroundColor Green
            } else {
                Write-Host "❌ Failed to sign: $exe" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "⚠️ signtool.exe not found at standard path. Skipping pre-installer signing." -ForegroundColor Yellow
    }
} else {
    Write-Host "[2.5/5] Skipping Pre-Installer Codesigning (No cert thumbprint provided)" -ForegroundColor Gray
}

# 3. Locate Inno Setup Compiler (ISCC.exe)
Write-Host "[3/5] Locating Inno Setup compiler (ISCC.exe)..." -ForegroundColor Yellow
$isccPath = $null

# Candidate paths
$candidates = @(
    "ISCC.exe", # Check if in PATH
    "$env:LocalAppData\Programs\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)

foreach ($candidate in $candidates) {
    if ($candidate -eq "ISCC.exe") {
        $checkCmd = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
        if ($checkCmd) {
            $isccPath = $checkCmd.Source
            break
        }
    } else {
        if (Test-Path -Path $candidate) {
            $isccPath = $candidate
            break
        }
    }
}

if (-not $isccPath) {
    Write-Host "❌ Inno Setup compiler (ISCC.exe) was not found in standard paths or Local AppData." -ForegroundColor Red
    Write-Host "Please install Inno Setup 6 or add its folder to your system PATH." -ForegroundColor Yellow
    Write-Host "Installer compilation skipped, but bundle is prepared in: $bundleDir" -ForegroundColor Green
    Exit 2
}

Write-Host "✅ Found Inno Setup compiler at: $isccPath" -ForegroundColor Green

# 4. Compile Installer
Write-Host "[4/5] Running Inno Setup compilation..." -ForegroundColor Yellow
$issScript = "packaging\windows\apmultitool_installer.iss"

if (-not (Test-Path -Path $issScript)) {
    Write-Error "Could not find Inno Setup script at: $issScript. Aborting."
    Exit 1
}

# Run compiler with parameterized versioning
& $isccPath "/DAppVersion=$AppVersion" "/DAppVersionSuffix=$ReleaseChannel" $issScript

if ($LASTEXITCODE -ne 0) {
    Write-Error "Inno Setup compiler failed with exit code: $LASTEXITCODE"
    Exit $LASTEXITCODE
}

Write-Host "✅ Inno Setup compilation finished successfully!" -ForegroundColor Green

# 5. Locate Output, Sign, and Generate Checksum
Write-Host "[5/5] Generating release metadata & checksums..." -ForegroundColor Yellow
$setupExe = "dist\APMultitool_Setup_v${AppVersion}${ReleaseChannel}.exe"

if (-not (Test-Path -Path $setupExe)) {
    Write-Error "Setup output file not found at: $setupExe. Compilation might have failed silently."
    Exit 1
}

# Post-Installer Codesigning Hook
if ($SignCertThumbprint) {
    Write-Host "Executing Codesigning on final installer..." -ForegroundColor Yellow
    $signtoolPath = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe"
    if (Test-Path $signtoolPath) {
        & $signtoolPath sign /sha1 $SignCertThumbprint /t http://timestamp.digicert.com /fd SHA256 $setupExe
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Signed final installer: $setupExe" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to sign installer." -ForegroundColor Red
        }
    }
}

# Generate SHA256 checksum
$sha256 = (Get-FileHash -Path $setupExe -Algorithm SHA256).Hash
$sha256File = "dist\APMultitool_Setup_v${AppVersion}${ReleaseChannel}.exe.sha256"
$sha256 | Out-File -FilePath $sha256File -Encoding ascii

Write-Host "✅ Created Installer Executable: $setupExe" -ForegroundColor Green
Write-Host "✅ SHA256 Checksum ($sha256) written to: $sha256File" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  APMultitool Windows Installer Build Completed!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
