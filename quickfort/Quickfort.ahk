#SingleInstance force
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
Version := "2.00"


SetTitleMatchMode, 3
;Menu, Tray, MainWindow

if (!A_IsCompiled)
  Hotkey, #!C, CompileToExe

; -----------------------------
; Set system default options
; -----------------------------
; ... so players don't necessarily have to overwrite options.txt for new versions with new options:
DelayMultiplier := 1
KeyPressDuration := 1
EmbeddedDelayDuration := 250
SendMode := "ControlSend"
KeyExitMenu := "{Esc}"
KeyLeft := "4"
KeyRight := "6"
KeyUp := "8"
KeyDown := "2"
KeyUpZ := "+5"
KeyDownZ := "^5"
KeyUpLeft := "7"
KeyUpRight := "9"
KeyDownLeft := "1"
KeyDownRight := "3"
UseDiagonalMoveKeys := 1
UseLongConstructions := 1
DisableBacktrackingOptimization := 0
DisableKeyOptimizations := 0
DisableShiftOptimizations := 1
ShowSplashBox := 1
ShowStartupTrayTip := 1
ShowMouseTooltip := 1
ShowCommentBox := 1
MutedSound := 0
DisableSafetyAbort := 0
MouseTooltipInGameUpdateEveryMs := 10
MouseTooltipPlaybackUpdateEveryMs := 500
MouseTooltipOutOfGameUpdateEveryMs := 50
AliasesPath := "aliases.txt"
DebugOn := 0


; -----------------------------
; Load options from options.txt (overrides above)
; -----------------------------

if (!FileExist("options.txt"))
{
  MsgBox, Error: Quickfort missing options.txt. Make sure options.txt exists and you are launching Quickfort from its own directory.`n`nExiting.
  ExitApp
}

Loop, Read, options.txt
{
  if (SubStr(A_LoopReadLine, 1, 1) != "#" && StrLen(A_LoopReadLine) > 3) ; skip comments and empty lines
  {
    StringSplit, optionsArray, A_LoopReadLine, `=, %A_Space%%A_Tab%
    if (optionsArray0 == 2) {
      %optionsArray1% := optionsArray2  ; sometimes AHK is pretty cool
    }
  }
}


ReadyToBuild := 0
Building := 0
Mode := ""
Comment := ""
LastSelectedFile := ""
SelectedFile := ""
SelectedFilename := ""
Tooltip := ""
StartPositionLabel := "Top left"
StartPos := 0
StartPosAbsX := 0
StartPosAbsY := 0
StartPosComment := ""
RepeatPattern =
ShowCSVIntro := 0
EvalMode := ""
EvalCommands := ""
MouseTipOn := 0
LastTooltip := ""
LastMouseX := 0
LastMouseY := 0
SuspendMouseTipOn := 0
HideTooltip := 0
Visualizing := 0

; Get display dimensions
SysGet, ScreenWidth, 16
SysGet, ScreenHeight, 17

ShowTip()

;;; ---------------------------------------------------------------------------
;;; Determine whether to show initial mouse tip
;if (ShowSplashBox)
;{
;  Tooltip := "" ; we don't set the actual splash text - that is assembled in ShowMouseTip when Tooltip is ""
;  MouseTipOn := 1
;  SetTimer, ShowMouseTip, %MouseTooltipInGameUpdateEveryMs%
;  ;SetTimer, HideMouseTip, -6000
;}
;else {
;  SetTimer, ShowMouseTip, 10
;  TurnMouseTipOff()
;}

if (ShowStartupTrayTip && !WinActive("Dwarf Fortress"))
{
  TrayTip, Quickfort, Version %Version%, , 1
}

return




;; ---------------------------------------------------------------------------
; Toggle suspend of the script (Shift-Alt-Z)
$+!Z::
  Suspend, Permit
  if (A_IsSuspended) {
    Suspend, Off
    ; show mouse tip if it was visible before
    if (SuspendMouseTipOn) {
      TurnMouseTipOn()
    }
  }
  else {
    ; store mouse tip state
    SuspendMouseTipOn := MouseTipOn
    TurnMouseTipOff()
    Suspend, On
  }
  return



#IfWinActive Dwarf Fortress



;; ---------------------------------------------------------------------------
; Intercept Ctrl-P command to DF and resend it. If sent manually, for large
; macros it causes DF to repeat the macro twice with a single Ctrl-P press.
; QF can send a single Ctrl-P that will not cause DF to repeat the macro.
$^p::
  Tip("interception complete")
  Send ^p
  return


;; ---------------------------------------------------------------------------
; Exit the script (Shift-Alt-X)
$+!X::
  TurnMouseTipOff()
  ExitApp
  return

;; ---------------------------------------------------------------------------
; Reload the script (Shift-Alt-R)
$+!R::
  Reload
  return

;; ---------------------------------------------------------------------------
; Hide/show mousetip
$!H::
  SwitchNoticeShown := 1
  if (HideTooltip) {
    HideTooltip := 0
    ForceMouseTipUpdate()
  }
  else {
    HideTooltip := 1
    Tooltip,
  }
  return

;; ---------------------------------------------------------------------------
; Cancel build (Alt+C)
$!C::
  Critical
  ;TurnMouseTipOff()
  SwitchNoticeShown := 1
  if (ReadyToBuild)
  {
    ReadyToBuild := 0
    Building := 0
    RepeatPattern =
    Tooltip := "Build Cancelled!"
    ForceMouseTipUpdate()
    SetTimer, ClearMouseTip, -1750
  }
  return

;; ---------------------------------------------------------------------------
; Start position switch
$!Q::
  SetStartPos(0, "Top left")
  return

;; ---------------------------------------------------------------------------
$!W::
  SetStartPos(1, "TOP RIGHT")
  return

;; ---------------------------------------------------------------------------
$!A::
  SetStartPos(2, "BOTTOM LEFT")
  return

;; ---------------------------------------------------------------------------
$!S::
  SetStartPos(3, "BOTTOM RIGHT")
  return

;; ---------------------------------------------------------------------------
; Helper to mass-demolish misplaced constuctions
$!X::
  Send {x 30}
  return

;; ---------------------------------------------------------------------------
; redo last construction effort (Alt+E)
; Only does anything after a build finishes (successfully or cancelled)
!E::
  if (!ReadyToBuild)
  {
    if (LastSelectedFile = "")
    {
      Goto ShowFilePicker
      return ; gratuitous
    }

    SelectedFile := LastSelectedFile
    ReadyToBuild := True
    UpdateTip()
  }
  ;else
  ;{
  ;  ; Re-enable use of the start() specification from the blueprint
  ;  SetStartPos(0, "Top left")
  ;  StartPosAbsX := LastStartPosAbsX
  ;  StartPosAbsY := LastStartPosAbsY
  ;  ForceMouseTipUpdate()
  ;}
  return

;; Autorepeat build (Alt+R)
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

    if (!RegExMatch(pattern, "^(\d*([dunsew]|flip[vh]|rotc?cw|\!)\s*)+$"))
    {
      MsgBox, Invalid transformation syntax:`n%pattern%
    }
    else
    {
      RepeatPattern := LastRepeatPattern := pattern
      UpdateTip()
    }
  }
  return


