Add-Type -AssemblyName System.Drawing
$root = (Get-Location).Path
$bank = Get-Content -Raw (Join-Path $root 'game-library/bank/questions.json') | ConvertFrom-Json
$media = Join-Path $root 'game-library/bank/media'
$outDir = Join-Path $root 'build/image-qsj-sampler/audit'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$byImage = [ordered]@{}
foreach ($q in $bank.questions) {
  foreach ($p in $q.presentations) {
    if (-not $p.content.imageRevealMode -or -not $p.content.imageUrl.StartsWith('media/')) { continue }
    $file = $p.content.imageUrl.Substring(6)
    if (-not $byImage.Contains($file)) { $byImage[$file] = [pscustomobject]@{ File=$file; Answer=($q.answers -join ' / '); Category=$p.legacyCategory } }
  }
}
$items = @($byImage.Values)
$cardW = 260; $cardH = 210; $cols = 4; $rows = 4; $pageSize = $cols * $rows
for ($start = 0; $start -lt $items.Count; $start += $pageSize) {
  $count = [Math]::Min($pageSize, $items.Count - $start)
  $bmp = [System.Drawing.Bitmap]::new($cardW * $cols, $cardH * $rows)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.Clear([System.Drawing.Color]::FromArgb(16, 23, 37))
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  for ($i=0; $i -lt $count; $i++) {
    $item = $items[$start + $i]
    $x = ($i % $cols) * $cardW; $y = [Math]::Floor($i / $cols) * $cardH
    $path = Join-Path $media $item.File
    try {
      $src = [System.Drawing.Image]::FromFile($path)
      $scale = [Math]::Min(240.0 / $src.Width, 155.0 / $src.Height)
      $dw = [Math]::Max(1, [int]($src.Width * $scale)); $dh = [Math]::Max(1, [int]($src.Height * $scale))
      $g.DrawImage($src, $x + 10 + [int]((240-$dw)/2), $y + 5 + [int]((155-$dh)/2), $dw, $dh)
      $src.Dispose()
    } catch { }
    $font = [System.Drawing.Font]::new('Arial', 9)
    $brush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::White)
    $id = '{0:D3}' -f ($start + $i + 1)
    $label = $id + '  ' + $item.Answer
    $g.DrawString($label, $font, $brush, [System.Drawing.RectangleF]::new($x+7,$y+163,$cardW-14,25))
    $font.Dispose(); $brush.Dispose()
  }
  $page = [int]($start / $pageSize) + 1
  $bmp.Save((Join-Path $outDir ('sheet-{0:D2}.jpg' -f $page)), [System.Drawing.Imaging.ImageFormat]::Jpeg)
  $g.Dispose(); $bmp.Dispose()
}
$items | Select-Object @{n='Number';e={[array]::IndexOf($items,$_)+1}}, Answer, File, Category | Export-Csv -NoTypeInformation -Encoding utf8 (Join-Path $outDir 'index.csv')
Write-Output ("images={0}; sheets={1}; output={2}" -f $items.Count, [Math]::Ceiling($items.Count / $pageSize), $outDir)
