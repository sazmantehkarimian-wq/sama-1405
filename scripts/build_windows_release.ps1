param(
  [string]$Version = "",
  [string]$OutputRoot = "build"
)
$ErrorActionPreference = "Stop"
if (-not $Version) { $Version = (Get-Content "VERSION" -Raw -Encoding utf8).Trim() }
if ($Version -notmatch '^5\.0\.0-uat\.\d+$') { throw "Unexpected UAT VERSION: $Version" }
$package = Join-Path $OutputRoot "SAMA_$Version"
if (Test-Path $package) { Remove-Item $package -Recurse -Force }
New-Item $package -ItemType Directory | Out-Null

# Zero-Data package boundary: application/runtime only. Authority source workbooks,
# import tooling, fixtures and sample data must never enter the LAN package.
$directories = @("core", "design_system", "domains", "queries", "reporting", "sama", "scripts", "services", "ui", "docs")
foreach ($directory in $directories) { Copy-Item $directory $package -Recurse }
$files = @("manage.py", "pyproject.toml", "README.md", "LEGACY_BOUNDARY.md", "VERSION", "START_SAMA.bat", "STOP_SAMA.bat")
foreach ($file in $files) { Copy-Item $file $package }
"Owner UAT build - ZERO DATA - manual entry only" | Set-Content (Join-Path $package "UAT_BUILD") -Encoding utf8NoBOM

New-Item (Join-Path $package "data") -ItemType Directory | Out-Null
Copy-Item "data/sama.sqlite3" (Join-Path $package "data/sama.sqlite3")
if (Test-Path "collected_static") { Copy-Item "collected_static" $package -Recurse }

# Fail closed if forbidden source/import artifacts accidentally enter the package.
$forbiddenDirectories = @("authority", "import_pipeline", "fixtures")
foreach ($name in $forbiddenDirectories) {
  if (Test-Path (Join-Path $package $name)) { throw "Forbidden Zero-Data package directory: $name" }
}
$forbiddenFiles = Get-ChildItem $package -Recurse -File | Where-Object {
  $_.Extension -in @('.xlsx','.xls','.csv','.zip') -or $_.Name -match 'fixture|sample[_-]?data|seed'
}
if ($forbiddenFiles) { throw "Forbidden data/import artifact in Zero-Data package: $($forbiddenFiles.FullName -join ', ')" }

$runtime = Join-Path $package "runtime"
$pythonZip = Join-Path $env:TEMP "python-3.11.9-embed-amd64.zip"
Invoke-WebRequest "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip" -OutFile $pythonZip
Expand-Archive $pythonZip $runtime
$pth = Join-Path $runtime "python311._pth"
@("python311.zip", ".", "Lib/site-packages", "..", "import site") | Set-Content $pth -Encoding ascii
$getPip = Join-Path $env:TEMP "get-pip.py"
Invoke-WebRequest "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPip
& (Join-Path $runtime "python.exe") $getPip --no-warn-script-location
if ($LASTEXITCODE -ne 0) { throw "Portable Python bootstrap failed" }
& (Join-Path $runtime "python.exe") -m pip install --no-warn-script-location --no-cache-dir --target (Join-Path $runtime "Lib/site-packages") `
  Django==5.2.7 openpyxl==3.1.5 python-docx==1.2.0 reportlab==4.4.4 jdatetime==5.2.0 waitress==3.0.2 Pillow==11.3.0 whitenoise==6.11.0 arabic-reshaper==3.0.0 python-bidi==0.4.2
if ($LASTEXITCODE -ne 0) { throw "Portable runtime dependency installation failed" }

Get-ChildItem $package -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem $package -Recurse -Include "*.pyc", ".secret-key", "FIRST_LOGIN_CREDENTIALS.txt" | Remove-Item -Force
Write-Host "Built clean ZERO-DATA Windows/LAN package at $package"