;; One-off command line (Alt+T)
;$!T::
;  SwitchNoticeShown := 1
;   if (!Building)
;   {
;    command := ""
;    msg =
;    (
;Syntax: mode command(,command2,command3)
;  mode should be one of (dig build place query) or (d b p q)
;  commands can be DF key-commands or QF aliases

;Examples:
;  build b,b,b,b,b      # build a row of 5 beds
;  dig i,h                  # then use Alt+R 10 down for mineshaft
;  query booze         # make a food stockpile only carry booze
;  q growlastcropall  # set a plot to grow plumps (usually)
;    )
;    InputBox, command, Quickfort Command Line, %msg%, , 400, 260 , , , , , %lastCommand%
;    ActivateGameWin()

;    if (command != "")
;    {
;      evalOK := RegExMatch(command, "S)^([bdpq])\w*\s+(.+)", evalMatch)
;      if (!evalOK)
;      {
;        MsgBox, Error: Command '%command%' syntax error: not of form [b|d|p|q] cmd(,cmd2,..,cmdN)
;        ActivateGameWin()
;        Exit
;      }
;      else
;      {
;        StartPosAbsX =
;        StartPosAbsY =
;        StartPosComment =
;        SetStartPos(0, "Top left")

;        EvalMode := evalMatch1
;        EvalCommands := evalMatch2 . ",#"

;        Comment := ""
;        ShowCSVIntro := 0

;        ; for next time
;        lastCommand := command

;        ; pretty print your command
;        SelectedFilename := command

;        ; "Eval" the command
;        BuildRoutine()
;      }
;    }
;  }
;  return


;;; ---------------------------------------------------------------------------
;; Visualize mode (Alt+V)
;$!V::
;  if (ReadyToBuild && !Building)
;  {
;    Visualizing := 1
;    BuildRoutine()
;    Visualizing := 0
;  }
;  return

;; ---------------------------------------------------------------------------
; File picker (Alt+F)
!F::
ShowFilePicker:
  if (!Building && !ReadyToBuild)
  {
    SelectedFile := SelectFile()
    if (SelectedFile)
      ReadyToBuild := True
    ShowTip()
  }
  return

;; ---------------------------------------------------------------------------
; Build starter (Alt+D)
!D::
  if (!Building && ReadyToBuild)
  {
    Building := True
    ConvertFile(SelectedFile, RepeatPattern)
    ExecuteMacro()
    ; TODO copy file here? rename ConvertFile to GenerateMacro and extract qfconvert executor to new method
    ;data := ConvertFile(SelectedFile, RepeatPattern)
    ;if (data)
    ;  SendKeys(data)
    Building := False
    ReadyToBuild := False
    LastSelectedFile := SelectedFile
    ; get the filename on its own
    SplitPath, LastSelectedFile, LastSelectedFilename

    SelectedFile =
    If (RepeatPattern)
      LastRepeatPattern := RepeatPattern
    RepeatPattern =
    UpdateTip()
  }
  return

;; ---------------------------------------------------------------------------
;; file picker
SelectFile()
{
  global
  local filename =

  ; show file selection box
  HideTip()
  FileSelectFile, filename, , , Select a Quickfort blueprint file to open, Blueprints (*.xls`; *.xlsx`; *.csv)
  ActivateGameWin()
  return filename
}

;; ---------------------------------------------------------------------------
;; execute macro by sending keys to DF window
ExecuteMacro()
{
  ActivateGameWin()
  ReleaseModifierKeys()
  Send ^l
  Sleep 500
  Send {Enter}
  Sleep 1000
  Send ^p
  return
}

