;; Manual material selection related stuff

;; ---------------------------------------------------------------------------
;; do DF screen reading and key sending to let user memorize a material in the
;; DF mats list then re-select it automatically through use of Cw:1 blueprint
;; syntax
HandleSelectMatKeycode(keycode)
{
  global MatMenuSearchDelay, KeyEnter, EmbeddedDelayDuration, MemorizedMats
  global KeySelectAll
  ParseSelectMatLabelCount(keycode, matLabel, matCount)

  if (!matLabel)
  {
    MsgBox, Error parsing manual mat selection keycode: %keycode%`nAborting playback.
    return false
  }

  ; Ask the user to memorize mats the first time a label is encountered
  if (!IsMatMemorized(matLabel))
  {
    if (!MemorizeMat(matLabel))
    {
      ; user cancelled
      return false
    }
  }

  ; we now have our mat
  mat := MemorizedMats[matLabel]

  ; pause a moment to give DF a chance to catch up
  Sleep, %EmbeddedDelayDuration%

  ; Initial search for the desired mat.
  found := SearchForMat(mat)

  while (true)
  {
    ; Is the mat currently found?
    if (!found)
    {
      ; mat not found ... maybe we've run out? offer to rememorize
      if (!PromptOnMissingMat(matLabel))
      {
        ; user declined to rememorize mat
        return false
      }

      ; rememorize mat - the DF menu highlight will be on the correct
      ; mat immediately after doing this, so we won't SearchForMat() again
      if (!MemorizeMat(matLabel))
      {
        ; user cancelled during re-memorization
        return false
      }
      mat := MemorizedMats[matLabel]
      found := true
    }

    ; Try to 'select all' on this mat and wait for DF to react
    WaitForMenuAfterSending(KeySelectAll, EmbeddedDelayDuration)

    ; Look for fingerprint of mat onscreen now: if we successfully
    ; selected all of the mat, we won't find it any longer as we'll
    ; be out of the mat menu
    if (!IsMatFingerprintVisible(mat))
    {
      ; mat is not visible so we evidently were able to select all the
      ; mats we required. Cave Johnson, we're done here.
      return true
    }

    ; mat is still visible onscreen, so we must have run out of material.
    ; DF does not remove such mats from the list but just shows them with
    ; Dist of - instead.
    ; Re-loop and we'll have the user rememorize.
    found := false
  }
  MsgBox, Error: reached impossible to reach code.
  return false
}

;; ---------------------------------------------------------------------------
;; Parse label and count from {SelectMat label count}, returned in matLabel
;; and matCount
ParseSelectMatLabelCount(keycode, byRef matLabel, byRef matCount)
{
  evalOK := RegExMatch(keycode, "^\{SelectMat ([\w\-]+) (\d+)\}$", evalMatch)
  if (!evalOK)
  {
    matLabel =
    matCount =
    return
  }

  matLabel := evalMatch1
  matCount := evalMatch2
  return
}

;; ---------------------------------------------------------------------------
;; Returns true if material identified by matLabel is currently memorized.
IsMatMemorized(matLabel)
{
  global MemorizedMats
  return MemorizedMats[matLabel] ? true : false
}

;; ---------------------------------------------------------------------------
;; Clear all memorized mats and mat menu coords.
InitMemorizedMats()
{
  global MemorizedMats, MatMenuCoords
  MemorizedMats := {}
  MatMenuCoords := {}
  
  ; Clean up any leftover clip files from last round
  path := A_ScriptDir "\~qfmatclip_*.bmp" 
  FileDelete, %path%

  return
}

;; ---------------------------------------------------------------------------
;; Memorize a material from the mat list. Gathers two mouse clicks from the
;; user and screenclips the rectangle formed by the two clicks. 
MemorizeMat(matLabel)
{
  global MemorizedMats, MatMenuCoords, SelectingMat
  CoordMode, Mouse, Screen

  ActivateGameWin()

  SelectingMat := true

  msg := "USER INPUT REQUIRED`nMEMORIZING MATERIAL '" matLabel "'`n"
  msgSuffix := "`n`nPress Alt+C to cancel playback."
  
  ; Get left coord
  Tip(msg "Step 1: Highlight the desired material using +-/* keys.`nStep 2: Click to the LEFT of the FIRST highlighted letter." msgSuffix)
  SoundPlay, config\matselect-1.wav
  if (!WaitForMemorizationClick()) { ; wait for user to click or cancel
    SelectingMat := false
    return false ; user cancelled
  }
  MouseGetPos, x1, y1

  ; Get right coord
  Tip(msg "Step 3: Click to the RIGHT of the LAST highlighted letter.`nFor long rows, click to the LEFT of the Dist number." msgSuffix)
  SoundPlay, config\matselect-2.wav
  if (!WaitForMemorizationClick()) { ; wait for user to click or cancel
    SelectingMat := false
    return false ; user cancelled
  }

  MouseGetPos, x2, y2
  SoundPlay, config\matselect-3.wav

  Order(x1, x2)
  Order(y1, y2)

  ; If region isn't tall enough expand it to a minimum of 3px
  If (abs(y2 - y1) < 3)
  {
      y1 := y1 - 1
      y2 := y1 + 2
  }

  ; screenclip the region between the two mouse clicks
  path := A_ScriptDir "\~qfmatclip_" matLabel ".bmp" 
  FileDelete, %path%
  CaptureScreenRegionToFile(path, x1, y1, x2 - x1 + 1, y2 - y1 + 1)

  ; no longer in SelectingMat 'mode'
  SelectingMat := false

  if (!FileExist(path))
  {
    MsgBox, There was an error while memorizing '%matLabel%'. Could not create memorized image file:`n%path%`nAborting playback.
    return false
  }

  ; record details of memorized mat
  MemorizedMats[matLabel] := {}
  MemorizedMats[matLabel].path := path
  MemorizedMats[matLabel].x1 := x1
  MemorizedMats[matLabel].x2 := x2
  MemorizedMats[matLabel].y1 := y1
  MemorizedMats[matLabel].y2 := y2
  MemorizedMats[matLabel].label := matLabel

  ; record general coordinates of where we think DF's side menu is on screen
  MatMenuCoords := {}
  MatMenuCoords.x1 := x1
  MatMenuCoords.x2 := x2
  MatMenuCoords.y1 := y1
  MatMenuCoords.y2 := y2
  

  ; Get the mouse out of the way so it doesn't mess up ImageSearches
  MouseMove, 0, 310, , R
  return true
}

;; ---------------------------------------------------------------------------
;; Presents a message box to the user asking if they'd like to rememorize
;; a mat that was not found.
PromptOnMissingMat(matLabel)
{
  msg = 
  (
You appear to have run out of material '%matLabel%', or you cancelled.

Click OK to memorize a new material for '%matLabel%'.
Click Cancel to abort playback.
  )

  MsgBox, 1, Quickfort - Error, %msg%

  IfMsgBox, OK
    return true
  else
    return false
}

;; ---------------------------------------------------------------------------
;; Scan the mats list for our memorized mat repeatedly, sending DF's + (next
;; menu item) key at each iteration to advance the mat menu highlight. Returns
;; true if memorized mat is found, false if we don't find it within
;; MaxMatSearchChecks iterations.
SearchForMat(mat)
{
  global KeyNextMenuItem, KeyPrevMenuPage
  global MaxMatSearchChecks, MatMenuSearchDelay
  global Building

  CoordMode, Pixel, Screen
  CoordMode, Mouse, Screen
  
  checksDone := 0
  Tip("Searching for material '" mat.label "'...")

  while (checksDone++ < MaxMatSearchChecks)
  {
    if (!WinActive("Dwarf Fortress"))
    {
      WinWaitActive, Dwarf Fortress
    }

    if (!Building) ; user cancel via Alt+C
    {
      return false
    }

    Sleep, %MatMenuSearchDelay%

    if (IsMatFingerprintVisible(mat))
    {
      return true ; mat found
    }

    Send, %KeyNextMenuItem%
  }

  return false ; mat not found
}

