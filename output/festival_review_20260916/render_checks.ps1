$ErrorActionPreference = 'Stop'
$folder = Join-Path $PSScriptRoot 'exports'
$ppt = $null
$deck = $null
$word = $null
$doc = $null
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $deck = $ppt.Presentations.Open((Join-Path $folder 'festival_render_check.pptx'), $true, $false, $false)
    $deck.Slides.Item(4).Export((Join-Path $folder 'case-cards.png'), 'PNG', 1600, 900)
    $deck.Slides.Item(5).Export((Join-Path $folder 'case-results.png'), 'PNG', 1600, 900)
    Write-Output ('PPT slides: {0}' -f $deck.Slides.Count)
    $word = New-Object -ComObject Word.Application
    $doc = $word.Documents.Open((Join-Path $folder 'festival_render_check.docx'), $false, $true, $false)
    $doc.ExportAsFixedFormat((Join-Path $folder 'festival_render_check.pdf'), 17)
    Write-Output ('Word pages: {0}' -f $doc.ComputeStatistics(2))
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $ppt -and $ppt.Presentations.Count -eq 0) { $ppt.Quit() }
    if ($null -ne $doc) { $doc.Close(0) }
    if ($null -ne $word -and $word.Documents.Count -eq 0) { $word.Quit() }
}
