$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $Root ".venv"
$VenvPython = Join-Path $Venv "Scripts\python.exe"
$Requirements = Join-Path $Root "requirements.txt"

function Invoke-BasePython {
    param([string[]]$Arguments)
    if ($script:UsePyLauncher) {
        & $script:PyLauncher -3 @Arguments
    } else {
        & $script:PythonExe @Arguments
    }
}

$script:UsePyLauncher = $false
$script:PyLauncher = $null
$script:PythonExe = $null

$Py = Get-Command py -ErrorAction SilentlyContinue
if ($Py) {
    $script:UsePyLauncher = $true
    $script:PyLauncher = $Py.Source
} else {
    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($Python) {
        $script:PythonExe = $Python.Source
    }
}

if (-not $script:UsePyLauncher -and -not $script:PythonExe) {
    Write-Host "Python est introuvable."
    Write-Host "Installe Python 3 depuis https://www.python.org/downloads/windows/ puis relance ce fichier."
    Start-Process "https://www.python.org/downloads/windows/"
    exit 1
}

if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Host "Creation de l'environnement Python local..."
    Invoke-BasePython -Arguments @("-m", "venv", $Venv)
}

Write-Host "Mise a jour de pip..."
& $VenvPython -m pip install --upgrade pip

Write-Host "Installation des dependances..."
& $VenvPython -m pip install -r $Requirements

Write-Host ""
Write-Host "Installation terminee."
Write-Host "Tu peux lancer l'application avec : Lancer Notes Intervention.bat"
