;; Functions to perform interactions with Dwarf Fortress.


;; ---------------------------------------------------------------------------
;; execute macro by sending keys to DF window
PlayMacro(delay)
{
  global KeyMacroLoad, KeyMacroHighlightLastMacro, KeyMacroSelectMacro, KeyMacroPlay

  ;if (delay < 500)
  ;  delay := 500
  ;else if (delay > 10000)
  ;  delay := 10000

  ActivateGameWin()
  ReleaseModifierKeys()

  Sleep, 1000 ;; sometimes DF needs a moment 
  Send %KeyMacroLoad% ;; show load macro menu
  Send %KeyMacroHighlightLastMacro%  ;; highlight last macro in the list
  Send %KeyMacroSelectMacro% ;; select macro
  Sleep %delay%
  Send %KeyMacroPlay% ;; play it after delay
  return
}


;; ---------------------------------------------------------------------------
;; send keystrokes to game window; keys should be separated by commas
SendKeys(keystrokes)
{
  global
  local key, testkeys, keylen, pctDone, ch, asc, msg, success
  ActivateGameWin()
  ReleaseModifierKeys()
  Sleep, 0
  InitMemorizedMats()
  SetKeyDelay, KeyDelay, KeyPressDuration
  SetKeyDelay, 1, 1, Play
  
  ; count number of , chars in the keys string
  StringReplace, testkeys, keystrokes,`,,`,,UseErrorLevel
  testkeys := ""
  keylen := ErrorLevel

  ; loop through the keys
  Loop, parse, keystrokes, `,
  {
    if (!Building) return ; user build cancellation

    pctDone := Floor((A_Index/keylen) * 100)
    Tip("Quickfort running (" pctDone "% done)`nHold Alt+C to cancel.")

    key := A_LoopField

    if (key = "{wait}")
    {
      Sleep, %EmbeddedDelayDuration%
      continue
    }

    if (key = "{EnterMatMenuSafe}")
    {
      if (HaveMatMenuCoordinates())
      {
        if (!WaitForMatMenuChange())
        {
          if (!Building) return ; user hit Alt+C to cancel
          
          MsgBox, Error: Quickfort timed out waiting for the materials menu. Aborting playback.
          return
        }
      }
      else
      {
        ; Don't have mat menu coords so just send {Enter}; we'll be
        ; asking the user to memorize a mat next so we needn't
        ; auto-detect when the mat menu appears
        Send, %KeyEnter%
      }
    }

    if (SubStr(key, 1, 10) = "{SelectMat")
    {
      ; Handle {SelectMat label count} manual material selection.
      SelectingMat := true
      success := HandleSelectMatKeycode(key)
      SelectingMat := false
      
      if (!success)
        return ; User cancelled process or there was an error, abort playback.

      continue ; Mat selection performed OK, continue looping through keystrokes
    }

    UseSafeMode := 0
    ch := SubStr(key, 1, 1)
    asc := Asc(ch)

    if (SendMode = "ControlSend" && (ch = "^" || ch = "+" || ch = "!" || ch = "<" || ch = ">" || SubStr(keys, 1, 6) = "{Shift" || (asc >= 65 && asc <= 90))) {
      ; We have to use special handling when send mode is ControlSend and we have to send modifier keys; ControlSend
      ; fails miserably when such modifier keys are sent.
      UseSafeMode := 1
    }

    if (EnableSafetyAbort)
    {
      IfWinNotActive Dwarf Fortress
      {
        ; prevent mass sending keys to wrong window (no reliable way to make DF receive all keys in background; ControlSend is flaky w/ DF)
        Building := 0
        HideTip()
        msg := "Macro aborted!`n`nYou switched windows. The Dwarf Fortress window must be focused while Quickfort is running."
        MsgBox, %msg%
        break
      }
    }

    ; actually send the keys!
    if (UseSafeMode)
    {
      ; Make sure the DF window is active
      ActivateGameWin()

      ; Send desired keys "safely"
      SetKeyDelay, 150, 25
      Send, %keys%
      SetKeyDelay, KeyDelay, KeyPressDuration
      ;SetKeyDelay, KeyDelay, KeyPressDuration, Play
    }
    else if (SendMode = "SendPlay")
      SendPlay %key%
    else if (SendMode = "SendInput")
      SendInput %key%
    else if (SendMode = "Send")
      Send %key%
    else if (SendMode = "SendEvent")
      SendEvent %key%
    else if (SendMode = "ControlSend") {
      ReleaseModifierKeys()
      ControlSend,, %key% ,Dwarf Fortress
    }
    else {
      MsgBox, Unsupported SendMode '%SendMode%'.
      return
    }
  }
  return
}