;; ---------------------------------------------------------------------------
;; do blueprint conversion via qfconvert
ConvertFile(filename, transformation)
{
  Tip("Thinking...")

  transcmd =
  if (transformation) {
    transcmd = --transform="%transformation%"
  }

  ; We use macro names that should always go in decreasing sort order in DF's UI
  ; (between reboots); and we always delete our macros after use. However DF doesn't
  ; update its macro list when macros are deleted; thus the desire to have our new
  ; macro always be sorted to the top item in DF's macro list. It allows QF to just
  ; use Ctrl+L, Enter to select our just-created macro.
  inverseticks := 4294967296 - A_TickCount
  title = @@@qf%inverseticks%
  titlecmd = --title="%title%"
  outfile := A_ScriptDir "\" title ".mak"
  ;FileDelete, %outfile%

  cmd = "c:\lang\Python26\python" "d:\code\Quickfort\trunk\qfconvert\qfconvert.py" "%filename%" "%outfile%" %transcmd% %titlecmd%

  ;MsgBox %cmd%
  RunWait %cmd%, , Hide

  ready := False
  Loop 10
  {
    If FileExist(outfile) {
      ready = True
      break
    }
    Sleep 250
  }

  if (!ready)
  {
    MsgBox, Error: qfconvert did not return any results.
    return
  }

  ; Read converter results
  FileRead, output, %outfile%

  ; Check for exceptions
  Loop, Read, %outfile%
  {
    if (RegExMatch(A_LoopReadLine, "Exception:"))
    {
      ; Inform the user.
      StringReplace, output, output, Exception:, Error:
      StringReplace, output, output, \n, `n
      MsgBox % output
      ClearTip()
      return ""
    }
    else
    {
      ; Copy to DF dir
      FileCopy, %outfile%, A:\games\dwarffortress3104\data\init\macros\
      ; TODO check for err
    }
    break
  }

  ClearTip()
  ;return output
}

HideTip()
{
  TurnMouseTipOff()
}

ShowTip()
{
  UpdateTip()
  TurnMouseTipOn()
}

Tip(value)
{
  global
  Tooltip := value
  UpdateTip()
}

ClearTip()
{
  global
  Tooltip := ""
  UpdateTip()
}

UpdateTip()
{
  global
  local mode, header, body

  ; Determine tip mode.
  if (!SelectedFile)
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
    header := "details about the blueprint and selected modes`nrepeat: " . RepeatPattern
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
      body := "Alt+V shows area size. Alt+D starts building."
    }
    else
    {
      body := "--"
    }
  }

  FullTip := header "`n`n" body "`n`n" mode
}

;; ---------------------------------------------------------------------------
;; send keystrokes to game window
SendKeys(keys)
{
  global
  ActivateGameWin()
  Sleep, 250
  Sleep, 0

  ; Count total number of % chars
  StringSplit, pctarray, keys, `%
  numPctChars := pctarray0

  SetKeyDelay, KeyDelay, KeyPressDuration
  SetKeyDelay, 1, 1, Play

  Loop, parse, keys, `%
  {
    pctDone := Floor((A_Index/numPctChars) * 100)

    if (!Visualizing)
    {
      Tooltip = Quickfort running (%pctDone%`%)`nHold Alt+C to cancel.
      ForceMouseTipUpdateDelayed()
    }

    Sleep, 0
    Sleep, KeyDelay
    if (!ReadyToBuild)
    {
      ; build was cancelled by user.
      break
    }

    keys := A_LoopField

    UseSafeMode := 0
    ch := SubStr(keys, 1, 1)
    asc := Asc(ch)

    if ((ch = "^" || ch = "+" || ch = "!" || ch = "<" || ch = ">" || SubStr(keys, 1, 6) = "{Shift" || (asc >= 65 && asc <= 90)) && SendMode = "ControlSend") {
      ; We have to use special handling when send mode is ControlSend and we have to send modifier keys; ControlSend
      ; fails miserably when such modifier keys are sent.
      UseSafeMode := 1
    }

    if (keys = "wait")
    {
      ;Sleep, (DelayMultiplier * 5)
      ;MsgBox, %EmbeddedDelayDuration%
      Sleep, %EmbeddedDelayDuration%
    }
    else
    {
      if (!DisableSafetyAbort)
      {
        IfWinNotActive Dwarf Fortress
        {
          ; prevent mass sending keys to wrong window (no reliable way to make DF receive all keys in background; ControlSend is flaky w/ DF)
          Building := 0
          TurnMouseTipOff()
          msg := "Macro aborted!`n`nYou switched windows. The Dwarf Fortress window must be focused while Quickfort is running.`n`n"
            . (Mode = "b" ? "Use Alt+X to send the x key 30 times to DF (useful for destructing aborted builds).`n`n" : "")
            . (EvalMode ? "Hit Alt+f to choose a .csv file." : "Hit Alt+F to choose another .csv file. `nHit Alt+E to redo the same .csv file again.")
            . "`nHit Alt+T to enter a command directly.`n`nShift+Alt+Z suspends/resumes Quickfort hotkeys.`nShift+Alt+X exits QF."
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
      else { ; SendMode = "ControlSend"
        ReleaseModifierKeys()
        ControlSend,, %keys% ,Dwarf Fortress
        BlockInput, Off
      }
    }
  }
}


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
      BlockInput, On
      Sleep 250
      ControlSend,, {Alt up}{Ctrl up}{Shift up}{LWin up}{RWin up},Dwarf Fortress
      Sleep 250
    }
    else
      break
  }
  return
}

