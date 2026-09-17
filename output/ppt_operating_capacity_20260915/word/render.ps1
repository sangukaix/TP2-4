$ErrorActionPreference='Stop'
$app=$null
$doc=$null
try {
 $app=New-Object -ComObject Word.Application
 $app.Visible=$false
 $doc=$app.Documents.Open((Join-Path $PSScriptRoot '제주시_기획서_디자인최종.docx'),$false,$true)
 $doc.ExportAsFixedFormat((Join-Path $PSScriptRoot 'word.pdf'),17)
 Write-Output "Word pages: $($doc.ComputeStatistics(2))"
} finally {
 if($null -ne $doc){$doc.Close(0)}
 if($null -ne $app -and $app.Documents.Count -eq 0){$app.Quit()}
}
