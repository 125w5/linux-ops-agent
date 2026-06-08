$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = $root
if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) {
    $env:OPSPILOT_PYTHON = Join-Path $env:CONDA_PREFIX "python.exe"
} elseif (-not $env:OPSPILOT_PYTHON) {
    $env:OPSPILOT_PYTHON = "python"
}
$bunCommand = Get-Command bun -ErrorAction SilentlyContinue
$bunPath = if ($bunCommand) { $bunCommand.Source } else { Join-Path $env:USERPROFILE ".bun/bin/bun.exe" }
if ((Test-Path $bunPath) -and (Test-Path (Join-Path $root "apps/opspilot-cli/src/main.tsx"))) {
    & $bunPath run (Join-Path $root "apps/opspilot-cli/src/main.tsx") @args
    if ($LASTEXITCODE -eq 0) { exit 0 }
    Write-Error "Bun frontend failed with exit code $LASTEXITCODE, falling back to Python workbench."
}
& $env:OPSPILOT_PYTHON -m diag workbench --target localhost --mode readonly @args