;BuildRoutine()
;{
;      ; Extract mode, start() param if any, and comment if any
;      RegExMatch(firstline, "S)^#(\w+)( +start\(.+?\))?( .+)?", modeLineMatch)
;      FullMode := modeLineMatch1
;      Mode := Substr(modeLineMatch1, 1, 1)

;      Comment := modeLineMatch3
;      Comment := TrimSpaces(Comment) ; trim spaces off
;      Comment := RegExReplace(Comment, "S),{2,}") ; throw out unwanted strings of commas
;      Comment := RegExReplace(Comment, "S),+$") ; discard any trailing commas
;      Comment := RegExReplace(Comment, "S)\\n", "`n") ; Turn \\n into `n (AHK-style newline)

;      startParam := modeLineMatch2

;      StartPosAbsX := 0
;      StartPosAbsY := 0
;      LastStartPosAbsX := 0
;      LastStartPosAbsY := 0
;      StartPosComment := ""

;      if (startParam)
;      {
;        ; Author specified start(x, y, comment) parameter
;        RegExMatch(startParam, "S)start\( *(\d+) *; *(\d+) *;? *(.+)? *\)", startParamMatch)

;        StartPosAbsX := startParamMatch1
;        StartPosAbsY := startParamMatch2
;        StartPosComment := startParamMatch3
;      }

;      ; get the filename on its own
;      SplitPath, SelectedFile, SelectedFilename
;    }

;    startKeys := ""

;    ; -----------------------------
;    ; Show instruction/comment box
;    ; -----------------------------
;    if (Mode = "b")
;    {
;      userInitKey = b o
;      userInitText = build road
;      startKeys := "{ExitMenu}%"
;      KeyDelay := DelayMultiplier * 3
;    }
;    else if (Mode = "d")
;    {
;      userInitKey = d
;      userInitText = designations
;      KeyDelay := DelayMultiplier
;    }
;    else if (Mode = "p")
;    {
;      userInitKey = p
;      userInitText = stockpiles
;      KeyDelay := DelayMultiplier * 2
;    }
;    else if (Mode = "q")
;    {
;      userInitKey = q
;      userInitText = set building tasks/prefs
;      KeyDelay := DelayMultiplier * 2
;    }
;    else
;    {
;      MsgBox, Unrecognized mode '%fullMode%' specified in %SelectedFilename%. Mode should be one of #build #dig #place #query
;      TurnMouseTipOn()
;      Exit
;    }

;    ReadyToBuild := 1

;    ; -----------------------------
;    ; Show CSV comment box
;    ; -----------------------------
;    if (ShowCommentBox && ShowCSVIntro)
;    {
;      countText := CountCommands(SelectedFile)
;      countText = %countText% ; whitespace trim
;      msg = %SelectedFilename% (%FullMode% mode)`n`n
;      if (StartPosAbsX > 0)
;        msg := msg . "Starts at:" . (StartPosComment ? " " . StartPosComment : "") . " (" . StartPosAbsX . ", " . StartPosAbsY . ")`n`n"
;      msg := msg Comment "`n`n" countText "Use Ctrl+C to copy this text."
;      MsgBox, 1, Quickfort - %SelectedFilename% [%FullMode%], %msg%
;      IfMsgBox Cancel
;      {
;        ReadyToBuild := 0
;        TurnMouseTipOn()
;        Exit
;      }
;      ActivateGameWin()
;    }


;    ; -----------------------------
;    ; Show howto mouse-tip
;    ; -----------------------------
;    Tooltip := "TYPE " . userInitKey . " (" . userInitText . "). Position cursor with KEYBOARD.`n`n"
;             . "Alt+V shows footprint.`n"
;             . "Alt+D starts playback.`n`n"
;             . "Alt+R for repeat mode.`n"
;             . "Alt+Q/W/A/S sets starting corner.`n"
;             . "Alt+C cancels."
;    TurnMouseTipOn()
;    Exit
;  }
;  ; else:


;  ; -----------------------
;  ; Start the build process
;  ; -----------------------
;  Building := 1
;  if (!Visualizing) Tooltip = Quickfort running (hold Alt+C to cancel)


;  ; -----------------------------
;  ; Load aliases from aliases.txt, if any (would be nice to put into a function but AHK global arrays are weird)
;  ; -----------------------------
;  aliasArrayCount := 0
;  Log("`nLoading aliases..")
;  Loop, Read, %AliasesPath%
;  {
;    if (StrLen(A_LoopReadLine) <= 2 || SubStr(A_LoopReadLine, 1, 1) = "#")
;      continue

;    aliases1 = aliases2 = ""
;    StringSplit, aliases, A_LoopReadLine, `,

;    ; drop leading or trailing spaces
;    aliases1 := RegExReplace(aliases1, "S)^\s*(.+)\s*$", "$1")
;    aliases2 := RegExReplace(aliases2, "S)^\s*(.+)\s*$", "$1")

;    Log("`n" . aliases1 . ", " . aliases2)
;    aliasArrayKey%A_Index% := aliases1
;    aliasArrayValue%A_Index% := aliases2
;    aliasArrayCount := A_Index
;  }
;  Log("`nDone.`n`n")

;  ; -------------------------------------
;  ; Correct for start position (Alt+QWAS);
;  ; determine width and height of blueprint
;  ; -------------------------------------
;  if (EvalMode)
;  {
;    ; count the number of commas (columns)
;    StringSplit, evalarr, EvalCommands, `,
;    width := evalarr0 - 1
;    height := 1
;  }
;  else
;  {
;    FileReadLine, firstline, %SelectedFile%, 2
;    StringSplit, firstarr, firstline, `,
;    width := firstarr0 - (RegExMatch(firstline, "S),#$") ? 1 : 0) ; make # at end of rows optional
;    height := 0
;    Loop, Read, %SelectedFile%
;    {
;      ; remove quotes
;      StringReplace, row, A_LoopReadLine, ", , 1

;      StringMid, firstchar, row, 1, 1
;      StringMid, first2chars, row, 1, 2

;      if(firstchar != "#")
;        height++
;      else if (first2chars = "#>" || first2chars = "#<")
;        break  ; we assume all floors in a multifloor layout are the same dimensions here
;    }
;  }


;  if (StartPosAbsX > 0) {
;    moves := GetCursorMoves(-StartPosAbsX + 1, -StartPosAbsY + 1, 0)
;  }
;  else {
;    ; Start corner mode
;    ; Initial moves are just to get to the top left corner if not there already.
;    moves := GetMovesFromCornerToCorner(StartPos, 0, width, height)
;  }

