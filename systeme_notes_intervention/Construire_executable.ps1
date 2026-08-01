$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Version = (Get-Content -LiteralPath (Join-Path $Root "VERSION") -Raw).Trim()
$BuildVenv = Join-Path $Root ".build_venv"
$BuildPython = Join-Path $BuildVenv "Scripts\python.exe"
$EntryPoint = Join-Path $Root "application\desktop_app.py"
$IconPath = Join-Path $Root "application\assets\easy-cesu.ico"
$Dist = Join-Path $Root "dist"
$AppDist = Join-Path $Dist "Easy CESU"
$AppBuild = Join-Path $Root "build\application"
$Sorties = Join-Path $Root "sorties"
$Stamp = Get-Date -Format "yyyyMMdd_HHmm"
$ZipPath = Join-Path $Sorties "EasyCESU-Portable-x64-$Version-$Stamp.zip"
$NoticeGenerator = Join-Path $Root "generer_notice_pdf.py"
$IconGenerator = Join-Path $Root "generer_icone.py"
$NoticePdf = Join-Path $Root "output\pdf\Easy_CESU_V3_Notice_Installation_et_Utilisation.pdf"
$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

function Find-BasePython {
    if (Test-Path -LiteralPath $BundledPython) {
        return @($BundledPython)
    }
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($Python) {
        return @($Python.Source)
    }
    $Py = Get-Command py -ErrorAction SilentlyContinue
    if ($Py) {
        return @($Py.Source, "-3")
    }
    throw "Python est introuvable. Installe Python 3 pour construire l'executable."
}

New-Item -ItemType Directory -Path $Sorties -Force | Out-Null
if (-not [Environment]::Is64BitOperatingSystem -or -not [Environment]::Is64BitProcess) {
    throw "La construction doit être réalisée sous Windows x64."
}
if (Test-Path -LiteralPath $AppDist) {
    Remove-Item -LiteralPath $AppDist -Recurse -Force
}

if (Test-Path -LiteralPath $BuildPython) {
    & $BuildPython -c "import sys" *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Environnement de build invalide, reconstruction..."
        Remove-Item -LiteralPath $BuildVenv -Recurse -Force
    }
}

if (-not (Test-Path -LiteralPath $BuildPython)) {
    Write-Host "Creation de l'environnement de build..."
    $BasePython = @(Find-BasePython)
    if ($BasePython.Count -gt 1) {
        & $BasePython[0] $BasePython[1] -m venv $BuildVenv
    } else {
        & $BasePython[0] -m venv $BuildVenv
    }
}

Write-Host "Installation des dependances de build..."
& $BuildPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Echec de mise a jour de pip." }
& $BuildPython -m pip install -r (Join-Path $Root "requirements-build.txt")
if ($LASTEXITCODE -ne 0) { throw "Echec d'installation des dependances de build." }

Write-Host "Generation de l'icone Easy CESU..."
& $BuildPython $IconGenerator
if ($LASTEXITCODE -ne 0) { throw "Echec de generation de l'icone." }

Write-Host "Construction de l'executable..."
& $BuildPython -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --windowed `
    --name "Easy CESU" `
    --icon $IconPath `
    --distpath $Dist `
    --workpath $AppBuild `
    --specpath $AppBuild `
    --paths $Root `
    --hidden-import generer_notes_et_donnees `
    --add-data "$Root\application\static;application\static" `
    --collect-data reportlab `
    $EntryPoint
if ($LASTEXITCODE -ne 0) { throw "Echec de construction de l'executable." }

Write-Host "Generation de la notice PDF..."
& $BuildPython $NoticeGenerator
if ($LASTEXITCODE -ne 0) { throw "Echec de generation de la notice PDF." }
Copy-Item -LiteralPath $NoticePdf -Destination (Join-Path $AppDist "Easy_CESU_V3_Notice_Installation_et_Utilisation.pdf") -Force

$InstallerCmd = Join-Path $AppDist "Installer sur ce PC.cmd"
$InstallerPs1 = Join-Path $AppDist "installer_sur_ce_pc.ps1"
$UninstallCmd = Join-Path $AppDist "Desinstaller de ce PC.cmd"

@'
@echo off
setlocal
set "APP_DIR=%~dp0"
set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%POWERSHELL_EXE%" set "POWERSHELL_EXE=powershell.exe"
"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -File "%APP_DIR%installer_sur_ce_pc.ps1"
pause
'@ | Set-Content -LiteralPath $InstallerCmd -Encoding ASCII

@'
$ErrorActionPreference = "Stop"
$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
$Target = Join-Path $env:LOCALAPPDATA "Easy CESU"
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "Easy CESU.lnk"

New-Item -ItemType Directory -Path $Target -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $Source "*") -Destination $Target -Recurse -Force

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = Join-Path $Target "Easy CESU.exe"
$Shortcut.WorkingDirectory = $Target
$Shortcut.Save()

Write-Host "Application installee dans : $Target"
Write-Host "Raccourci cree sur le Bureau : $ShortcutPath"
'@ | Set-Content -LiteralPath $InstallerPs1 -Encoding UTF8

@'
@echo off
setlocal
set "TARGET=%LOCALAPPDATA%\Easy CESU"
if exist "%USERPROFILE%\Desktop\Easy CESU.lnk" del "%USERPROFILE%\Desktop\Easy CESU.lnk"
if exist "%TARGET%" rmdir /s /q "%TARGET%"
echo Application desinstallee.
pause
'@ | Set-Content -LiteralPath $UninstallCmd -Encoding ASCII

if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}

Compress-Archive -LiteralPath $AppDist -DestinationPath $ZipPath -Force
Write-Host "Executable : $(Join-Path $AppDist 'Easy CESU.exe')"
Write-Host "Package portable : $ZipPath"
