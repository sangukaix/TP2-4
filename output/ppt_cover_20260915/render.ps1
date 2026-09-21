$ErrorActionPreference = 'Stop'
$renderDir = Join-Path $PSScriptRoot 'render'
New-Item -ItemType Directory -Force -Path $renderDir | Out-Null
$pptApp = $null
$deck = $null
try {
    $pptApp = New-Object -ComObject PowerPoint.Application
    $deck = $pptApp.Presentations.Open((Join-Path $PSScriptRoot '제주시_기획서_디자인최종.pptx'), $true, $false, $false)
    foreach ($slide in $deck.Slides) {
        $slide.Export((Join-Path $renderDir ('slide-{0:D2}.png' -f $slide.SlideIndex)), 'PNG', 1600, 900)
    }
    Write-Output ('Rendered {0} slides' -f $deck.Slides.Count)
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $pptApp -and $pptApp.Presentations.Count -eq 0) { $pptApp.Quit() }
}
