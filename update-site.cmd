@echo off
setlocal
cd /d "%~dp0"

python -S scripts\build_site.py
if errorlevel 1 exit /b 1

python -S scripts\validate_site.py
if errorlevel 1 exit /b 1

echo Public site updated and validated in %CD%
