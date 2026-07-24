$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $Root
$Sorties = Join-Path $Root "sorties"
$Stamp = Get-Date -Format "yyyyMMdd_HHmm"
$PackageName = "Easy_CESU_portable_$Stamp.zip"
$PackagePath = Join-Path $Sorties $PackageName
$TempRoot = Join-Path $env:TEMP "Easy_CESU_package_$Stamp"
$Stage = Join-Path $TempRoot "Easy CESU"

if (Test-Path -LiteralPath $TempRoot) {
    Remove-Item -LiteralPath $TempRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $Stage -Force | Out-Null
New-Item -ItemType Directory -Path $Sorties -Force | Out-Null

Copy-Item -LiteralPath (Join-Path $ProjectRoot "Ouvrir Easy CESU.cmd") -Destination $Stage -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "Installer Easy CESU.cmd") -Destination $Stage -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "Construire installateur Easy CESU.cmd") -Destination $Stage -Force
Copy-Item -LiteralPath $Root -Destination $Stage -Recurse -Force

$CopiedApp = Join-Path $Stage "systeme_notes_intervention"
$RemovePaths = @(
    (Join-Path $CopiedApp ".venv"),
    (Join-Path $CopiedApp ".build_venv"),
    (Join-Path $CopiedApp "build"),
    (Join-Path $CopiedApp "__pycache__"),
    (Join-Path $CopiedApp "application\__pycache__"),
    (Join-Path $CopiedApp "application\application.log"),
    (Join-Path $CopiedApp "application\application.err.log"),
    (Join-Path $CopiedApp "Easy CESU.spec")
)

foreach ($Path in $RemovePaths) {
    if (Test-Path -LiteralPath $Path) {
        Remove-Item -LiteralPath $Path -Recurse -Force
    }
}

$CopiedSorties = Join-Path $CopiedApp "sorties"
if (Test-Path -LiteralPath $CopiedSorties) {
    Get-ChildItem -LiteralPath $CopiedSorties -Filter "Easy_CESU*_*.zip" -File -ErrorAction SilentlyContinue |
        Remove-Item -Force
}

if (Test-Path -LiteralPath $PackagePath) {
    Remove-Item -LiteralPath $PackagePath -Force
}

Compress-Archive -LiteralPath $Stage -DestinationPath $PackagePath -Force
Remove-Item -LiteralPath $TempRoot -Recurse -Force

Write-Host "Package cree : $PackagePath"
