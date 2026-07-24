$Processes = Get-Process -Name "Easy CESU" -ErrorAction SilentlyContinue
if (-not $Processes) {
    Write-Host "Aucune application Easy CESU en cours."
    exit 0
}

foreach ($Process in $Processes) {
    Stop-Process -Id $Process.Id -Force
    Write-Host "Application Easy CESU arretee : $($Process.Id)"
}