;; ---------------------------------------------------------------------------
;; do DF screen reading and key sending to let user memorize a material in the
;; DF mats list then re-select it automatically through use of Cw:1 blueprint
;; syntax
HandleSelectMatKeycode(key)
{
  global MatMenuSearchDelay, KeyEnter
  ParseSelectMatLabelCount(key, matLabel, matCount)

  if (!matLabel)
  {
    MsgBox, Error parsing manual mat selection key: %key%`nAborting playback.
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

  ; Search for and select the desired mat the specified number of times.
  Loop, % matCount
  {
    ; mat is already memorized; try to find it in the mat list
    if (!SearchForMat(matLabel))
    {
      ; mat not found ... maybe we've run out?
      if (!PromptOnMissingMat(matLabel))
      {
        ; user declined to rememorize mat
        return false
      }

      ; rememorize mat - the DF menu highlight will be on the correct
      ; mat immediately after doing this, so we won't SearchForMat() again
      if (!MemorizeMat(matLabel))
      {
        ; user cancelled re-memorization
        return false
      }
    }
    
    ; correct mat is now highlighted, now just send the choose-mat key
    ; TODO abstract code which calls Send/SendInput/... and use it here,
    ;      and in PlayMacro() also. 
    Send, %KeyEnter%
    Sleep, %MatMenuSearchDelay%
  }

  ; Done with {SelectMat label count} key
  return true
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
  return
}

;; ---------------------------------------------------------------------------
;; Memorize a material from the mat list. Gathers two mouse clicks from the
;; user and screenclips the rectangle formed by the two clicks. 
MemorizeMat(matLabel)
{
  global MemorizedMats, MatMenuCoords

  ActivateGameWin()

  ; Get left coord
  ;KeyWait, LButton ; wait for lbutton to be released
  msg := "USER INPUT REQUIRED - MEMORIZING MATERIAL :" matLabel "`n"
  Tip(msg "Step 1: Highlight the desired material using +-/* keys.`nStep 2: Click to the LEFT of the FIRST highlighted letter.")
  WaitForMemorizationClick()

  CoordMode, Mouse, Screen
  MouseGetPos, x1, y1
  ;CoordMode, Mouse, Relative
  ;MouseGetPos, rx1, ry1

  ; Get right coord
  KeyWait, LButton ; wait for lbutton to be released
  Tip(msg "Step 3: Click to the RIGHT of the LAST highlighted letter.`nFor long rows, click to the LEFT of the Dist number.")
  WaitForMemorizationClick()
  while (true)
  {
    KeyWait, LButton, D
    if (WinActive("Dwarf Fortress") && !IsMouseOverTitleBar())
      break
  }
  CoordMode, Mouse, Screen
  MouseGetPos, x2, y2
  ;CoordMode, Mouse, Relative
  ;MouseGetPos, rx2, ry2

  Order(x1, x2)
  Order(y1, y2)
  ;Order(rx1, rx2)
  ;Order(ry1, ry2)

  ; If region isn't tall enough expand it
  If (abs(y2 - y1) < 3)
  {
      y1 := y1 - 1
      y2 := y1 + 2
  }

  ;aa := x1 ", " y1 ", " x2 ", " y2
  ;Tip(aa)
  path := A_ScriptDir "\~qfmatclip_" matLabel ".bmp" 
  FileDelete, %path%
  CaptureScreenRegionToFile(path, x1, y1, x2 - x1 + 1, y2 - y1 + 1)

  if (!FileExist(path))
  {
    MsgBox, There was an error while memorizing '%matLabel%'. Could not create memorized image file:`n%path%`nAborting playback.
    return false
  }
  MemorizedMats[matLabel] := {}
  MemorizedMats[matLabel].path := path
  MemorizedMats[matLabel].x1 := x1
  MemorizedMats[matLabel].x2 := x2
  MemorizedMats[matLabel].y1 := y1
  MemorizedMats[matLabel].y2 := y2

  MatMenuCoords := {}
  MatMenuCoords.x1 := x1
  MatMenuCoords.x2 := x2
  MatMenuCoords.y1 := y1
  MatMenuCoords.y2 := y2

  return true
}

;; ---------------------------------------------------------------------------
;; Presents a message box to the user asking if they'd like to rememorize
;; a mat that was not found.
PromptOnMissingMat(matLabel)
{
  msg = 
  (
The material you memorized for '%matLabel%' could not be found. 
You might have run out of the material.

Click OK to re-memorize material '%matLabel%'.
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
SearchForMat(matLabel)
{
  global MemorizedMats, KeyNextMenuItem, MaxMatSearchChecks, MatMenuSearchDelay

  CoordMode, Pixel, Screen
  CoordMode, Mouse, Screen
  mat := MemorizedMats[matLabel]
  path := mat.path
  checksLeft := MaxMatSearchChecks
  Tip("Searching for material :" matLabel)
  while (--checksLeft >= 0)
  {
    if (!WinActive("Dwarf Fortress"))
    {
      WinWaitActive, Dwarf Fortress
    }

    ; Scan the screen region where we think our memorized mat bitmap
    ; may appear on screen, in the materials list
    ImageSearch, , , mat.x1, mat.y1 - 300, mat.x2, mat.y2 + 300, %path%

    if (!ErrorLevel)
        return true ; mat found

    Send, % KeyNextMenuItem
    Sleep, % MatMenuSearchDelay
  }
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
;; Sends Enter to open the mat menu and then waits for it to appear by
;; monitoring a screen-region for change where we expect the mat menu to appear.
;; Returns true if the change was detected, or false if we timed out waiting.
WaitForMatMenuChange()
{
  global MatMenuCoords, KeyEnter, WaitForMatMenuMaxMS
  CoordMode, Pixel, Screen
  CoordMode, Mouse, Screen
  ActivateGameWin()
  WinGetPos, winLeft, winTop, winWidth, winHeight, A
  
  ;MouseMove, MatMenuCoords.x1 - 1, winTop + 48
  ;Sleep, 1000
  if (!ScreenRegionWaitChange(MatMenuCoords.x1 - 1, winTop + 48, 32, Min(150, winHeight - winTop), KeyEnter, WaitForMatMenuMaxMS))
  {
    return false
  }

  return true
}


;; ---------------------------------------------------------------------------
;; release modifier keys to avoid sending modified keystrokes to the game window
ReleaseModifierKeys()
{
  Loop
  {
    if (GetKeyState("Alt") || GetKeyState("Ctrl") || GetKeyState("Shift") || GetKeyState("LWin") || GetKeyState("RWin"))
    {
      ; Try to avoid the modifier keys screwing up our playback if the user presses them.
      KeyWait, Alt
      KeyWait, Ctrl
      KeyWait, Shift
      KeyWait, LWin
      KeyWait, RWin
      Sleep 10
      ControlSend,, {Alt up}{Ctrl up}{Shift up}{LWin up}{RWin up},Dwarf Fortress
      Sleep 10
    }
    else
      break
  }
  return
}


;; ---------------------------------------------------------------------------
;; Activate/focus DF window.
ActivateGameWin()
{
  If (!WinActive("Dwarf Fortress"))
  {
    WinActivate, Dwarf Fortress
    SendInput {Alt up}{Ctrl up}{Shift up}
  }
}

;; ---------------------------------------------------------------------------
;; Check DF's init.txt for [MACRO_MS:1+] and give the user an opportunity
;; to have QF modify the file to have [MACRO_MS:0] instead.
CheckDFMacroMS()
{
  global DoMacroMSCheck

  if (!DoMacroMSCheck)
    return

  WinWaitActive, Dwarf Fortress

  val := GetDFInitTxtSetting("MACRO_MS")

  if (val == -255)
    return  ; file/setting not found
  
  if (val == 0)
    return  ; already set to 0ms
  
  msg =
  (
Quickfort has detected that this instance of Dwarf Fortress has a
setting of [MACRO_MS:%val%] in its data/init/init.txt file.

Values for MACRO_MS higher than 0 can make Quickfort's
macro-based playback run very slowly.

Quickfort can change this setting for you. Please choose:

YES: Modify my DF's init.txt and set [MACRO_MS:0]
NO: Don't modify now, but ask again next time
CANCEL: Don't modify and never ask me again
  )

  MsgBox, 3, Quickfort - Warning, %msg%
  IfMsgBox, Yes
  {
    ActivateGameWin()
    path := SetDFInitTxtSetting("MACRO_MS", "0")
    if (path == -255)
    {
      MsgBox, There was a problem modifying init.txt. Quickfort will continue.
      return
    }
    MsgBox, MACRO_MS set successfully. Please restart Dwarf Fortress for the change to take effect.`n`nModified file path:`n%path%
    return
  }

  IfMsgBox, Cancel
  {
    DoMacroMSCheck := 0
    SaveAppState()
    return
  }

  ; User clicked No - do nothing
  return
}


;; ---------------------------------------------------------------------------
;; Examine DF data/init/init.txt and retrieve value of named setting.
;; Currently expects DF window to be active (this allows for multiple
;; simultaneous DF instances).
;; Returns the setting's value, or -255 if file or setting could not be found.
GetDFInitTxtSetting(name)
{
  dfpath := GetWinPath("A") ; active window is the instance of DF we want 
  SplitPath, dfpath, , dfpath
  initpath := dfpath "\data\init\init.txt"

  FileRead, data, %initpath%
  if (!data)
  {
    ;; Did not locate init.txt
    return -255
  }

  evalOK := RegExMatch(data, "\[" name "\:(.*)\]", evalMatch)
  if (!evalOK)
  {
    ;; Did not locate setting
    return -255
  }

  ;; Got a match
  return evalMatch1
}

;; ---------------------------------------------------------------------------
;; Set the value of an EXISTING setting in DF data/init/init.txt.
;; Currently expects DF window to be active (this allows for multiple
;; simultaneous DF instances).
;; Returns the setting's new value, or -255 if file could not be found.
SetDFInitTxtSetting(name, newValue)
{
  dfpath := GetWinPath("A") ; active window is the instance of DF we want 
  SplitPath, dfpath, , dfpath
  initpath := dfpath "\data\init\init.txt"

  FileRead, data, %initpath%
  if (!data)
  {
    ;; Did not locate init.txt
    return -255
  }

  changed := RegExReplace(data, "\[" name "\:(.*)\]", "[" name ":" newValue "]")
  FileDelete, %initpath%
  FileAppend, %changed%, %initpath%
  return initpath
}

;; ---------------------------------------------------------------------------
;; Waits for the user to click the left mouse button and ensures that click
;; was done IN the DF window -- not on the title bar and not in order to
;; activate the DF window
WaitForMemorizationClick()
{
  SoundPlay, config/attention.wav
  while (true)
  {
    KeyWait, LButton, D
    if (WinActive("Dwarf Fortress") && !IsMouseOverTitleBar())
      break
  }
  return
}