;  if (Visualizing)
;  {
;    moves := moves . "%wait%%wait%" . GetCursorMoves(width-1, 0, 0)
;      . "%wait%%wait%" . GetCursorMoves(0, height-1, 0)
;      . "%wait%%wait%" . GetCursorMoves(-width+1, 0, 0)
;      . "%wait%%wait%" . GetCursorMoves(0, -height+1, 0)
;      . "%wait%"

;    if (StartPosAbsX > 0)
;    {
;      moves := moves . GetCursorMoves(StartPosAbsX - 1, StartPosAbsY - 1, 0)
;    }

;    ; put us back in the position we started from
;    moves := moves . GetMovesFromCornerToCorner(0, StartPos, width, height)

;    output := TransformDiagonalKeys(moves)
;  }
;  else
;  {
;    output := startKeys
;    lastSubmenu := ""
;    rowNum := 0
;    zLevel := 0

;    ; -----------------------------------------
;    ; Build dataArray from file or EvalCommands
;    ; -----------------------------------------
;    if (EvalMode)
;    {
;      Log("Storing EvalCommands " . EvalCommands . " in dataArray`n`n")

;      dataArray1 := EvalCommands
;      dataArray2 := "#"
;      dataArrayCount := 2
;    }
;    else
;    {
;      ; read data from file
;      Log("Reading from " . SelectedFile . " into dataArray`n`n")
;      dataArrayCount := 0
;      Loop, Read, %SelectedFile%
;      {
;        if (A_Index > 1) ; skip the first line, which is the mode specifier/comment row
;        {
;          row := A_LoopReadLine

;          ; make sure every row ends in # (end-of-row specifier)
;          if (!RegExMatch(row, "S),#$")) {
;            row := row . ",#"
;          }

;          dataArrayCount++
;          dataArray%dataArrayCount% := row
;        }
;      }

;      ; make sure our dataArray ends with a #,#,# row (end of file marker)
;      if (!RegExMatch(dataArray%dataArrayCount%, "S)^[#, ]+$"))
;      {
;        dataArrayCount++
;        dataArray%dataArrayCount% := "#" . RepeatStr(",#", width)
;      }
;    }



;    ; -----------------------------
;    ; Main row loop
;    ; -----------------------------
;    Loop %dataArrayCount%
;    {
;      outputRow := ""
;      lastAction := ""

;      row := dataArray%A_Index%
;      rowNum++

;      ; remove quotes
;      StringReplace, row, row, ", , 1

;      ; if whole row is blank except for #'s (so just [,# ]) then add a {Down} to the moves string and skip the rest of cell processing.
;      if (RegExMatch(row, "S)^[,# ]+$"))
;      {
;        moves := moves . "{D}"
;        continue
;      }

;      ; row level "pre"-optimizations
;      if (Mode = "b" && UseLongConstructions)
;      {
;        ; turn 4-10 repetitions of objects like walls (Cw) into long constructions (works faster)
;        ; we don't do this for dirt roads because dirt roads can't be placed on tiles without soil
;        ; which breaks most long construction attempts on the surface
;        longItem1 = Cw
;        longItem2 = Cf
;        longItem3 = CF
;        longItem4 = Cr
;        longItem5 = o
;        longItemCount := 5
;        Loop %longItemCount%
;        {
;          longItem := longItem%A_Index%
;          Loop 7 {
;            reps := 11 - A_Index ; reps will go from 10 to 4 in single steps, so we do the longest bits first
;            needle := "S)(" longItem ",){" reps "}"
;            replaceWith := longItem "(" reps "x1)" RepeatStr(",", reps)
;            row := RegExReplace(row, needle, replaceWith)
;          }
;        }
;      }

;      colNum := 0

;      ; -------------------------------------------
;      ; Cell loop
;      ; -------------------------------------------
;      Loop, parse, row, `, ; loop over substrings separated by commas
;      {
;        each := ""
;        afterEach := ""
;        outputCell := ""
;        action := TrimSpaces(A_LoopField)
;        colNum++

;        ; alias substitution
;        Loop %aliasArrayCount% {
;          if (aliasArrayKey%A_Index% == action)
;            action := aliasArrayValue%A_Index%
;        }

;        action := ConvertToNumpadKeys(action) ; convert {/} to {NumpadDiv}, etc

;        ; commit last opened action in dig mode, if action has changed
;        if (Mode = "d" && lastAction != "" && lastAction != action)
;        {
;          outputRow := outputRow . "{Enter}%"
;          lastAction := ""
;        }

;        if (action = "#>" or action = "#<") {
;          ; multilevel blueprint. advance to the next z-level specified, reset cursor and continue.
;          dir := SubStr(action, 2, 1)
;          zLevel += (dir = "<" ?  1 : -1) ; relative z-level adjustment, higher ground = larger number. used by repeater code.
;          moves := moves . dir . RepeatStr("{U}", rowNum - 1)
;          rowNum := 0
;          break
;        }

;        else if (action = "#")
;        {
;          ; just move cursor to beginning of next row, don't do anything else here
;          moves := moves . RepeatStr("{L}", colNum - 1) . "{D}"
;          break
;        }
;        else if (action = "" || action = " " || action = "~" || action = "``")
;        {
;          ; blank spot, we'll just be moving the cursor. Note that ` and ~ serve as blank tiles; this is just to give layout designers
;          ; an option to mark some blank tiles differently. In a multilevel setup, a designer could design a general floorplan template
;          ; using ` and ~ in cells to specify where walls and stairs would be, and then base other floorplans/layers off that design.
;          moves := moves . "{R}"
;          lastAction := ""
;          continue
;        }
;        else
;        {
;          if (Mode != "b" && RegExMatch(action, "S)^(.+)\((\d+)x(\d+)\)(.*)", rangeMatch) > 0) {
;            ; Matches commands of the form a(4x6), which would place a 4 wide x 6 tall
;            ; animal stockpile in place mode, using the cursor keys to size it. Object
;            ; will be placed with its top-left corner tile at the present cursor
;            ; position. Full format is C(WxH)C where C are keystrokes, W is object
;            ; width and H is object height
;            each := "&" . rangeMatch1
;                    . "{Enter}" . RepeatStr("{D}", rangeMatch3 - 1) . RepeatStr("{R}", rangeMatch2 - 1) . "{Enter}"
;                    . RepeatStr("{U}", rangeMatch3 - 1) . RepeatStr("{L}", rangeMatch2 - 1)
;                    . rangeMatch4
;          }
;          else if (Mode = "d") {
;            if (lastAction == action)
;            {
;              ; performing same action as last tile. We'll just move right
;              each := "&"
;            }
;            else if (lastAction == "")
;            {
;              ; no last action, so we need to press the command and then enter now to start placing
;              each := "&@{Enter}%"
;              lastAction := action
;            }
;            else {
;              ; we have a last action and it's different than this tile's action.
;              ; we already took care of committing the last action earlier, so just act like normal here.
;              each := "&@{Enter}%"
;              lastAction := action
;            }
;          }
;          else if (Mode = "p") {
;            each := "%@{Enter}%&"
;          }
;          else if (Mode = "q") {
;            ; Enter is not always needed for query, but it doesn't hurt when it isn't.
;            ; A more refined approach would be to adjust this on a per command basis.
;            each := "&@{Enter}%"
;          }
;          else if (Mode = "b") {
;            if (action == "p") {
;              ; farm plots don't have a materials list
;              each := "@&{Enter}%wait%"
;            }
;            else if (action == "wf" || action == "wv" || action == "D") {
;              ; Placing wf, wv, Ms require extra regular Enters (others?).
;              each := "@&{Enter}%wait%{Enter}%wait%+{Enter}%wait%"
;            }
;            else if (SubStr(action, 1, 2) == "Ms") {
;              each := "@&{Enter}{Enter}{Enter}{Enter}%wait%"
;            }
;            else {
;              each := "@&{Enter}{Enter}%wait%" ; all other buildings require 2 enters
;            }

;            if (RegExMatch(action, "S)^([CMTwe])(.+)$", submenuMatch)) {
;              ; Build submenus handling

;              if (submenuMatch1 == lastSubmenu) {
;                ; still in the same submenu as last time. don't need to send submenu opening key again.
;                action := subMenuMatch2
;              }
;              else if (lastSubmenu != "") {
;                ; changing from one menu to another. Need to exit current menu with space before entering new submenu.
;                action := "{ExitMenu}%" . action
;              }

;              lastSubmenu := submenuMatch1
;              inSubMenu := 1
;            }
;            else {
;              ; this wasn't a submenu command. If lastSubmenu has a value now, we need to send Space to get out of that submenu before the next command.
;              if (lastSubmenu != "")
;              {
;                action := "{ExitMenu}%" action
;                lastSubmenu := ""
;              }

;              ; if /^[dgx]/, we are placing a door, bridge or floodgate. These toggleable pathfinding obstacles can
;              ; cause DF to lag for a moment just after placement.
;              ;if (RegExMatch(action, "S)^[dgx]")) {
;              ;  action := action . "%wait%"
;              ;}
;              inSubMenu := 0
;            }

;            if (RegExMatch(action, "S)^(.+)\((\d+)x(\d+)\)(.*)", rangeMatch) > 0) {
;              ; Matches commands of the form ga(4x6), which would place a 4 wide x 6 tall bridge which raises to the left.
;              ; Object will be placed with its top-left corner tile at the present cursor position.
;              ; Full format is C(WxH)C where C are keystrokes, W is object width and H is object height
;              each :=   rangeMatch1
;                    . moves
;                    . RepeatStr("{R}", rangeMatch2 // 2)
;                    . RepeatStr("{D}", rangeMatch3 // 2)
;                    . (rangeMatch3 > 1 ? RepeatStr("u", rangeMatch3 - 1) : "")
;                    . (rangeMatch2 > 1 ? RepeatStr("k", rangeMatch2 - 1) : "")
;                    . "{Enter}%wait%+{Enter}%wait%"

;              ; store moves needed to get us back into the current next-cursor position for next command's move portion
;              moves :=  RepeatStr("{U}", rangeMatch3 // 2)
;                      . RepeatStr("{L}", rangeMatch2 // 2)
;                      . rangeMatch4
;            }
;          }

;          ; perform the cell action.


;          ; Sub the cell value into @ and the move key(s) for this cell into &
;          StringReplace, each, each, @, %action%

;          if (Instr(each, "&")) {
;            ; Only sub in moves and clear moves string if there is a & in each; otherwise we want to keep moves for next iteration
;            StringReplace, each, each, &, %moves%
;            moves := ""
;          }

;          ; append cell output (each) to row so far
;          outputRow := outputRow . each

;          ; add R to moves to get us Right onto the spot we need next iteration
;          moves := moves . "{R}"

;        }
;      }

;      ; append row output to final output
;      output := output . outputRow

;    }

;    ; put us back in the position we started from
;    moves := moves . "{U}{U}" . GetMovesFromCornerToCorner(2, StartPos, width, height)

;    ; add any remaining (unsent) moves
;    if (Mode = "b")
;    {
;      output := output
;        . (inSubMenu ? "{ExitMenu}%" : "")
;        . "O%"   ; use dirt road (b O) to reposition cursor reliably
;        . moves
;    }
;    else
;    {
;      output := output . moves
;    }



;    ; ------------------
;    ; handle repeat mode
;    ; ------------------
;    if (RepeatPattern)
;    {
;      ; correct for start() pos
;      if (StartPosAbsX > 0)
;        output := output . GetCursorMoves(StartPosAbsX - 1, StartPosAbsY - 1, 0)

;      ; repeat our blueprint as requested
;      output := RepeatKeyPattern(output, RepeatPattern, height, width, zLevel + 1)
;    }

;    Log("`n`nBefore keystroke optimizations: " . output)
;    output := OptimizeKeystrokes(output)
;  }

;  Log("`n`nBefore keystroke transformations: " . output)
;  output := TransformKeystrokes(output)

;  Log("`n`nFinal output: " . output)

;  if (!Visualizing)
;  {
;    Tooltip = Thinking...
;    TurnMouseTipOn()

;    FileDelete, %A_ScriptDir%\pyout.txt
;    RunWait %comspec% /c ""c:\lang\Python26\python" "d:\code\Quickfort\trunk\QuickfortPy\qfconvert.py" "%SelectedFile%" "%A_ScriptDir%\pyout.txt"", , Hide

;    Loop 10
;    {
;      If FileExist(A_ScriptDir "\pyout.txt")
;        Goto ConversionSuccessful
;      Sleep 250
;    }
;    MsgBox, Error: QuickfortPy did not return any results.
;    return

;    ConversionSuccessful:
;    FileRead, output, %A_ScriptDir%\pyout.txt

;    ; Migrate SelectedFile to LastSelected file now, so if the user cancels we'll still have it for use with Alt+E (redo).
;    LastSelectedFile := SelectedFile
;    SelectedFile := ""

;    ; Show busy mousetip
;    Tooltip = Quickfort running... (hold Alt+C to cancel)
;    TurnMouseTipOn()
;  }

  ; Send it chunk style, breaking up Sends between % chars to give user a chance to cancel with Alt+C
  ; If a chunk is just "wait" (i.e. %wait%) we'll sleep for a bit (for those CPU intensive actions in DF).
  ; ------------------------------------------------------------------------------------------------------
  ;if (!DebugOn)
  ;{
  ;  ActivateGameWin()
  ;  Sleep, 250
  ;  Sleep, 0

  ;  ; Count total number of % chars
  ;  StringSplit, pctarray, output, `%
  ;  numPctChars := pctarray0

  ;  SetKeyDelay, KeyDelay, KeyPressDuration
  ;  SetKeyDelay, 1, 1, Play

  ;  Loop, parse, output, `%
  ;  {
  ;    pctDone := Floor((A_Index/numPctChars) * 100)

  ;    if (!Visualizing)
  ;    {
  ;      Tooltip = Quickfort running (%pctDone%`%)`nHold Alt+C to cancel.
  ;      ForceMouseTipUpdateDelayed()
  ;    }

  ;    Sleep, 0
  ;    Sleep, KeyDelay
  ;    if (!ReadyToBuild)
  ;    {
  ;      ; build was cancelled by user.
  ;      break
  ;    }

  ;    keys := A_LoopField

  ;    UseSafeMode := 0
  ;    ch := SubStr(keys, 1, 1)
  ;    asc := Asc(ch)

  ;    if ((ch = "^" || ch = "+" || ch = "!" || ch = "<" || ch = ">" || SubStr(keys, 1, 6) = "{Shift" || (asc >= 65 && asc <= 90)) && SendMode = "ControlSend") {
  ;      ; We have to use special handling when send mode is ControlSend and we have to send modifier keys; ControlSend
  ;      ; fails miserably when such modifier keys are sent.
  ;      UseSafeMode := 1
  ;    }

  ;    if (keys = "wait")
  ;    {
  ;      ;Sleep, (DelayMultiplier * 5)
  ;      ;MsgBox, %EmbeddedDelayDuration%
  ;      Sleep, %EmbeddedDelayDuration%
  ;    }
  ;    else
  ;    {
  ;      if (!DisableSafetyAbort)
  ;      {
  ;        IfWinNotActive Dwarf Fortress
  ;        {
  ;          ; prevent mass sending keys to wrong window (no reliable way to make DF receive all keys in background; ControlSend is flaky w/ DF)
  ;          Building := 0
  ;          TurnMouseTipOff()
  ;          msg := "Macro aborted!`n`nYou switched windows. The Dwarf Fortress window must be focused while Quickfort is running.`n`n"
  ;            . (Mode = "b" ? "Use Alt+X to send the x key 30 times to DF (useful for destructing aborted builds).`n`n" : "")
  ;            . (EvalMode ? "Hit Alt+f to choose a .csv file." : "Hit Alt+F to choose another .csv file. `nHit Alt+E to redo the same .csv file again.")
  ;            . "`nHit Alt+T to enter a command directly.`n`nShift+Alt+Z suspends/resumes Quickfort hotkeys.`nShift+Alt+X exits QF."
  ;          MsgBox, %msg%
  ;          break
  ;        }
  ;      }

  ;      ; actually send the keys!
  ;      if (UseSafeMode)
  ;      {
  ;        ;MsgBox % "safe mode on " keys
  ;        ; Make sure the DF window is active

  ;        ActivateGameWin()

  ;        ; Send desired keys "safely"
  ;        SetKeyDelay, 150, 25
  ;        Send %keys%
  ;        SetKeyDelay, KeyDelay, KeyPressDuration
  ;        ;SetKeyDelay, KeyDelay, KeyPressDuration, Play
  ;      }
  ;      else if (SendMode = "SendPlay")
  ;        SendPlay %keys%
  ;      else if (SendMode = "SendInput")
  ;        SendInput %keys%
  ;      else if (SendMode = "Send")
  ;        Send %keys%
  ;      else if (SendMode = "SendEvent")
  ;        SendEvent %keys%
  ;      else { ; SendMode = "ControlSend"
  ;        Loop {
  ;          if (GetKeyState("Alt") || GetKeyState("Ctrl") || GetKeyState("Shift") || GetKeyState("LWin") || GetKeyState("RWin"))
  ;          {
  ;            ; Try to avoid the modifier keys screwing up our playback if the user presses them.
  ;            KeyWait, Alt
  ;            KeyWait, Ctrl
  ;            KeyWait, Shift
  ;            KeyWait, LWin
  ;            KeyWait, RWin
  ;            BlockInput, On
  ;            Sleep 250
  ;            ControlSend,, {Alt up}{Ctrl up}{Shift up}{LWin up}{RWin up},Dwarf Fortress
  ;            Sleep 250
  ;          }
  ;          else
  ;            break
  ;        }
  ;        ControlSend,, %keys% ,Dwarf Fortress
  ;        BlockInput, Off
  ;      }
  ;    }
  ;  }
  ;}


