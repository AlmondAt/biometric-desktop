$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$bundleRoot = Join-Path $projectRoot 'bundle\python-runtime'
$pythonHome = 'C:\Users\Den\AppData\Local\Programs\Python\Python310'
$targetPythonRoot = Join-Path $bundleRoot 'python'

if (Test-Path $bundleRoot) {
    Remove-Item $bundleRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $bundleRoot | Out-Null

if (-not (Test-Path (Join-Path $pythonHome 'python.exe'))) {
    throw "Python runtime tidak ditemukan di $pythonHome"
}

New-Item -ItemType Directory -Path $targetPythonRoot | Out-Null

Write-Host "Menyalin Python runtime dari $pythonHome ke $targetPythonRoot"
Copy-Item (Join-Path $pythonHome '*') $targetPythonRoot -Recurse -Force

Write-Host "Bundled Python runtime berhasil disalin ke $targetPythonRoot"