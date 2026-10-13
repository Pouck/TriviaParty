$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$reactionData = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'answer-reactions.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$assetDirectory = Join-Path (Split-Path $PSScriptRoot) 'app/src/main/assets/tv/sounds'
$manifest = @()
$frenchVoices = @('Microsoft Caroline', 'Microsoft Claude', 'Microsoft Nathalie(Canada)')
$englishVoices = @('Microsoft Richard', 'Microsoft Linda')
foreach ($outcome in @('bad','good')) {
    $reactionIndex = 0
    foreach ($phrase in $reactionData.$outcome) {
        $reactionIndex++
        $language = if ($phrase -match '^(Das |Ja!)') { 'de' } elseif ($phrase -match '^(What |Two )') { 'en' } elseif ($phrase -eq 'Niet!') { 'ru' } else { 'fr' }
        $stem = '{0}-{1:d2}' -f $outcome,$reactionIndex
        $rate = @(-1,0,1)[$reactionIndex % 3]
        if ($language -in @('de','ru')) {
            $filename = $stem + '.mp3'
            $uri = 'https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=' + $language + '&q=' + [Uri]::EscapeDataString($phrase)
            Invoke-WebRequest -Uri $uri -UserAgent 'Mozilla/5.0' -OutFile (Join-Path $assetDirectory $filename)
            $voice = 'Google TTS ' + $language
        } else {
            $filename = $stem + '.wav'
            $voice = if ($language -eq 'en') { $englishVoices[[int]($outcome -eq 'good')] } else { $frenchVoices[$reactionIndex % $frenchVoices.Count] }
            $speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
            try {
                $speaker.SelectVoice($voice)
                $speaker.Rate = $rate
                $speaker.Volume = 85
                $speaker.SetOutputToWaveFile((Join-Path $assetDirectory $filename))
                $speaker.Speak($phrase)
            } finally { $speaker.Dispose() }
        }
        $manifest += [ordered]@{ outcome=$outcome; file=$filename; text=$phrase; language=$language; voice=$voice; rate=$rate }
    }
}
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $assetDirectory 'reactions.json') -Encoding UTF8
Write-Output ('Generated {0} reactions with French, English, German and Russian voices.' -f $manifest.Count)