;  ForceMouseTipUpdate()

;  if (Visualizing) {
;    Building := 0
;    return
;  }

;  ; Reset repeat pattern.
;  RepeatPattern =

;  ; Show "completed" popup box if option is set and user didn't cancel first
;  Sleep, 0
;  if (ShowCompletedBox && ReadyToBuild && Building && 0) ; DISABLED: Interferes with mousetip being up all the time.
;  {
;    msg := "Macro completed.`n`n"
;      . (EvalMode ? "Hit Alt+f to choose a .csv file." : "Hit Alt+F to choose another .csv file. `nHit Alt+E to redo the same .csv file again.")
;      . "`nHit Alt+T to enter a command directly.`n`nShift+Alt+Z suspends/resumes Quickfort hotkeys.`nShift+Alt+X exits QF."
;    MsgBox, %msg%
;  }

;  if (!MuteCompletedSound)
;  {
;    SoundPlay *64 ; "asterisk"
;  }

;  ; Show file selection box next time Alt+D is hit
;  ReadyToBuild := 0
;  Building := 0

;  ; Clear Eval stuff, tooltip
;  EvalCommand := EvalMode := Tooltip := ""

;  return
;}



;----------------------------------------------------
; Helper Functions
;----------------------------------------------------

;; ---------------------------------------------------------------------------
RepeatReplace(subject, pattern, replace)
{
  Loop {
    StringReplace, subject, subject, %pattern%, %replace%, UseErrorLevel
    if (ErrorLevel = 0)
      break
  }
  return subject
}

