$ErrorActionPreference = 'Stop'
$ppt = $null
$deck = $null
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $deck = $ppt.Presentations.Open((Join-Path $PSScriptRoot 'original.pptx'), $true, $false, $false)
    foreach ($n in @(4, 7, 12)) {
        $deck.Slides.Item($n).Export((Join-Path $PSScriptRoot "original-$n.png"), 'PNG', 1600, 900)
    }
    Write-Output ('Rendered original slides 4, 7, 12; total {0}' -f $deck.Slides.Count)
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $ppt -and $ppt.Presentations.Count -eq 0) { $ppt.Quit() }
}
