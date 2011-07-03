;; ---------------------------------------------------------------------------
;; Set global var defaults for the mouse tip.
InitMouseTip()
{
  global
  MouseTip := ""
  FullTip := ""
  LastTooltip := ""
  LastMouseX := 0
  LastMouseY := 0
  HideTooltip := 0 ; used by Alt+H hotkey
  ClearTip()
  return
}


;; ---------------------------------------------------------------------------
;; Set the body of the mousetip to value.
Tip(value)
{
  global MouseTip
  MouseTip := value
  UpdateTip()
}


;; ---------------------------------------------------------------------------
;; Clear the body of the mousetip.
ClearTip()
{
  global MouseTip
  MouseTip := ""
  UpdateTip()
}


;; ---------------------------------------------------------------------------
;; Show the mousetip.
ShowTip()
{
    global MouseTipOn, MouseTooltipUpdateMs
    UpdateTip()
    SetTimer, ShowMouseTip, %MouseTooltipUpdateMs%
    ;SetTimer, HideMouseTip, Off ; make sure a timed mouse tip hiding event (e.g. the splash tip) doesn't close a different tip
    Sleep 50 ; let the timer tick a bit, so the tip gets updated right after being turned on (Send can block the timer otherwise)
    ForceMouseTipUpdate()
}


;; ---------------------------------------------------------------------------
;; Hide the mousetip.
HideTip()
{
  global MouseTipOn
  SetTimer, ShowMouseTip, Off
  ToolTip,
}


;; ---------------------------------------------------------------------------
;; Update the text contents of the mousetip.
UpdateTip()
{
  global
  local mode, header, body
  
  ; Determine tip mode.
  if (Building)
    mode := "build"
  else if (CommandLineMode)
    mode := "prebuild"
  else if (!SelectedFile)
    mode := "pickfile"
  else if SelectedSheetIndex =
    mode := "pickfile"
  else
    mode := "prebuild"

  ; Determine contents of mouse tooltip based on mode.
  if (mode == "pickfile")
  {
    header := "Quickfort " Version "`n`nPick a blueprint file with Alt+F.`nAlt+T for command line."
  }
  else {
    if (CommandLineMode)
    {
      header := "Alt+T: #" EvalMode " " SubStr(EvalCommands, 1, 30)
      if (StrLen(EvalCommands) > 30)
        header := header . "..."
    }
    else
    {
      header := SelectedFilename
    
      if (Name%SelectedSheetIndex% != SelectedFilename)
      {
        header := header ": " Name%SelectedSheetIndex%
      }

      header := header " (" BuildType%SelectedSheetIndex% " mode)"
      header := header ", " Width%SelectedSheetIndex% "x" Height%SelectedSheetIndex%

      if (LayerCount%SelectedSheetIndex% > 1)
        header := header "x" LayerCount%SelectedSheetIndex%
    }


    if (RepeatPattern)
      header := header "`nALT+R: " RepeatPattern

    if (StartPos)
      header := header "`n>> STARTS AT: " StartPosLabel
    else if (StartPosition%SelectedSheetIndex%)
    {
      if (StartPosition%SelectedSheetIndex% == "(1, 1)")
        header := header "`nStarts at: North-west corner"
      else
        header := header "`n>> STARTS AT: " StartPosition%SelectedSheetIndex%

      if (StartComment%SelectedSheetIndex%)
      	header := header " (" StartComment%SelectedSheetIndex% ")"
    }
  }

  if (MouseTip)
  {
    body := MouseTip
  }
  else
  {
    if (mode == "build")
    {
      body := "Designating..."
    }
    else if (mode == "prebuild")
    {
      if (ShowFullTip)
      {
        body := "TYPE " . UserInitKey . " (" . UserInitText . ").`n"
            . "Position cursor with KEYBOARD.`n"
            . "`n"
            . "Alt+V shows footprint.`n"
            . "Alt+D starts playback.`n"
            . "`n"
            . "Alt+Q/W/A/S sets starting corner.`n"
            . (StartPos ? "Alt+Z resets starting corner.`n" : "")
            . "Alt+R transforms blueprint.`n"
            . "`n"
            . "Alt+F/E picks a new file/sheet.`n"
            . "Alt+T for command line.`n"
            . (PlaybackMode == "macro" ? "Alt+N saves named macro.`n" : "")
            . "Alt+K sets mode [now: " PlaybackMode "].`n"
            . "Alt+M for minitip, Alt+H to hide tip."
      }
      else
      {
        body := "TYPE " . UserInitKey . " (" . UserInitText . ") then Alt+D/V.`nAlt+F/E/T: new file/sheet/cmd.`nAlt+R: transform. Alt+M: full tip."
      }
    }
    else
    {
      body := ""
    }
  }

  FullTip := header (body ? "`n`n" body : "")
  RequestMouseTipUpdate()
}


;; ---------------------------------------------------------------------------
ForceMouseTipUpdate()
{
  RequestMouseTipUpdate()
  Gosub ShowMouseTip
  return
}


;; ---------------------------------------------------------------------------
RequestMouseTipUpdate()
{
  global LastMouseX, LastMouseY

  ; this causes the mouse tip to get refreshed next timer tick
  LastMouseX := LastMouseY := -1
  return
}


;; ---------------------------------------------------------------------------
ShowMouseTip:
{
  CoordMode, Mouse, Screen
  CoordMode, Tooltip, Screen
  MouseGetPos, xpos, ypos

  if (!ShowMouseTooltip) {
    Tooltip,
    return
  }

  if (!WinActive("Dwarf Fortress"))
  {
    Tooltip,
    LastToolTip =
  }
  else
  {
    SetTimer, ShowMouseTip, %MouseTooltipUpdateMs%

    xpos += 25
    if (ypos + 100 > ScreenHeight)
      ypos := ScreenHeight - 100 ; put tooltip above mouse pointer if we're near the bottom
    else
      ypos += 10 ; below

    if (LastTooltip != FullTip || LastMouseX != xpos || LastMouseY != ypos)
    {
      LastTooltip := FullTip
      LastMouseX := xpos
      LastMouseY := ypos

      ToolTip, %FullTip%, %xpos%, %ypos%
    }
  }
  return
}


;; ---------------------------------------------------------------------------
;; Clear and hide mouse tip goto-label
HideMouseTip:
  ClearTip()
  HideTip()
  return


;; ---------------------------------------------------------------------------
;; Clear mouse tip goto-label
ClearMouseTip:
  ClearTip()
  return
