@echo off
setlocal
set "ROOT=%~dp0"
set "VENV=%ROOT%.ish-editor\venv"

if not exist "%VENV%\Scripts\python.exe" (
  where py >nul 2>nul
  if errorlevel 1 (
    python -m venv "%VENV%"
  ) else (
    py -3 -m venv "%VENV%"
  )
  if errorlevel 1 exit /b 1
  "%VENV%\Scripts\python.exe" -m pip install --upgrade pip
  "%VENV%\Scripts\python.exe" -m pip install -r "%ROOT%editor\requirements.txt"
)

if not exist "%ROOT%editor\ui\dist\index.html" (
  pushd "%ROOT%editor\ui"
  call npm ci
  if errorlevel 1 exit /b 1
  call npm run build
  if errorlevel 1 exit /b 1
  popd
)

"%VENV%\Scripts\python.exe" -m editor.launcher --workspace "%ROOT%" %*
