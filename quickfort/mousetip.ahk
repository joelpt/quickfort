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
    global MouseTipOn, MouseTooltipInGameUpdateEveryMs
    MouseTipOn := 1
    UpdateTip()
    SetTimer, ShowMouseTip, %MouseTooltipInGameUpdateEveryMs%
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
  MouseTipOn := 0
  ToolTip,
}

;; ---------------------------------------------------------------------------
;; Update the text contents of the mousetip.
UpdateTip()
{
  global
  local mode, header, body

  ; Determine tip mode.
  if (!SelectedFile)
    mode := "pickfile"
  else if SelectedSheetIndex =
    mode := "pickfile"
  else if (Building)
    mode := "build"
  else
    mode := "prebuild"

  ; Determine contents of mouse tooltip based on mode.
  if (mode == "pickfile")
  {
    header := "Quickfort 2.0.`n`nPick a blueprint file with Alt+F." . (LastSelectedFile ? "`nPress Alt+E to use " LastSelectedFilename " again." : "")
  }
  else {
    header := SelectedFilename
    n := Name%SelectedSheetIndex%
    if (Name%SelectedSheetIndex% != SelectedFilename)
    {
      header := header "`n" Name%SelectedSheetIndex%
    }

    if (RepeatPattern)
      header := header "`nTRANSFORMATION: " RepeatPattern
    if (StartPos)
      header := header "`nSTARTING CORNER: " StartPosLabel
  }

  if (Tooltip)
  {
    body := Tooltip
  }
  else
  {
    if (mode == "build")
    {
      body := "Building...(% of % done)"
    }
    else if (mode == "prebuild")
    {
        body := "TYPE " . userInitKey . " (" . userInitText . "). Position cursor with KEYBOARD.`n`n"
            . "Alt+V shows footprint.`n"
            . "Alt+D starts playback.`n"
            . "Alt+F picks another file.`n`n"
            . "Alt+R for repeat mode.`n"
            . "Alt+Q/W/A/S sets starting corner."
    }
    else
    {
      body := ""
    }
  }

  FullTip := header "`n`n" body "`n`n" mode
  RequestMouseTipUpdate()
}


;; ---------------------------------------------------------------------------
ForceMouseTipUpdate()
{
  RequestMouseTipUpdate()
  SetTimer, ShowMouseTip, 1 ; "undelayed"
}

;; ---------------------------------------------------------------------------
RequestMouseTipUpdate()
{
  global LastMouseX, LastMouseY

  ; this forces the mouse tip to get updated next timer tick
  LastMouseX := LastMouseY := 0
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
    SetTimer, ShowMouseTip, %MouseTooltipInGameUpdateEveryMs%

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

      ;tip := ""
      ;. (LastSelectedFile ? LastSelectedFilename . " complete.`n`nTo begin, hit Alt+F and select a CSV file.`nAlt+E will run " . LastSelectedFilename . " again." : "Quickfort " . Version . "`nhttp://sun2design.com/quickfort`n`nTo begin, hit Alt+F and select a CSV file.")
      ;. "`n`nAlt+H hides/shows this tooltip.`nAlt+T opens QF command line.`nShift+Alt+Z suspends/resumes QF.`nShift+Alt+X exits QF."

      ToolTip, %FullTip%, xpos, ypos

      ;tip := "[" SelectedFilename "]" . (RepeatPattern ? "`n** REPEATING: " RepeatPattern " **" : "") . "`n"
      ;if (StartPosAbsX > 0)
      ;{
      ;  tip := tip . "START POSITION:" . (StartPosComment ? " " . StartPosComment : "") . " (" . StartPosAbsX . ", " . StartPosAbsY . ")"
      ;}
      ;else
      ;{
      ;  tip := tip . "Start corner: " . StartPosLabel . (StartPosComment ? "`nUse Alt+E to reset start position." : "")
      ;}

      xpos += 25
      ;if (ypos + 170 > ScreenHeight)
      ;  ypos -= 170 ; put tooltip above mouse pointer if we're near the bottom
      ;else
      ;  ypos += 10 ; below

      ;ToolTip, %tip%, xpos, ypos
    }
  }
  return
}

;; ---------------------------------------------------------------------------
HideMouseTip:
  ClearTip()
  HideTip()
  return

;; ---------------------------------------------------------------------------
ClearMouseTip:
  ClearTip()
  return
