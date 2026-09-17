$ErrorActionPreference = 'Stop'
$validationRoot = $PSScriptRoot
$pptImages = Join-Path $validationRoot 'ppt_render'
New-Item -ItemType Directory -Force -Path $pptImages | Out-Null
$presentationApp = $null
$presentation = $null
$wordApp = $null
$wordDoc = $null
try {
    $presentationApp = New-Object -ComObject PowerPoint.Application
    $presentation = $presentationApp.Presentations.Open((Join-Path $validationRoot '제주시_최종검증.pptx'), $true, $false, $false)
    foreach ($slide in $presentation.Slides) {
        $slide.Export((Join-Path $pptImages ('slide-{0:D2}.png' -f $slide.SlideIndex)), 'PNG', 1600, 900)
    }
    $slideCount = $presentation.Slides.Count
    $presentation.Close()
    $presentation = $null
    if ($presentationApp.Presentations.Count -eq 0) { $presentationApp.Quit() }
    $presentationApp = $null

    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordDoc = $wordApp.Documents.Open((Join-Path $validationRoot '제주시_최종검증.docx'), $false, $true)
    $wordDoc.ExportAsFixedFormat((Join-Path $validationRoot 'jeju_word.pdf'), 17)
    $pageCount = $wordDoc.ComputeStatistics(2)
    @{ppt_slides=$slideCount;word_pages=$pageCount} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $validationRoot 'native_render_counts.json') -Encoding utf8
    $wordDoc.Close(0)
    $wordDoc = $null
    if ($wordApp.Documents.Count -eq 0) { $wordApp.Quit() }
    $wordApp = $null
    Write-Output "Rendered $slideCount slides and $pageCount Word pages."
} finally {
    if ($null -ne $presentation) { $presentation.Close() }
    if ($null -ne $presentationApp -and $presentationApp.Presentations.Count -eq 0) { $presentationApp.Quit() }
    if ($null -ne $wordDoc) { $wordDoc.Close(0) }
    if ($null -ne $wordApp -and $wordApp.Documents.Count -eq 0) { $wordApp.Quit() }
}
