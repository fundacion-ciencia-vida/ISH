@echo off
setlocal
cd /d "%~dp0"

call update-site.cmd
if errorlevel 1 exit /b 1

if "%ISH_SITE_HOST%"=="" set ISH_SITE_HOST=0.0.0.0
if "%ISH_SITE_PORT%"=="" set ISH_SITE_PORT=8080

echo Public site: http://127.0.0.1:%ISH_SITE_PORT%/
echo Listening on %ISH_SITE_HOST%:%ISH_SITE_PORT% ^(editor not required^)
python -S -m http.server %ISH_SITE_PORT% --bind %ISH_SITE_HOST% --directory "%CD%"
