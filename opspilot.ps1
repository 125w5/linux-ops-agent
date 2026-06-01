$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$env:PYTHONIOENCODING = "utf-8"
$bunCommand = Get-Command bun -ErrorAction SilentlyContinue
$bunPath = if ($bunCommand) { $bunCommand.Source } else { Join-Path $env:USERPROFILE ".bun/bin/bun.exe" }
if ((Test-Path $bunPath) -and (Test-Path (Join-Path $root "apps/opspilot-cli/src/main.tsx"))) {
    & $bunPath run (Join-Path $root "apps/opspilot-cli/src/main.tsx") @args
    exit $LASTEXITCODE
}
python -m diag workbench --target localhost --mode demo @args
