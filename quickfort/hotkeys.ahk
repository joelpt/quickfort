;; Hotkey definitions.

;; ---------------------------------------------------------------------------
;; Toggle suspend of the script (Shift-Alt-Z)
$+!Z::
  Suspend, Permit
  if (A_IsSuspended) {
    Suspend, Off
    ; show mouse tip if it was visible before
    if (SuspendMouseTipOn) {
      ShowTip()
    }
  }
  else {
    ; store mouse tip state
    SuspendMouseTipOn := MouseTipOn
    HideTip()
    Suspend, On
  }
  return


;; ---------- remaining commands only work when DF window is active ----------
#IfWinActive Dwarf Fortress

;; ---------------------------------------------------------------------------
;; Intercept Ctrl-P command to DF and send it ourselves. If sent manually, for large
;; macros it causes DF to repeat the macro twice with a single Ctrl-P press.
;; QF can send a single Ctrl-P that will not cause DF to repeat the macro.
$^p:: Send ^p


;; ---------------------------------------------------------------------------
;; Exit the script (Shift-Alt-X)
+!X::
  HideTip()
  ExitApp
  return


;; ---------------------------------------------------------------------------
;; Reload the script (Shift-Alt-R)
+!R::
  Reload
  return


;; ---------------------------------------------------------------------------
;; Hide/show mousetip
!H::
  if (HideTooltip) {
    HideTooltip := 0
    ShowTip()
  }
  else {
    HideTooltip := 1
    HideTip()
  }
  return


;; ---------------------------------------------------------------------------
;; Cancel build (Alt+C)
!C::
  Critical
  if (Building)
  {
    ReadyToBuild := 0
    Building := 0
    Tooltip := "Build Cancelled!"
    UpdateTip()
    SetTimer, ClearMouseTip, -1750
  }
  return


;; ---------------------------------------------------------------------------
;; Set start corner with Alt+Q/W/A/S or unset with Alt+Z
$!Q:: SetStartPos("nw", "North-west corner")
$!W:: SetStartPos("ne", "North-east corner")
$!A:: SetStartPos("sw", "South-west corner")
$!S:: SetStartPos("se", "South-east corner")
$!Z:: SetStartPos("", "") ; unset start corner


;; ---------------------------------------------------------------------------
;; Helper to mass-demolish misplaced constuctions
$!X::
  Send {x 30}
  return


;; ---------------------------------------------------------------------------
;; Switch worksheet (Alt+E)
!E::
  if (!Building && SelectedFile)
  {
    ShowSheetInfoGui()
  }
  return


;; ---------------------------------------------------------------------------
;; Repeat/transform (Alt+R)
!R::
  if (!Building && ReadyToBuild)
  {
    msg =
    (
Enter transformation pattern below.

  Syntax: #D #D #D ...
    where D is one of: n s e w u d flipv fliph rotcw rotccw !
  Examples:
    4e 4s;  2n 2w 2d;  fliph 2e flipv 2s

Enter ? for more help.
    )

    InputBox, pattern, Transform blueprint, %msg%, , 440, 260, , , , , %LastRepeatPattern%
    ActivateGameWin()
    if (RegExMatch(pattern, "^(help|\?)"))
    {
      msg =
      (
Enter transformation pattern below.

Syntax: [#]D [[#]D [#]D...]
  # = times to repeat action, defaults to 1 if omitted
  D = one of: n s e w u d flipv fliph rotcw rotccw !
  Any number of transformations can be chained together.
  #d/#u transforms (multi z-level) are always performed last.

Examples:
  4e -- make a row of the blueprint repeated 4 times going east
  3e 3s -- 3x3 repeating pattern of blueprint
  5e 5s 5d -- 5x5x5 cube of blueprint (multi z level)
  fliph -- flip the blueprint horizontally
  rotcw -- rotate the blueprint clockwise 90 degrees
  fliph 2e flipv 2s -- 2x2 symmetrical pattern of blueprint
  rotcw 2e flipv fliph 2s -- 2x2 rotated around a center point
  rotcw ! 2e -- rotate original blueprint then repeat that 2x east
      )
      InputBox, pattern, Transform blueprint, %msg%, , 440, 400, , , , , %LastRepeatPattern%
      ActivateGameWin()
    }

    pattern = %pattern% ; whitespace trim

    if (RegExMatch(pattern, "^(\d*([dunsew]|flip[vh]|rotc?cw|\!)\s*)+$"))
    {
      RepeatPattern := LastRepeatPattern := pattern
      UpdateTip()
    }
    else if (!pattern)
    {
      RepeatPattern =
      UpdateTip()
    }
    else
    {
      MsgBox, Invalid transformation syntax:`n%pattern%
    }
  }
  return


;; ---------------------------------------------------------------------------
;; File picker (Alt+F)
!F::
ShowFilePicker:
{
  if (!Building)
  {
    newfile := SelectFile()
    if (newfile)
    {
      SelectedFile := newfile
      SelectedSheetIndex =
      RepeatPattern =

      ; get the filename on its own for use by mousetip
      SplitPath, SelectedFile, SelectedFilename

      if (GetBlueprintInfo(SelectedFile))
      {
        SelectedSheetIndex =
        ShowSheetInfoGui()
      }
    }
  }
  return
}


;; ---------------------------------------------------------------------------
;; Build starter (Alt+D)
!D::
{
  if (!Building && ReadyToBuild)
  {
    Building := True
    Tip("Building...")

    if (PlaybackMode == "macro")
      ConvertAndPlayMacro()
    else
      ConvertAndSendKeys(false)

    If (RepeatPattern)
      LastRepeatPattern := RepeatPattern ; remembered for transform GUI default

    Building := False
    ClearTip()
  }
  return
}


;; ---------------------------------------------------------------------------
;; Visualize blueprint's footprint (Alt+V)
!V::
{
  if (!Building && ReadyToBuild)
  {
    Building := True
    Tip("Visualizing...")
    ConvertAndSendKeys(true)
    Building := False
    ClearTip()
  }
  return
}

