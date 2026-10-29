$root = (Get-Location).Path
$primaryPath = Join-Path $root 'app/src/main/assets/tv/receiver.js'
$castPath = Join-Path $root 'cast-receiver/receiver.js'
$primary = [System.IO.File]::ReadAllText($primaryPath)
$cast = [System.IO.File]::ReadAllText($castPath)
$startMarker = '  function applyImageReveal('
$endMarker = '  function makeSoundPlayer('
$start = $primary.IndexOf($startMarker)
$end = $primary.IndexOf($endMarker, $start)
if ($start -lt 0 -or $end -lt 0) { throw 'Could not locate image reveal function in Android receiver.' }
$newFunction = $primary.Substring($start, $end - $start)
$castStart = $cast.IndexOf($startMarker)
$castEnd = $cast.IndexOf($endMarker, $castStart)
if ($castStart -lt 0 -or $castEnd -lt 0) { throw 'Could not locate image reveal function in Cast receiver.' }
$cast = $cast.Substring(0, $castStart) + $newFunction + $cast.Substring($castEnd)
$cast = $cast.Replace('function visual(parent, question, reveal) {', 'function visual(parent, question, reveal, state) {')
$cast = $cast.Replace('image.onload = function () { applyImageReveal(wrapper, image, question, reveal); };', 'image.onload = function () { applyImageReveal(wrapper, image, question, reveal, state); };')
$cast = $cast.Replace('if (image.complete && image.naturalWidth) applyImageReveal(wrapper, image, question, reveal);', 'if (image.complete && image.naturalWidth) applyImageReveal(wrapper, image, question, reveal, state);')
$oldFlow = @'
      if (active && displayedQuestionId === qid && promptNode) {
        if (state.question.imageRevealMode && displayedImageRevealStep !== state.question.imageRevealStep) {
          var revealImage = questionLayout && questionLayout.querySelector(".visual img");
          var oldCanvas = questionLayout && questionLayout.querySelector("canvas.progressive-image");
          if (oldCanvas && revealImage) { oldCanvas.remove(); revealImage.hidden = false; applyImageReveal(revealImage.parentNode, revealImage, state.question); }
          displayedImageRevealStep = state.question.imageRevealStep;
        }
'@
$newFlow = @'
      if (displayedQuestionId === qid && questionLayout && state.question.imageRevealMode) {
        var revealImage = questionLayout.querySelector(".visual img");
        if (revealImage) {
          var revealState = state.phase === "QUESTION_ACTIVE" ? state : Object.assign({}, state, { timerPaused: true });
          applyImageReveal(revealImage.parentNode, revealImage, state.question, false, revealState);
          displayedImageRevealStep = state.question.imageRevealStep;
        }
      }
      if (active && displayedQuestionId === qid && promptNode) {
'@
if ($cast.Contains($oldFlow)) { $cast = $cast.Replace($oldFlow, $newFlow) }
elseif (-not $cast.Contains($newFlow)) { throw 'Could not locate Cast receiver timer update block.' }
$cast = $cast.Replace('var imagePanel = node("div", null, "image-panel"); visual(imagePanel, question, reveal); layout.appendChild(imagePanel);', 'var imagePanel = node("div", null, "image-panel"); visual(imagePanel, question, reveal, state); layout.appendChild(imagePanel);')
[System.IO.File]::WriteAllText($castPath, $cast, [System.Text.UTF8Encoding]::new($false))
Write-Output 'Synchronized continuous image reveal in the Cast receiver.'
