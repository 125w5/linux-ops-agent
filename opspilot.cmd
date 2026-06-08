@echo off
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set "PYTHONPATH=%~dp0"
if defined CONDA_PREFIX if exist "%CONDA_PREFIX%\python.exe" set "OPSPILOT_PYTHON=%CONDA_PREFIX%\python.exe"
if not defined OPSPILOT_PYTHON set "OPSPILOT_PYTHON=python"
set "BUN_CMD="
where bun >nul 2>nul
if %ERRORLEVEL%==0 set "BUN_CMD=bun"
if not defined BUN_CMD if exist "%USERPROFILE%\.bun\bin\bun.exe" set "BUN_CMD=%USERPROFILE%\.bun\bin\bun.exe"
if defined BUN_CMD (
  if exist "%~dp0apps\opspilot-cli\src\main.tsx" (
    "%BUN_CMD%" run "%~dp0apps\opspilot-cli\src\main.tsx" %*
    if "%~1"=="--smoke" exit /b %ERRORLEVEL%
    if %ERRORLEVEL% EQU 0 exit /b 0
    echo Bun frontend failed with exit code %ERRORLEVEL%, falling back to Python workbench. 1>&2
  )
)
"%OPSPILOT_PYTHON%" -m diag workbench --target localhost --mode readonly %*
