;; Hotkey definitions.

;; ---------------------------------------------------------------------------
;; Toggle suspend of the script (Shift-Alt-Z) while also letting it pass
;; through to OS
~$+!Z::
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
;; Toggle mini/full tip
!M::
  ShowFullTip := !ShowFullTip
  UpdateTip()
  SaveAppState()
  return


;; ---------------------------------------------------------------------------
;; Cancel build (Alt+C)
$!C::
  Critical
  if (Building)
  {
    Building := 0
    Tooltip := "Build Cancelled!"
    UpdateTip()
    SetTimer, ClearMouseTip, -1750
  }
  return


;; ---------------------------------------------------------------------------
;; Set start corner with Alt+Q/W/A/S or unset with Alt+Z
!Q:: SetStartPos("nw", "North-west corner")
!W:: SetStartPos("ne", "North-east corner")
!A:: SetStartPos("sw", "South-west corner")
!S:: SetStartPos("se", "South-east corner")
!Z:: SetStartPos("", "") ; unset start corner


;; ---------------------------------------------------------------------------
;; Helper to mass-demolish misplaced constuctions
!X::
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
;; Switch playback mode (Alt+K)
!K::
  if (!Building)
  {
    if (PlaybackMode = "macro")
      PlaybackMode := "key"
    else
      PlaybackMode := "macro"
    SaveAppState()
    UpdateTip()
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
    
    if ErrorLevel ; user clicked cancel button
    {
      RepeatPattern = ; clear out any existing repeat pattern
      UpdateTip()
      return
    }

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

    pattern = %pattern% ; magic AHK whitespace trim

    if (RegExMatch(pattern, "^((\d*([dunsew]|flip[vh]|rotc?cw|\!)|halign=([lmr]|left|middle|right)|valign=([tmb]|top|middle|bottom))\s*)+$"))
    {
      RepeatPattern := LastRepeatPattern := pattern
      SaveAppState()
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
      RepeatPattern =
      CommandLineMode := False
      SetSelectedFile(newfile)

      ; save change to app state (SelectedFolder)
      SaveAppState()

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
$!D::
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
$!V::
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


;; ---------------------------------------------------------------------------
;; One-off command line (Alt+T)
$!T::
   if (!Building)
   {
    command := ""
    msg =
    (
Syntax: mode cmd1(,cmd2,cmd3,...)(#cmd1,....)
  - mode should be one of (dig build place query) or (d b p q)
  - cmds can be DF key-commands or QF aliases
  - separate multiple rows with #

Examples:
  build b,b,b,b,b      # build a row of 5 beds
  dig i,h                  # then use Alt+R, 10d for a mineshaft
  query booze         # make a food stockpile only carry booze
  q growlastcropall  # set a plot to grow plumps (usually)
  d d,d#d,d           # dig a 2x2 square
    )
    InputBox, command, Quickfort Command Line, %msg%, , 400, 300 , , , , , %LastCommandLine%
    ActivateGameWin()

    if ErrorLevel ; user clicked cancel button
    {
      EvalCommands =
      EvalMode =
      CommandLineMode := False
      ReadyToBuild := False
      UpdateTip()
      return
    }

    if (command != "")
    {
      evalOK := RegExMatch(command, "S)^([bdpq])\w*\s+(.+)", evalMatch)
      if (!evalOK)
      {
        MsgBox, Error: Invalid command syntax`nExpected: [b|d|p|q] cmd(,cmd2,..,cmdN)(#cmd,...)`n`n%command%
        ActivateGameWin()
        Exit
      }
      else
      {
        StartPosAbsX := 0
        StartPosAbsY := 0
        StartPosComment =
        SetStartPos(0, "Top left")

        if (evalMatch1 == "b")
          EvalMode := "build"
        else if (evalMatch1 == "d")
          EvalMode := "dig"
        else if (evalMatch1 == "p")
          EvalMode := "place"
        else if (evalMatch1 == "q")
          EvalMode := "query"

        EvalCommands := evalMatch2

        outfile := A_ScriptDir "\" GetRandomFileName() ".csv"
        WriteCommandLineToCSVFile(EvalMode, EvalCommands, outfile)
        SetSelectedFile(outfile)
        SetVarsByBuildType(EvalMode)

        CommandLineMode := True
        ReadyToBuild := True
        
        ; persistently remember last command entered here
        LastCommandLine := command
        SaveAppState()

        ShowCSVIntro := False
        RepeatPattern =

        UpdateTip()
      }
    }
  }
  return
