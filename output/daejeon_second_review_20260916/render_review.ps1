$ErrorActionPreference = 'Stop'
$ppt = $null
$deck = $null
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $deck = $ppt.Presentations.Open('C:\Users\Admin\Downloads\대전광역시-서구-관광-전략기획안 (2).pptx', $true, $false, $false)
    foreach ($n in @(4,7,8,11,12,13)) {
        $deck.Slides.Item($n).Export((Join-Path $PSScriptRoot "slide-$n.png"), 'PNG', 1600, 900)
    }
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $ppt -and $ppt.Presentations.Count -eq 0) { $ppt.Quit() }
}
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $doc = $word.Documents.Open('C:\Users\Admin\Downloads\대전광역시-서구-관광-전략기획안 (1).docx', $false, $true)
    $doc.ExportAsFixedFormat((Join-Path $PSScriptRoot 'word.pdf'), 17)
} finally {
    if ($null -ne $doc) { $doc.Close(0) }
    if ($null -ne $word -and $word.Documents.Count -eq 0) { $word.Quit() }
}
'Rendered 6 PPT slides and Word PDF; original files untouched.'