;; ---------------------------------------------------------------------------
SetStartPos(position, label)
{
  global StartPos, StartPositionLabel, StartPosAbsX, StartPosAbsY, LastStartPosAbsX, LastStartPosAbsY
  StartPos := position
  StartPositionLabel := label
  ForceMouseTipUpdate()

  if (StartPosAbsX > 0) {
    LastStartPosAbsX := StartPosAbsX
    LastStartPosAbsY := StartPosAbsY
    StartPosAbsX := StartPosAbsY := 0
  }
}



;; ---------------------------------------------------------------------------
RepeatStr(str, count)
{
  output := ""
  Loop %count%
  {
    output = %output%%str%
  }
  return output
}

;; ---------------------------------------------------------------------------
TrimSpaces(str)
{
  str := RegExReplace(str ,"S)^ +")
  str := RegExReplace(str ,"S) +$")

  return str
}

;; ---------------------------------------------------------------------------
Log(debugstr)
{
    global DebugOn
    FileAppend, %debugstr%, debug.txt
}


;; ---------------------------------------------------------------------------
TurnMouseTipOn()
{
  global
  MouseTipOn := 1
  SetTimer, ShowMouseTip, %MouseTooltipInGameUpdateEveryMs%
  ;SetTimer, HideMouseTip, Off ; make sure a timed mouse tip hiding event (e.g. the splash tip) doesn't close a different tip
  Sleep 50 ; let the timer tick a bit, so the tip gets updated right after being turned on (Send can block the timer otherwise)
  ForceMouseTipUpdate()
}

