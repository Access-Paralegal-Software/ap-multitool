# build_installer.ps1 - Windows installer build orchestrator
# Run from repository root: powershell -File packaging/windows/build_installer.ps1
param (
    [string]$AppVersion = "1.0.0",
    [string]$ReleaseChannel = "-beta1",
    [string]$SignCertThumbprint = "",
    [string]$SignPfxPath = "",
    [string]$SignPfxPassword = "",
    [string]$TimestampUrl = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"

if (-not $SignCertThumbprint) {
    $SignCertThumbprint = $env:APM_SIGN_CERT_THUMBPRINT
}
if (-not $SignPfxPath) {
    $SignPfxPath = $env:APM_SIGN_PFX_PATH
}
if (-not $SignPfxPassword) {
    $SignPfxPassword = $env:APM_SIGN_PFX_PASSWORD
}
if ($env:APM_SIGN_TIMESTAMP_URL) {
    $TimestampUrl = $env:APM_SIGN_TIMESTAMP_URL
}

function Get-SignToolPath {
    $candidates = @(
        "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe",
        "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe"
    )

    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    $cmd = Get-Command "signtool.exe" -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    return $null
}

function Get-SigningMode {
    if ($SignCertThumbprint) {
        return "thumbprint"
    }
    if ($SignPfxPath) {
        return "pfx"
    }
    return "unsigned"
}

function Invoke-SignArtifact {
    param (
        [string]$ArtifactPath,
        [string]$SignToolPath,
        [string]$SigningMode
    )

    if ($SigningMode -eq "unsigned") {
        Write-Host "Skipping signing for $ArtifactPath (unsigned mode)." -ForegroundColor Gray
        return
    }

    if (-not (Test-Path $ArtifactPath)) {
        throw "Cannot sign missing artifact: $ArtifactPath"
    }

    $args = @("sign", "/fd", "SHA256", "/tr", $TimestampUrl, "/td", "SHA256")
    if ($SigningMode -eq "thumbprint") {
        $args += @("/sha1", $SignCertThumbprint)
    } elseif ($SigningMode -eq "pfx") {
        $args += @("/f", $SignPfxPath)
        if ($SignPfxPassword) {
            $args += @("/p", $SignPfxPassword)
        }
    }
    $args += $ArtifactPath

    & $SignToolPath @args
    if ($LASTEXITCODE -ne 0) {
        throw "signtool failed for $ArtifactPath with exit code $LASTEXITCODE"
    }

    $signature = Get-AuthenticodeSignature -FilePath $ArtifactPath
    Write-Host ("Signature status for {0}: {1}" -f $ArtifactPath, $signature.Status) -ForegroundColor Green
    if ($signature.SignerCertificate) {
        Write-Host ("Signer subject: {0}" -f $signature.SignerCertificate.Subject) -ForegroundColor Green
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  APMultitool Windows Installer Compiler Pipeline" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$signingMode = Get-SigningMode
$signtoolPath = $null
if ($signingMode -ne "unsigned") {
    $signtoolPath = Get-SignToolPath
    if (-not $signtoolPath) {
        throw "Signing was requested, but signtool.exe was not found."
    }
}

Write-Host ("Build version: v{0}{1}" -f $AppVersion, $ReleaseChannel) -ForegroundColor Cyan
Write-Host ("Signing mode: {0}" -f $signingMode) -ForegroundColor Cyan

# 1. Trigger bundle preparation
Write-Host "[1/5] Preparing application distribution bundle..." -ForegroundColor Yellow
if (-not (Test-Path -Path "packaging/windows/prepare_bundle.ps1")) {
    throw "Could not find prepare_bundle.ps1 at packaging/windows/prepare_bundle.ps1."
}

& powershell -File packaging/windows/prepare_bundle.ps1
if ($LASTEXITCODE -ne 0) {
    throw "Bundle preparation failed."
}

# 2. Validate bundle outputs
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

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path -Path $file)) {
        $missingFiles += $file
        Write-Host "Missing required file: $file" -ForegroundColor Red
    } else {
        Write-Host "Verified file: $file" -ForegroundColor Green
    }
}

if ($missingFiles.Count -gt 0) {
    throw ("Bundle validation failed. Missing files: {0}" -f ($missingFiles -join ", "))
}

# 2.5 Sign bundle binaries when credentials are available
Write-Host "[2.5/5] Processing bundle signing..." -ForegroundColor Yellow
foreach ($exe in @("$bundleDir\Access_Paralegal_Multitool.exe", "$bundleDir\apmultitool.exe")) {
    Invoke-SignArtifact -ArtifactPath $exe -SignToolPath $signtoolPath -SigningMode $signingMode
}

# 3. Locate Inno Setup compiler
Write-Host "[3/5] Locating Inno Setup compiler (ISCC.exe)..." -ForegroundColor Yellow
$isccPath = $null
$candidates = @(
    "ISCC.exe",
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
    } elseif (Test-Path -Path $candidate) {
        $isccPath = $candidate
        break
    }
}

if (-not $isccPath) {
    throw "Inno Setup compiler (ISCC.exe) was not found in standard paths or Local AppData."
}
Write-Host "Found Inno Setup compiler at: $isccPath" -ForegroundColor Green

# 4. Compile installer
Write-Host "[4/5] Running Inno Setup compilation..." -ForegroundColor Yellow
$issScript = "packaging\windows\apmultitool_installer.iss"
if (-not (Test-Path -Path $issScript)) {
    throw "Could not find Inno Setup script at: $issScript."
}

& $isccPath "/DAppVersion=$AppVersion" "/DAppVersionSuffix=$ReleaseChannel" $issScript
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup compiler failed with exit code $LASTEXITCODE"
}
Write-Host "Inno Setup compilation finished successfully." -ForegroundColor Green

# 5. Sign installer, verify signatures, and generate checksum
Write-Host "[5/5] Generating release metadata & checksums..." -ForegroundColor Yellow
$setupExe = "dist\APMultitool_Setup_v${AppVersion}${ReleaseChannel}.exe"
if (-not (Test-Path -Path $setupExe)) {
    throw "Setup output file not found at: $setupExe"
}

Invoke-SignArtifact -ArtifactPath $setupExe -SignToolPath $signtoolPath -SigningMode $signingMode

$sha256 = (Get-FileHash -Path $setupExe -Algorithm SHA256).Hash
$sha256File = "dist\APMultitool_Setup_v${AppVersion}${ReleaseChannel}.exe.sha256"
$sha256 | Out-File -FilePath $sha256File -Encoding ascii

Write-Host "Created installer executable: $setupExe" -ForegroundColor Green
Write-Host "SHA256 checksum ($sha256) written to: $sha256File" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  APMultitool Windows Installer Build Completed!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
