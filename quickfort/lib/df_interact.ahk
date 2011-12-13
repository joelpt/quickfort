;; Functions to interact with Dwarf Fortress.

;; ---------------------------------------------------------------------------
;; execute macro by sending keys to DF window
PlayMacro(delay)
{
  global KeyMacroLoad, KeyMacroHighlightLastMacro, KeyMacroSelectMacro, KeyMacroPlay
  global LastMacroSentToWinID

  ActivateGameWin()
  ReleaseModifierKeys()

  winID := WinActive()
  if (LastMacroSentToWinID != winID)
  {
    ; this isn't really used anywhere at present but we'll still track it
    ; for possible future use; it tells us whether we've sent a macro
    ; to THIS DF instance yet
    LastMacroSentToWinID := winID
  }

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
  local key, testkeys, keylen, ch, asc, msg, success, waitAfterNext
  
  waitAfterNext := false

  ; count number of , chars in the keys string
  StringReplace, testkeys, keystrokes,`,,`,,UseErrorLevel
  testkeys := ""
  keylen := ErrorLevel

  SetKeyDelay, KeyDelay, KeyPressDuration
  SetKeyDelay, 1, 1, Play
  
  InitMemorizedMats()
  
  ActivateGameWin()
  ReleaseModifierKeys()
  Sleep, 0
  
  ; loop through the keys
  Loop, parse, keystrokes, `,
  {
    if (!Building)
      return ; user build cancellation

    Tip("Sending keystrokes (" . ((100 * A_Index)//keylen) . "% done)`nPress Alt+C to cancel.")
    Sleep, 0

    key := A_LoopField

    if (key = "{wait}")
    {
      Sleep, %EmbeddedDelayDuration%
      continue
    }

    if (key = "{WaitAfterNext}")
    {
      waitAfterNext := true
      continue
    }

    if (waitAfterNext)
    {
      if (!WaitForMenuAfterSending(key, WaitForMatMenuMaxMS)) ; sends keystroke and waits for screen change
      {
        if (!Building) 
          return ; user hit Alt+C to cancel
        MsgBox, Error: Quickfort timed out waiting for DF menu. Aborting playback.
        return
      }
      waitAfterNext := false
      continue
    }

    if (SubStr(key, 1, 10) = "{SelectMat")
    {
      ; Handle {SelectMat label count} manual material selection.
      success := HandleSelectMatKeycode(key)
      
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

    if (!WinActive("Dwarf Fortress"))
    {
      WinWaitActive, Dwarf Fortress
      Sleep, 500
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
    }
    else if (SendMode = "SendPlay")
      SendPlay, %key%
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
  InitMemorizedMats() ; clean up as needed
  return
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