;; ---------------------------------------------------------------------------
TurnMouseTipOff()
{
  global
  SetTimer, ShowMouseTip, Off
  MouseTipOn := 0
  ToolTip,
}

;; ---------------------------------------------------------------------------
ForceMouseTipUpdate()
{
  ForceMouseTipUpdateDelayed()
  SetTimer, ShowMouseTip, 1 ; "undelayed"
}

;; ---------------------------------------------------------------------------
ForceMouseTipUpdateDelayed()
{
  global LastMouseX, LastMouseY

  ; this forces the mouse tip to get updated next timer tick
  LastMouseX := LastMouseY := 0
}

;; ---------------------------------------------------------------------------
ShowMouseTip:
{
  CoordMode, Mouse, Screen
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
      ;  tip := tip . "Start corner: " . StartPositionLabel . (StartPosComment ? "`nUse Alt+E to reset start position." : "")
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
  TurnMouseTipOff()
  Tooltip := ""
  return

;; ---------------------------------------------------------------------------
ClearMouseTip:
  Tooltip := ""
  return

;; ---------------------------------------------------------------------------
CompileToExe:
  CompileToExeFunc()
  return

CompileToExeFunc()
{
  global Version

  if (A_IsCompiled)
    return

  MsgBox, Compiling as version %Version%
  icon := A_ScriptDir . ReplaceExtension(A_ScriptName, ".ico")

  MsgBox, "c:\Program Files (x86)\AutoHotkey\Compiler\Ahk2Exe.exe" /in "%A_ScriptFullPath%" /icon "%icon%"

  FileDelete, Quickfort.exe
  RunWait, "c:\Program Files (x86)\AutoHotkey\Compiler\Ahk2Exe.exe" /in "%A_ScriptFullPath%" /icon "%icon%"

  FileDelete, releases\Quickfort.zip
  FileDelete, releases\Quickfort_%Version%.zip
  Sleep 1000

  RunWait, zip -9 -r releases\Quickfort.zip aliases.txt Blueprints options.txt Quickfort.ahk Quickfort.exe readme.txt
  Sleep 1000

  FileCopy, releases\Quickfort.zip, releases\Quickfort_%Version%.zip
  Sleep 1000

  Run, releases\Quickfort_%Version%.zip

  MsgBox, 4, , Upload?

  IfMsgBox Yes
  {
    to := "m:\sun2design.com\quickfort\"
    FileCopy, releases\Quickfort_%Version%.zip, %to%, 1
    FileCopy, releases\Quickfort.zip, %to%, 1
    FileCopy, readme.txt, %to%, 1
    Run, http://sun2design.com/quickfort
  }
}

;; ---------------------------------------------------------------------------
ReplaceExtension(path, newExtension)
{
  SplitPath, path, , , , fileNoExt
  SplitPath, path, , dir
  result := dir . "\" . fileNoExt . newExtension
  return result
}

;; ---------------------------------------------------------------------------
ActivateGameWin()
{
  If (!WinActive("Dwarf Fortress"))
  {
    WinActivate, Dwarf Fortress
    SendInput {Alt up}{Ctrl up}{Shift up}
  }
}