param(
    [int]$Annee = (Get-Date).Year,
    [int]$Mois = 0,
    [switch]$RemplacerNotes,
    [switch]$SansNotes,
    [string]$SortieNotes = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Config = Join-Path $Root "config.json"
$Sorties = Join-Path $Root "sorties"
$Json = Join-Path $Sorties ("donnees_interventions_{0}.json" -f $Annee)
$Xlsx = Join-Path $Sorties ("Bilan activite application {0}.xlsx" -f $Annee)

New-Item -ItemType Directory -Force -Path $Sorties | Out-Null

$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$PythonExe = $BundledPython
$PythonPrefixArgs = @()
if (-not (Test-Path -LiteralPath $PythonExe)) {
    $Py = Get-Command py -ErrorAction SilentlyContinue
    if ($Py) {
        $PythonExe = $Py.Source
        $PythonPrefixArgs = @("-3")
    } else {
        $Python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $Python) {
            throw "Python est introuvable. Installe Python 3 ou relance depuis Codex."
        }
        $PythonExe = $Python.Source
    }
}

$PythonArgs = @()
$PythonArgs += $PythonPrefixArgs
$PythonArgs += @(
    (Join-Path $Root "generer_notes_et_donnees.py"),
    "--config", $Config,
    "--year", $Annee
)
if ($Mois -gt 0) {
    $PythonArgs += @("--month", $Mois)
}
if ($RemplacerNotes) {
    $PythonArgs += "--replace"
}
if ($SansNotes) {
    $PythonArgs += "--no-pdf"
}
if ($SortieNotes -ne "") {
    $PythonArgs += @("--notes-output", $SortieNotes)
}

Write-Host "Lecture du suivi de paye et generation des notes..."
& $PythonExe @PythonArgs
if ($LASTEXITCODE -ne 0) {
    throw "La generation des donnees a echoue."
}

Write-Host "Creation du tableur de bilan..."
$ExportCode = @"
import json
import sys
from pathlib import Path

root = Path(r"$Root")
data_path = Path(r"$Json")
output_path = Path(r"$Xlsx")
sys.path.insert(0, str(root / "application"))

from excel_export import export_bilan_excel

payload = json.loads(data_path.read_text(encoding="utf-8"))
export_bilan_excel(payload, output_path, data_path)
"@
& $PythonExe @PythonPrefixArgs -c $ExportCode
if ($LASTEXITCODE -ne 0) {
    throw "La creation du tableur a echoue."
}

$InspectDump = "$Xlsx.inspect.ndjson"
if (Test-Path -LiteralPath $InspectDump) {
    Remove-Item -LiteralPath $InspectDump -Force
}

Write-Host ""
Write-Host "Termine."
Write-Host ("Tableur : {0}" -f $Xlsx)
Write-Host ("Donnees : {0}" -f $Json)
