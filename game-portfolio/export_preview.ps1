$ErrorActionPreference = "Stop"
$dir  = "C:\Users\LEGION\Desktop\shooting-game\game-portfolio"
$tmp  = Join-Path $dir "build_tmp.pptx"
$pdfT = Join-Path $dir "build_tmp.pdf"
$out  = Join-Path $dir "preview"

if (Test-Path $out) { Remove-Item $out -Recurse -Force }
New-Item -ItemType Directory -Path $out | Out-Null

$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($tmp, $true, $false, $false)
$pres.SaveAs($pdfT, 32)   # ppSaveAsPDF

foreach ($slide in $pres.Slides) {
    $n = $slide.SlideIndex
    $file = Join-Path $out ("slide-{0:D2}.png" -f $n)
    $slide.Export($file, "PNG", 1600, 900)
}
$pres.Close()
$app.Quit()
Write-Output "pdf: ok"
Write-Output "slides exported: $((Get-ChildItem $out).Count)"
