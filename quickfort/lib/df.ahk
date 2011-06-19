;; Functions to perform interactions with Dwarf Fortress.


;; ---------------------------------------------------------------------------
;; execute macro by sending keys to DF window
PlayMacro(delay)
{
  if (delay < 500)
    delay := 500
  else if (delay > 5000)
    delay := 5000

  ActivateGameWin()
  ReleaseModifierKeys()
  Send ^l
  Sleep 1000
  Send {Enter}
  Sleep %delay%
  Send ^p
  return
}


;; ---------------------------------------------------------------------------
;; send keystrokes to game window
SendKeys(keys)
{
  global
  ActivateGameWin()
  ReleaseModifierKeys()
  Sleep, 0

  if (Instr(keys, "{wait}"))
  {
    ; Convert {wait} statements to ¢ so we can Loop Parse in chunks
    ; and sleep between each chunk.
    StringReplace, keys, keys, {wait}, ¢, All
  }
  ; TODO: seed {waits} into long key sequences which have no {wait}s
  ; in them, to permit for catching Alt+C and safety abort

  ; Count total number of ¢ chars
  StringSplit, pctarray, keys, ¢
  numPctChars := pctarray0

  SetKeyDelay, KeyDelay, KeyPressDuration
  SetKeyDelay, 1, 1, Play

  Loop, parse, keys, ¢
  {
    pctDone := Floor((A_Index/numPctChars) * 100)

    Tip("Quickfort running (" pctDone "% done)`nHold Alt+C to cancel.")

    Sleep, 0
    Sleep, KeyDelay
    if (!Building)
    {
      ; build was cancelled by user.
      break
    }

    keys := A_LoopField

    UseSafeMode := 0
    ch := SubStr(keys, 1, 1)
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
      ;MsgBox % "safe mode on " keys
      ; Make sure the DF window is active

      ActivateGameWin()

      ; Send desired keys "safely"
      SetKeyDelay, 150, 25
      Send %keys%
      SetKeyDelay, KeyDelay, KeyPressDuration
      ;SetKeyDelay, KeyDelay, KeyPressDuration, Play
    }
    else if (SendMode = "SendPlay")
      SendPlay %keys%
    else if (SendMode = "SendInput")
      SendInput %keys%
    else if (SendMode = "Send")
      Send %keys%
    else if (SendMode = "SendEvent")
      SendEvent %keys%
    else if (SendMode = "ControlSend") {
      ReleaseModifierKeys()
      ControlSend,, %keys% ,Dwarf Fortress
    }
    else {
      MsgBox, Unsupported SendMode '%SendMode%'.
      return
    }

    Sleep, %EmbeddedDelayDuration%
  }
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
