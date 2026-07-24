$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$App = Join-Path $Root "application\app_server.py"
$Log = Join-Path $Root "application\application.log"
$ErrLog = Join-Path $Root "application\application.err.log"
$Port = if ($env:NOTES_APP_PORT) { $env:NOTES_APP_PORT } else { "8765" }

$LocalPython = Join-Path $Root ".venv\Scripts\python.exe"
$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$PythonExe = $null
if (Test-Path -LiteralPath $LocalPython) {
    $PythonExe = $LocalPython
} elseif (Test-Path -LiteralPath $BundledPython) {
    $PythonExe = $BundledPython
} else {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Python) {
        throw "Python est introuvable. Installe Python 3 puis lance Installer_dependances.bat."
    }
    $PythonExe = $Python.Source
}

& $PythonExe -c "import openpyxl, reportlab" 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "Dependances Python manquantes. Lance Installer_dependances.bat, puis relance l'application."
}

$Existing = Get-NetTCPConnection -LocalPort ([int]$Port) -State Listen -ErrorAction SilentlyContinue
if ($Existing) {
    Write-Host "Application deja disponible : http://127.0.0.1:$Port"
    exit 0
}

$QuotedApp = "`"$App`""
Start-Process -FilePath $PythonExe -ArgumentList $QuotedApp -WindowStyle Hidden -WorkingDirectory $Root -RedirectStandardOutput $Log -RedirectStandardError $ErrLog
Start-Sleep -Seconds 2

Write-Host "Application disponible : http://127.0.0.1:$Port"
Write-Host "Journal : $Log"
