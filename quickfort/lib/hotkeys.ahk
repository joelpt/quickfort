;; Hotkey definitions.

;; ---------------------------------------------------------------------------
;; Dynamically a few hotkeys that are controlled through options.txt
InitHotkeys()
{
  global KeyMacroPlay, KeyMacroLoad, KeyMacroSave, KeyMacroRecord

  Hotkey, IfWinActive, Dwarf Fortress

  ; $ means don't catch this key if we generate it
  Hotkey, $%KeyMacroPlay%, MacroPlayKeyPressed, On 
  
  ; ~ means don't eat this key if pressed (let them pass through to the DF window)
  Hotkey, ~%KeyMacroLoad%, MacroKeyPressed, On
  Hotkey, ~%KeyMacroSave%, MacroKeyPressed, On
  Hotkey, ~%KeyMacroRecord%, MacroKeyPressed, On
  
  return
}


;; ---------------------------------------------------------------------------
;; Intercept Ctrl-P command to DF and send it ourselves. If sent manually, for large
;; macros it causes DF to repeat the macro twice with a single Ctrl-P press.
;; QF can send a single Ctrl-P that will not cause DF to repeat the macro.
MacroPlayKeyPressed:
{
  ReleaseModifierKeys()
  Send %KeyMacroPlay%
  LastMacroWasPlayed := false
  return
}

;; ---------------------------------------------------------------------------
;; Detect use of Ctrl+S/L/R and reset LastMacroWasPlayed when it happens
MacroKeyPressed:
{
  LastMacroWasPlayed := false
  return
}

;; ---------------------------------------------------------------------------
;; Toggle suspend of the script (Shift-Alt-Z) while also letting it pass
;; through to OS
#IfWinActive ; any window not just DF
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
  LastMacroWasPlayed := false
  LastSendKeys =
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
    LastMacroWasPlayed := false
    LastSendKeys =
  }
  return

;; ---------------------------------------------------------------------------
;; Switch playback mode (Alt+K)
!K::
  LastMacroWasPlayed := false
  LastSendKeys =
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

  Syntax: #D #D #D ... where D is one of:
    n s e w u d flipv fliph rotcw rotccw ! halign=.. valign=..

  Examples:
    2e 2s
    rotcw
    fliph 2e flipv 2s

Enter ? for more help.
    )

    InputBox, pattern, Transform blueprint, %msg%, , 440, 300, , , , , %LastRepeatPattern%
    ActivateGameWin()
    
    LastMacroWasPlayed := false
    LastSendKeys =

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
Base syntax: [#]D [[#]D [#]D...]
  # = times to repeat action, defaults to 1 if omitted
  D = one of: n s e w u d flipv fliph rotcw rotccw !
  Any number of transformations can be chained together.
  #d/#u transforms (multi z-level) are always performed last.

Alignment codes can be used to specify chaining alignments.
  halign=left|middle|right|l|m|r
  valign=top|middle|bottom|t|m|b

Examples:
  4e -- make a row of the blueprint repeated 4 times going east
  3e 3s -- 3x3 repeating pattern of blueprint
  5e 5s 5d -- 5x5x5 cube of blueprint (multi z level)
  rotcw -- rotate the blueprint clockwise 90 degrees
  fliph -- flip the blueprint horizontally
  fliph 2e flipv 2s -- 2x2 symmetrical pattern of blueprint
  rotcw 2e flipv fliph 2s -- 2x2 rotated around a center point
  rotcw valign=top 2e -- after rotating, top-align and repeat 2e
  rotcw ! 2e -- rotate original blueprint, then repeat that 2x east
  valign=m halign=m rotcw 2e flipv fliph 2s 2e 2s 2d -- big example

Read the Quickfort user manual for more details.

Enter transformation pattern below.
      )
      InputBox, pattern, Transform blueprint, %msg%, , 440, 520, , , , , %LastRepeatPattern%
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
    LastMacroWasPlayed := false
    LastSendKeys =
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

    ;; Check if file was modified before testing if we can replay last macro played
    if (!CommandLineMode && SelectedModifiedOn)
    {
      FileGetTime, currentModifiedOn, %SelectedFile%, M
      if (SelectedModifiedOn != currentModifiedOn)
      {
        LastMacroWasPlayed := false
        LastSendKeys := false
        SelectedModifiedOn := currentModifiedOn
      }
    }

    ;; initiate playback based on PlaybackMode and whether we can just replay
    ;; the last macro/keys
    if (PlaybackMode == "macro")
    {
      if (LastMacroWasPlayed)
      {
        ; just play the last played macro
        Send %KeyMacroPlay%
      }
      else
      {
        ConvertAndPlayMacro()
      }
    }
    else if (LastSendKeys)
    {
      SendKeys(LastSendKeys)
    }
    else
    {
      ConvertAndSendKeys(false)
    }

    If (RepeatPattern)
      LastRepeatPattern := RepeatPattern ; remembered for transform GUI's default

    Building := False
    ClearTip()
  }
  return
}


;; ---------------------------------------------------------------------------
;; Save named macro (Alt+N)
$!N::
{
  if (Building || !ReadyToBuild)
  {
    return
  }
  
  if (PlaybackMode != "macro")
  {
    MsgBox, Alt+N only works in macro output mode. Use Alt+K to change output modes.
    return
  }

  InputBox, title, Save named macro, Specify a name for the new macro., , , 130

  if (ErrorLevel || !title) ;; user clicked cancel or entered nothing
  {
    return
  }

  ConvertAndSaveMacro(title)
  MsgBox, Saved macro as '%title%' in DF macros folder.
  
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
    LastMacroWasPlayed := false
    LastSendKeys =
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
  dig d,d#d,d          # dig a 2x2 square
    )
    InputBox, command, Quickfort Command Line, %msg%, , 400, 300 , , , , , %LastCommandLine%
    ActivateGameWin()

    LastMacroWasPlayed := false
    LastSendKeys =

    if ErrorLevel ; user clicked cancel button
    {
      EvalCommands =
      EvalMode =
      CommandLineMode := False
      CommandLineFile =
      ;ReadyToBuild := False
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

        ; Clean last CommandLineFile if any
        if (CommandLineFile)
          FileDelete, %CommandLineFile%
          
        outfile := A_ScriptDir "\" GetRandomFileName() ".csv"
        WriteCommandLineToCSVFile(EvalMode, EvalCommands, outfile)
        ;SetSelectedFile(outfile)
        CommandLineFile := outfile
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
