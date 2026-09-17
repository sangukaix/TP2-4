param([Parameter(Mandatory=$true)][string]$Stem)
$ErrorActionPreference = 'Stop'
$reviewRoot = [IO.Path]::GetFullPath($PSScriptRoot)
$inputDocx = Join-Path $reviewRoot ($Stem + '.docx')
$inputPptx = Join-Path $reviewRoot ($Stem + '.pptx')
if (-not (Test-Path -LiteralPath $inputDocx) -or -not (Test-Path -LiteralPath $inputPptx)) { throw 'Both downloaded documents must exist.' }
$wordPdf = Join-Path $reviewRoot ($Stem + '-word.pdf')
$slideDir = Join-Path $reviewRoot ($Stem + '-slides')
New-Item -ItemType Directory -Path $slideDir -Force | Out-Null

# Own read-only document handles only; never save back to the source documents.
$wordApp = New-Object -ComObject Word.Application
$wordDocument = $null
try {
    $wordDocument = $wordApp.Documents.Open($inputDocx, $false, $true)
    $wordDocument.ExportAsFixedFormat($wordPdf, 17)
} finally {
    if ($null -ne $wordDocument) { $wordDocument.Close(0) }
    if ($wordApp.Documents.Count -eq 0) { $wordApp.Quit(0) }
}
$slideApp = New-Object -ComObject PowerPoint.Application
$slideDeck = $null
try {
    $slideDeck = $slideApp.Presentations.Open($inputPptx, -1, 0, 0)
    $slideDeck.Export($slideDir, 'PNG', 1600, 900)
    Write-Output ('PPT_SLIDES ' + $slideDeck.Slides.Count)
} finally {
    if ($null -ne $slideDeck) { $slideDeck.Close() }
    # PowerPoint may share an app instance. Do not close anyone else's deck.
    if ($slideApp.Presentations.Count -eq 0) { $slideApp.Quit() }
}
Write-Output ('WORD_PDF ' + $wordPdf)