;; ---------------------------------------------------------------------------
;; Returns true if we find a memorized mat bitmap on screen in DF's mat list
IsMatFingerprintVisible(mat)
{
  ; Scan the screen region where we think our memorized mat bitmap
  ; may appear on screen, in the materials list
  path := mat.path
  CoordMode, Pixel, Screen
  ImageSearch, , , mat.x1, mat.y1 - 300, mat.x2, mat.y2 + 300, %path%

  if (!ErrorLevel)
      return true ; mat found
  return false ; mat not found
}

;; ---------------------------------------------------------------------------
;; Returns true if we have mat menu coordinates.
HaveMatMenuCoordinates()
{
  global MatMenuCoords
  return MatMenuCoords.x1 > 0
  return
}

;; ---------------------------------------------------------------------------
;; Sends keys to DF, then waits for DF's submenu region on the right hand side
;; of the screen to change. This only works after a mat has been memorized using
;; manual material selection (we use memorized pixel coordinates to locate the
;; menu onscreen). If no mat has been memorized we just do a regular {wait} after
;; sending keys.
WaitForMenuAfterSending(keys, delay=1000)
{
  global MatMenuCoords, MatMenuSearchDelay, EmbeddedDelayDuration
  
  if (!HaveMatMenuCoordinates()) ; don't know where DF's side menu is onscreen
  {
    ; Send keys and emulate a normal {Wait} after
    Send, %keys%
    Sleep, %EmbeddedDelayDuration%
    return true
  }

  CoordMode, Pixel, Screen
  CoordMode, Mouse, Screen
  ActivateGameWin()
  WinGetPos, winLeft, winTop, winWidth, winHeight, A
  Tip("Waiting for DF menu after sending " keys "...")
  Sleep, %MatMenuSearchDelay%
  if (!ScreenRegionWaitChange(MatMenuCoords.x1 - 1, winTop + 48, 32, Min(150, winHeight - winTop), keys, delay, 0))
  {
    return false
  }

  return true
}

;; ---------------------------------------------------------------------------
;; Waits for the user to click the left mouse button and ensures that click
;; was done IN the DF window -- not on the title bar and not in order to
;; activate the DF window
WaitForMemorizationClick()
{
  global Building

  while (true)
  {
    KeyWait, LButton, D T0.25
    if (!Building)
    {
      ; user cancelled with Alt+C
      return false
    }
    if (ErrorLevel == 1)
    {
      ; lbutton not yet clicked, keep waiting
      continue
    }
    if (WinActive("Dwarf Fortress") && !IsMouseOverTitleBar())
    {
      ; Got the DF window click we were waiting on
      KeyWait, LButton ; wait for LButton to be released
      return true
    }
  }
}
