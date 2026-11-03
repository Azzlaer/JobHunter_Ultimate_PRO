@echo off
cd /d "%~dp0"
set /p EXTID=ID de extension Chrome (32 letras): 
py -3 install_windows.py %EXTID%
pause
