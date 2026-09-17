$ErrorActionPreference = 'Stop'
$ppt = $null
$deck = $null
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $deck = $ppt.Presentations.Open((Join-Path $PSScriptRoot '대전서구_공통양식_견적개선.pptx'), $true, $false, $false)
    foreach ($n in @(4,5,9,13)) {
        $deck.Slides.Item($n).Export((Join-Path $PSScriptRoot "linked-$n.png"), 'PNG', 1600, 900)
    }
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $ppt -and $ppt.Presentations.Count -eq 0) { $ppt.Quit() }
}
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $doc = $word.Documents.Open((Join-Path $PSScriptRoot '대전서구_공통양식_견적개선.docx'), $false, $true)
    $doc.ExportAsFixedFormat((Join-Path $PSScriptRoot 'linked-word.pdf'), 17)
} finally {
    if ($null -ne $doc) { $doc.Close(0) }
    if ($null -ne $word -and $word.Documents.Count -eq 0) { $word.Quit() }
}
'Rendered changed slides and Word PDF without saving originals.'
