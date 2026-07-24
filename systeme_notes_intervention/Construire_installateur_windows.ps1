$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Version = (Get-Content -LiteralPath (Join-Path $Root "VERSION") -Raw).Trim()
$BuildScript = Join-Path $Root "Construire_executable.ps1"
$BuildVenv = Join-Path $Root ".build_venv"
$BuildPython = Join-Path $BuildVenv "Scripts\python.exe"
$AppDist = Join-Path $Root "dist\Easy CESU"
$InstallerEntry = Join-Path $Root "installateur_windows.py"
$IconPath = Join-Path $Root "application\assets\easy-cesu.ico"
$ShortcutIcons = Join-Path $Root "application\assets\shortcut-icons"
$Sorties = Join-Path $Root "sorties"
$InstallerName = "EasyCESU-Setup-x64-$Version"
$InstallerExe = Join-Path $Sorties "$InstallerName.exe"
$InstallerBuild = Join-Path $Root "build\installateur"

Write-Host "Construction de l'application autonome..."
if (-not [Environment]::Is64BitOperatingSystem -or -not [Environment]::Is64BitProcess) {
    throw "La construction doit être réalisée sous Windows x64."
}
& $BuildScript
if ($LASTEXITCODE -ne 0) { throw "Echec de construction de l'application autonome." }

if (-not (Test-Path -LiteralPath $BuildPython)) {
    throw "Environnement de build introuvable : $BuildPython"
}
if (-not (Test-Path -LiteralPath (Join-Path $AppDist "Easy CESU.exe"))) {
    throw "Application autonome introuvable : $AppDist"
}

Copy-Item -LiteralPath (Join-Path $Root "MODE_EMPLOI.md") -Destination (Join-Path $AppDist "MODE_EMPLOI.md") -Force

New-Item -ItemType Directory -Path $Sorties -Force | Out-Null
if (Test-Path -LiteralPath $InstallerExe) {
    Remove-Item -LiteralPath $InstallerExe -Force
}

Write-Host "Construction de l'installateur Windows..."
& $BuildPython -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name $InstallerName `
    --icon $IconPath `
    --distpath $Sorties `
    --workpath $InstallerBuild `
    --specpath $InstallerBuild `
    --add-data "$IconPath;." `
    --add-data "$ShortcutIcons;shortcut-icons" `
    --add-data "$AppDist;payload\Easy CESU" `
    $InstallerEntry
if ($LASTEXITCODE -ne 0) { throw "Echec de construction de l'installateur Windows." }

Write-Host "Installateur : $InstallerExe"
