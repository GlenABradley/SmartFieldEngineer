param(
    [Parameter(Mandatory=$true)][string]$JobId,
    [Parameter(Mandatory=$true)][string]$OutputRoot,
    [string]$AuthorizedTarget = ''
)
$ErrorActionPreference = 'Stop'
if ($JobId -notmatch '^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$') { throw 'Invalid job ID' }
$dest = Join-Path $OutputRoot ($JobId + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Path $dest | Out-Null
Get-NetAdapter | Select-Object Name,InterfaceDescription,Status,LinkSpeed,MacAddress | ConvertTo-Json | Set-Content (Join-Path $dest 'adapters.json')
Get-NetIPConfiguration | Format-List * | Out-File (Join-Path $dest 'ip-configuration.txt')
Get-NetRoute | Select-Object InterfaceAlias,DestinationPrefix,NextHop,RouteMetric | ConvertTo-Json | Set-Content (Join-Path $dest 'routes.json')
Get-DnsClientServerAddress | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $dest 'dns.json')
netsh wlan show interfaces | Out-File (Join-Path $dest 'wifi-interface.txt')
# Active probe occurs only when an explicit target is supplied. No subnet scan.
if ($AuthorizedTarget) {
    if ($AuthorizedTarget -notmatch '^[A-Za-z0-9.:_-]+$') { throw 'Invalid target' }
    Test-Connection -ComputerName $AuthorizedTarget -Count 4 -ErrorAction Continue | Format-List * | Out-File (Join-Path $dest 'ping.txt')
}
Get-ChildItem $dest -File | Get-FileHash -Algorithm SHA256 | Select-Object Path,Hash | ConvertTo-Json | Set-Content (Join-Path $dest 'hashes.json')
Write-Output $dest
