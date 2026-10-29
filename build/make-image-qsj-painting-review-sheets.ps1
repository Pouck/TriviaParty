Add-Type -AssemblyName System.Drawing
$root = (Get-Location).Path
$allTargets = Get-Content -Raw (Join-Path $root 'build/image-qsj-candidate-targets.json') | ConvertFrom-Json
$paintTargets = @()
foreach ($target in $allTargets) { if ($target.collection -eq 'paintings100') { $paintTargets += $target } }
$paintTargets = @($paintTargets | Sort-Object benchmarkRank)
$candidates = Join-Path $root 'build/image-qsj-sampler/candidates/quality-pass'
$outDir = Join-Path $root 'build/image-qsj-sampler/audit/paintings-top100'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$cardW = 260; $cardH = 210; $cols = 4; $rows = 4; $pageSize = $cols * $rows
for ($start = 0; $start -lt $paintTargets.Count; $start += $pageSize) {
  $count = [Math]::Min($pageSize, $paintTargets.Count - $start)
  $bmp = [System.Drawing.Bitmap]::new($cardW * $cols, $cardH * $rows)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.Clear([System.Drawing.Color]::FromArgb(16, 23, 37))
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  for ($i=0; $i -lt $count; $i++) {
    $item = $paintTargets[$start + $i]
    $x = ($i % $cols) * $cardW; $y = [Math]::Floor($i / $cols) * $cardH
    $path = Join-Path $candidates ($item.key + '.jpg')
    if (-not (Test-Path -LiteralPath $path)) { $path = Join-Path $candidates ($item.key + '.png') }
    try {
      $src = [System.Drawing.Image]::FromFile($path)
      $scale = [Math]::Min(240.0 / $src.Width, 155.0 / $src.Height)
      $dw = [Math]::Max(1, [int]($src.Width * $scale)); $dh = [Math]::Max(1, [int]($src.Height * $scale))
      $g.DrawImage($src, $x + 10 + [int]((240-$dw)/2), $y + 5 + [int]((155-$dh)/2), $dw, $dh)
      $src.Dispose()
    } catch { }
    $font = [System.Drawing.Font]::new('Arial', 9)
    $brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)
    $label = ('{0:D3}  {1}' -f $item.benchmarkRank, $item.displayTitle)
    $g.DrawString($label, $font, $brush, [System.Drawing.RectangleF]::new($x+7,$y+163,$cardW-14,34))
    $font.Dispose(); $brush.Dispose()
  }
  $page = [int]($start / $pageSize) + 1
  $bmp.Save((Join-Path $outDir ('paintings-{0:D2}.jpg' -f $page)), [System.Drawing.Imaging.ImageFormat]::Jpeg)
  $g.Dispose(); $bmp.Dispose()
}
$paintTargets | Select-Object benchmarkRank, displayTitle, artist, fileTitle, key | Export-Csv -NoTypeInformation -Encoding utf8 (Join-Path $outDir 'index.csv')
Write-Output ("candidates={0}; sheets={1}; output={2}" -f $paintTargets.Count, [Math]::Ceiling($paintTargets.Count / $pageSize), $outDir)
