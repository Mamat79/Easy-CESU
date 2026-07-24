@echo off
setlocal
set "PROJECT_DIR=%~dp0systeme_notes_intervention"
set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%POWERSHELL_EXE%" set "POWERSHELL_EXE=powershell.exe"
"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_DIR%\Construire_installateur_windows.ps1"
pause
