@echo off
setlocal
set "PASTA=%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\ALBERTO.lnk'); $s.TargetPath=$env:ComSpec; $s.Arguments='/c ""' + $env:PASTA + 'INICIAR_ALBERTO.bat""'; $s.WorkingDirectory=$env:PASTA; $s.IconLocation='%SystemRoot%\System32\SHELL32.dll,13'; $s.Save()"
echo Atalho ALBERTO criado na area de trabalho.
pause
