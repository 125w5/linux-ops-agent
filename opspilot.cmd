@echo off
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set "BUN_CMD="
where bun >nul 2>nul
if %ERRORLEVEL%==0 set "BUN_CMD=bun"
if not defined BUN_CMD if exist "%USERPROFILE%\.bun\bin\bun.exe" set "BUN_CMD=%USERPROFILE%\.bun\bin\bun.exe"
if defined BUN_CMD (
  if exist "%~dp0apps\opspilot-cli\src\main.tsx" (
    "%BUN_CMD%" run "%~dp0apps\opspilot-cli\src\main.tsx" %*
    exit /b %ERRORLEVEL%
  )
)
python -m diag workbench --target localhost --mode readonly %*
