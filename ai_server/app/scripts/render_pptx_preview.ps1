param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$powerPoint = New-Object -ComObject PowerPoint.Application

$presentation = $null
try {
    $presentation = $powerPoint.Presentations.Open(
        $SourcePath,
        $true,
        $true,
        $false
    )
    $presentation.SaveAs($OutputPath, 32)
}
finally {
    if ($null -ne $presentation) {
        $presentation.Close()
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($presentation) | Out-Null
    }
    # PowerPoint may share its COM instance with an open user presentation.
    if ($powerPoint.Presentations.Count -eq 0) { $powerPoint.Quit() }
    [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($powerPoint) | Out-Null
}
