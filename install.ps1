$ErrorActionPreference = "Stop"

$python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Error "Python not found. Install Python 3."
    exit 1
}

$venv = ".venv"
if (-not (Test-Path $venv)) {
    & $python.Source -m venv $venv
}

$activate = Join-Path $venv "Scripts\Activate.ps1"
. $activate
$pip = Join-Path $venv "Scripts\pip.exe"

if (Test-Path "requirements.txt") {
    & $pip install -r requirements.txt
}

@'
#!/usr/bin/env pwsh
. .\.venv\Scripts\Activate.ps1

function DefaultIfEmpty($val, $def) {
    if ([string]::IsNullOrWhiteSpace($val)) { return $def } else { return $val }
}

Write-Host "Select quality:"
Write-Host "1) Low    - 480p15, fastest (-ql)"
Write-Host "2) Medium - 720p30, default (-qm)  [default]"
Write-Host "3) High   - 1080p60, slower (-qh)"
$q = Read-Host "Choice [1/2/3, default=2]"
$q = DefaultIfEmpty $q "2"
switch ($q) {
    "1" { $QUALITY = "-ql" }
    "2" { $QUALITY = "-qm" }
    "3" { $QUALITY = "-qh" }
    default { Write-Host "Invalid quality"; exit 1 }
}

$pv = Read-Host "Preview after render? (Y/n) [default=Y]"
$pv = DefaultIfEmpty $pv "Y"
if ($pv -match "^[Yy]$") { $PREVIEW = "-p" } else { $PREVIEW = "" }

Write-Host ""
Write-Host "Select animation(s):"
Write-Host "1) HypnoticLissajous"
Write-Host "2) PulseGrid"
Write-Host "3) SurfaceWave3D  [default]"
Write-Host "4) TextMorph"
Write-Host "a) All scenes"
$s = Read-Host "Choice [1/2/3/4/a, default=3]"
$s = DefaultIfEmpty $s "3"

if ($s -eq "a") {
    Write-Host "Rendering all scenes..."
    manim $PREVIEW $QUALITY -a main.py
} else {
    switch ($s) {
        "1" { $SCENE = "HypnoticLissajous" }
        "2" { $SCENE = "PulseGrid" }
        "3" { $SCENE = "SurfaceWave3D" }
        "4" { $SCENE = "TextMorph" }
        default { Write-Host "Invalid selection"; exit 1 }
    }
    Write-Host "Rendering $SCENE ..."
    manim $PREVIEW $QUALITY main.py $SCENE
}
'@ | Set-Content run.ps1 -Encoding UTF8

Write-Host "Install complete: run .\run.ps1 to start."