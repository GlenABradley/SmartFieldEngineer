# Run in Windows PowerShell as the normal technician account.
# Review the script first. Windows applications are downloaded from winget manifests.
$ErrorActionPreference = 'Stop'
$packages = @('Python.Python.3.12','WiresharkFoundation.Wireshark','PuTTY.PuTTY','WinSCP.WinSCP','TheDocumentFoundation.LibreOffice','Gyan.FFmpeg')
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw 'Install Microsoft App Installer from Microsoft Store, then retry.' }
foreach ($package in $packages) {
    & winget install --id $package --exact --source winget --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne -1978335189) { throw "Installer failed or requires attention: $package code $LASTEXITCODE" }
}
Write-Host 'Install Panasonic drivers using the serial-specific official support package. Reopen PowerShell after Python installation.'
Write-Host 'Npcap capture driver requires separate license review and installation; no redistribution is included.'
Write-Host 'Start: py -3.12 .\desktop.py'
Write-Host 'Verify: py -3.12 -m unittest discover -s tests -v'
