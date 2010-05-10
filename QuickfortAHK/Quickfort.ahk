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


ReadyToGo := 0
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


;; ---------------------------------------------------------------------------
;; Determine whether to show initial mouse tip
if (ShowSplashBox)
{
  Tooltip := "" ; we don't set the actual splash text - that is assembled in ShowMouseTip when Tooltip is ""
  MouseTipOn := 1
  SetTimer, ShowMouseTip, %MouseTooltipInGameUpdateEveryMs%
  ;SetTimer, HideMouseTip, -6000
}
else {
  SetTimer, ShowMouseTip, 10
  TurnMouseTipOff()
}

if (ShowStartupTrayTip && !WinActive("Dwarf Fortress"))
{
  TrayTip, Quickfort, Version %Version%, , 1
}

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
  if (ReadyToGo)
  {
    ReadyToGo := 0
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
$!E::
  if (!ReadyToGo)
  {
    if (LastSelectedFile = "")
    {
      MsgBox, No file selected yet. Use Alt+D to select a file, or Alt+T to enter a command directly.`n`nShift+Alt+Z suspends/resumes Quickfort hotkeys.
      ActivateGameWin()
      return
    }

    SelectedFile := LastSelectedFile
    ShowCSVIntro := 0
    ForceMouseTipUpdate()
    BuildRoutine()
  }
  else
  {
    ; Re-enable use of the start() specification from the blueprint
    SetStartPos(0, "Top left")
    StartPosAbsX := LastStartPosAbsX
    StartPosAbsY := LastStartPosAbsY
    ForceMouseTipUpdate()
  }
  return

; Autorepeat build (Alt+R)
$!R::
  if (!Building && ReadyToGo)
  {
    msg =
    (
Enter repeat pattern below.

Syntax: #D
  # is the number of times to repeat in a direction
  D is north|south|east|west|up|down or one of nsewud
  Up to 3 directions (dimensions) can be specified.

Examples:
    4 north       - repeat blueprint 4 times to the north
    3e 3s          - make a 3x3 pattern of our repeated blueprint
    10e 10s 4d  - repeat a 10x10 pattern 4 z-levels down (10x10x4)
    )
    InputBox, pattern, Auto-repeat blueprint, %msg%, , 440, 300
    ;InputBox, pattern, Auto-repeat blueprint, %msg%
    if (!RegExMatch(pattern, "S)^(\d+\s*[dunsew]\w*\s*)+$", pattern)) {
      MsgBox, Repeat pattern not in correct format.
    }
    else {
      RepeatPattern := pattern
      ForceMouseTipUpdate()
    }
  }
  ActivateGameWin()
  return


; One-off command line (Alt+T)
$!T::
  SwitchNoticeShown := 1
   if (!Building)
   {
    command := ""
    msg =
    (
Syntax: mode command(,command2,command3)
  mode should be one of (dig build place query) or (d b p q)
  commands can be DF key-commands or QF aliases

Examples:
  build b,b,b,b,b      # build a row of 5 beds
  dig i,h                  # then use Alt+R 10 down for mineshaft
  query booze         # make a food stockpile only carry booze
  q growlastcropall  # set a plot to grow plumps (usually)
    )
    InputBox, command, Quickfort Command Line, %msg%, , 400, 260 , , , , , %lastCommand%
    ActivateGameWin()

    if (command != "")
    {
      evalOK := RegExMatch(command, "S)^([bdpq])\w*\s+(.+)", evalMatch)
      if (!evalOK)
      {
        MsgBox, Error: Command '%command%' syntax error: not of form [b|d|p|q] cmd(,cmd2,..,cmdN)
        ActivateGameWin()
        Exit
      }
      else
      {
        StartPosAbsX =
        StartPosAbsY =
        StartPosComment =
        SetStartPos(0, "Top left")

        EvalMode := evalMatch1
        EvalCommands := evalMatch2 . ",#"

        Comment := ""
        ShowCSVIntro := 0

        ; for next time
        lastCommand := command

        ; pretty print your command
        SelectedFilename := command

        ; "Eval" the command
        BuildRoutine()
      }
    }
  }
  return


;; ---------------------------------------------------------------------------
; Visualize mode (Alt+V)
$!V::
  if (ReadyToGo && !Building)
  {
    Visualizing := 1
    BuildRoutine()
    Visualizing := 0
  }
  return

;; ---------------------------------------------------------------------------
; Build starter (Alt+D)
$!D::
  SwitchNoticeShown := 1
  if (!Building)
  {
    if (!ReadyToGo)
    {
      ShowCSVIntro := 1
      SelectedFile := "" ; clear this if we aren't about to build, or in the process of it (ReadyToGo).
    }
    BuildRoutine()
  }
  return

;; ---------------------------------------------------------------------------
; and its routine
BuildRoutine()
{
  global
  static startKeys

  Critical, Off
  FileDelete, debug.txt
  TurnMouseTipOff()

  ; BuildRoutine will behave differently if ReadyToGo is set or not. If not set it will prompt for a filename (unless
  ; Alt+T was used to provide a direct command). If set, it will actually do the build.
  if (!ReadyToGo)
  {
    ; -----------------------------
    ; Show file UI / determine mode and comment
    ; -----------------------------

    Mode := ""
    Comment := ""

    ; if we have an EvalCommand (Alt+T), stick with that.
    if (EvalMode)
    {
      Mode := EvalMode
    }
    else
    {
      ; show a file selection box if SelectedFile is blank. If user presses Alt+E after a build, SelectedFile will not be blank.
      if (SelectedFile == "")
      {
        SelectedFilename := ""

        ; show file selection box
        FileSelectFile, SelectedFile, , , Select a Quickfort .csv file to open, Quickfort CSV Files (*.csv)

        ActivateGameWin()

        if (!SelectedFile)
        {
          ; DISABLED: We'll just keep showing the mousetip now instead.
          ;MsgBox, No file selected. Use Alt+D again to select a Quickfort .csv file, or Alt+T to enter a command directly.`n`nShift+Alt+Z suspends/resumes QF.
          TurnMouseTipOn()
          Exit
        }
      }

      ; make sure we have a #mode line
      FileReadLine, firstline, %SelectedFile%, 1
      StringReplace, firstline, firstline, ", , 1
      if (!RegExMatch(firstline, "i)^#[dbpq]"))
      {
        MsgBox, Error: First line of .csv file must be one of: #dig #build #place #query (optionally followed by a space and a comment)`n`nUse Shift+Alt+Z to suspend/resume QF.
        Exit
      }

      ; Extract mode, start() param if any, and comment if any
      RegExMatch(firstline, "S)^#(\w+)( +start\(.+?\))?( .+)?", modeLineMatch)
      FullMode := modeLineMatch1
      Mode := Substr(modeLineMatch1, 1, 1)

      Comment := modeLineMatch3
      Comment := TrimSpaces(Comment) ; trim spaces off
      Comment := RegExReplace(Comment, "S),{2,}") ; throw out unwanted strings of commas
      Comment := RegExReplace(Comment, "S),+$") ; discard any trailing commas
      Comment := RegExReplace(Comment, "S)\\n", "`n") ; Turn \\n into `n (AHK-style newline)

      startParam := modeLineMatch2

      StartPosAbsX := 0
      StartPosAbsY := 0
      LastStartPosAbsX := 0
      LastStartPosAbsY := 0
      StartPosComment := ""

      if (startParam)
      {
        ; Author specified start(x, y, comment) parameter
        RegExMatch(startParam, "S)start\( *(\d+) *; *(\d+) *;? *(.+)? *\)", startParamMatch)

        StartPosAbsX := startParamMatch1
        StartPosAbsY := startParamMatch2
        StartPosComment := startParamMatch3
      }

      ; get the filename on its own
      SplitPath, SelectedFile, SelectedFilename
    }

    startKeys := ""

    ; -----------------------------
    ; Show instruction/comment box
    ; -----------------------------
    if (Mode = "b")
    {
      userInitKey = b o
      userInitText = build road
      startKeys := "{ExitMenu}%"
      KeyDelay := DelayMultiplier * 3
    }
    else if (Mode = "d")
    {
      userInitKey = d
      userInitText = designations
      KeyDelay := DelayMultiplier
    }
    else if (Mode = "p")
    {
      userInitKey = p
      userInitText = stockpiles
      KeyDelay := DelayMultiplier * 2
    }
    else if (Mode = "q")
    {
      userInitKey = q
      userInitText = set building tasks/prefs
      KeyDelay := DelayMultiplier * 2
    }
    else
    {
      MsgBox, Unrecognized mode '%fullMode%' specified in %SelectedFilename%. Mode should be one of #build #dig #place #query
      TurnMouseTipOn()
      Exit
    }

    ReadyToGo := 1

    ; -----------------------------
    ; Show CSV comment box
    ; -----------------------------
    if (ShowCommentBox && ShowCSVIntro)
    {
      countText := CountCommands(SelectedFile)
      countText = %countText% ; whitespace trim
      msg = %SelectedFilename% (%FullMode% mode)`n`n
      if (StartPosAbsX > 0)
        msg := msg . "Starts at:" . (StartPosComment ? " " . StartPosComment : "") . " (" . StartPosAbsX . ", " . StartPosAbsY . ")`n`n"
      msg := msg Comment "`n`n" countText "Use Ctrl+C to copy this text."
      MsgBox, 1, Quickfort - %SelectedFilename% [%FullMode%], %msg%
      IfMsgBox Cancel
      {
        ReadyToGo := 0
        TurnMouseTipOn()
        Exit
      }
      ActivateGameWin()
    }


    ; -----------------------------
    ; Show howto mouse-tip
    ; -----------------------------
    Tooltip := "TYPE " . userInitKey . " (" . userInitText . "). Position cursor with KEYBOARD.`n`n"
             . "Alt+V shows footprint.`n"
             . "Alt+D starts playback.`n`n"
             . "Alt+R for repeat mode.`n"
             . "Alt+Q/W/A/S sets starting corner.`n"
             . "Alt+C cancels."
    TurnMouseTipOn()
    Exit
  }
  ; else:


  ; -----------------------
  ; Start the build process
  ; -----------------------
  Building := 1
  if (!Visualizing) Tooltip = Quickfort running (hold Alt+C to cancel)


  ; -----------------------------
  ; Load aliases from aliases.txt, if any (would be nice to put into a function but AHK global arrays are weird)
  ; -----------------------------
  aliasArrayCount := 0
  Log("`nLoading aliases..")
  Loop, Read, %AliasesPath%
  {
    if (StrLen(A_LoopReadLine) <= 2 || SubStr(A_LoopReadLine, 1, 1) = "#")
      continue

    aliases1 = aliases2 = ""
    StringSplit, aliases, A_LoopReadLine, `,

    ; drop leading or trailing spaces
    aliases1 := RegExReplace(aliases1, "S)^\s*(.+)\s*$", "$1")
    aliases2 := RegExReplace(aliases2, "S)^\s*(.+)\s*$", "$1")

    Log("`n" . aliases1 . ", " . aliases2)
    aliasArrayKey%A_Index% := aliases1
    aliasArrayValue%A_Index% := aliases2
    aliasArrayCount := A_Index
  }
  Log("`nDone.`n`n")

  ; -------------------------------------
  ; Correct for start position (Alt+QWAS);
  ; determine width and height of blueprint
  ; -------------------------------------
  if (EvalMode)
  {
    ; count the number of commas (columns)
    StringSplit, evalarr, EvalCommands, `,
    width := evalarr0 - 1
    height := 1
  }
  else
  {
    FileReadLine, firstline, %SelectedFile%, 2
    StringSplit, firstarr, firstline, `,
    width := firstarr0 - (RegExMatch(firstline, "S),#$") ? 1 : 0) ; make # at end of rows optional
    height := 0
    Loop, Read, %SelectedFile%
    {
      ; remove quotes
      StringReplace, row, A_LoopReadLine, ", , 1

      StringMid, firstchar, row, 1, 1
      StringMid, first2chars, row, 1, 2

      if(firstchar != "#")
        height++
      else if (first2chars = "#>" || first2chars = "#<")
        break  ; we assume all floors in a multifloor layout are the same dimensions here
    }
  }


  if (StartPosAbsX > 0) {
    moves := GetCursorMoves(-StartPosAbsX + 1, -StartPosAbsY + 1, 0)
  }
  else {
    ; Start corner mode
    ; Initial moves are just to get to the top left corner if not there already.
    moves := GetMovesFromCornerToCorner(StartPos, 0, width, height)
  }

  if (Visualizing)
  {
    moves := moves . "%wait%%wait%" . GetCursorMoves(width-1, 0, 0)
      . "%wait%%wait%" . GetCursorMoves(0, height-1, 0)
      . "%wait%%wait%" . GetCursorMoves(-width+1, 0, 0)
      . "%wait%%wait%" . GetCursorMoves(0, -height+1, 0)
      . "%wait%"

    if (StartPosAbsX > 0)
    {
      moves := moves . GetCursorMoves(StartPosAbsX - 1, StartPosAbsY - 1, 0)
    }

    ; put us back in the position we started from
    moves := moves . GetMovesFromCornerToCorner(0, StartPos, width, height)

    output := TransformDiagonalKeys(moves)
  }
  else
  {
    output := startKeys
    lastSubmenu := ""
    rowNum := 0
    zLevel := 0

    ; -----------------------------------------
    ; Build dataArray from file or EvalCommands
    ; -----------------------------------------
    if (EvalMode)
    {
      Log("Storing EvalCommands " . EvalCommands . " in dataArray`n`n")

      dataArray1 := EvalCommands
      dataArray2 := "#"
      dataArrayCount := 2
    }
    else
    {
      ; read data from file
      Log("Reading from " . SelectedFile . " into dataArray`n`n")
      dataArrayCount := 0
      Loop, Read, %SelectedFile%
      {
        if (A_Index > 1) ; skip the first line, which is the mode specifier/comment row
        {
          row := A_LoopReadLine

          ; make sure every row ends in # (end-of-row specifier)
          if (!RegExMatch(row, "S),#$")) {
            row := row . ",#"
          }

          dataArrayCount++
          dataArray%dataArrayCount% := row
        }
      }

      ; make sure our dataArray ends with a #,#,# row (end of file marker)
      if (!RegExMatch(dataArray%dataArrayCount%, "S)^[#, ]+$"))
      {
        dataArrayCount++
        dataArray%dataArrayCount% := "#" . RepeatStr(",#", width)
      }
    }



    ; -----------------------------
    ; Main row loop
    ; -----------------------------
    Loop %dataArrayCount%
    {
      outputRow := ""
      lastAction := ""

      row := dataArray%A_Index%
      rowNum++

      ; remove quotes
      StringReplace, row, row, ", , 1

      ; if whole row is blank except for #'s (so just [,# ]) then add a {Down} to the moves string and skip the rest of cell processing.
      if (RegExMatch(row, "S)^[,# ]+$"))
      {
        moves := moves . "{D}"
        continue
      }

      ; row level "pre"-optimizations
      if (Mode = "b" && UseLongConstructions)
      {
        ; turn 4-10 repetitions of objects like walls (Cw) into long constructions (works faster)
        ; we don't do this for dirt roads because dirt roads can't be placed on tiles without soil
        ; which breaks most long construction attempts on the surface
        longItem1 = Cw
        longItem2 = Cf
        longItem3 = CF
        longItem4 = Cr
        longItem5 = o
        longItemCount := 5
        Loop %longItemCount%
        {
          longItem := longItem%A_Index%
          Loop 7 {
            reps := 11 - A_Index ; reps will go from 10 to 4 in single steps, so we do the longest bits first
            needle := "S)(" longItem ",){" reps "}"
            replaceWith := longItem "(" reps "x1)" RepeatStr(",", reps)
            row := RegExReplace(row, needle, replaceWith)
          }
        }
      }

      colNum := 0

      ; -------------------------------------------
      ; Cell loop
      ; -------------------------------------------
      Loop, parse, row, `, ; loop over substrings separated by commas
      {
        each := ""
        afterEach := ""
        outputCell := ""
        action := TrimSpaces(A_LoopField)
        colNum++

        ; alias substitution
        Loop %aliasArrayCount% {
          if (aliasArrayKey%A_Index% == action)
            action := aliasArrayValue%A_Index%
        }

        action := ConvertToNumpadKeys(action) ; convert {/} to {NumpadDiv}, etc

        ; commit last opened action in dig mode, if action has changed
        if (Mode = "d" && lastAction != "" && lastAction != action)
        {
          outputRow := outputRow . "{Enter}%"
          lastAction := ""
        }

        if (action = "#>" or action = "#<") {
          ; multilevel blueprint. advance to the next z-level specified, reset cursor and continue.
          dir := SubStr(action, 2, 1)
          zLevel += (dir = "<" ?  1 : -1) ; relative z-level adjustment, higher ground = larger number. used by repeater code.
          moves := moves . dir . RepeatStr("{U}", rowNum - 1)
          rowNum := 0
          break
        }

        else if (action = "#")
        {
          ; just move cursor to beginning of next row, don't do anything else here
          moves := moves . RepeatStr("{L}", colNum - 1) . "{D}"
          break
        }
        else if (action = "" || action = " " || action = "~" || action = "``")
        {
          ; blank spot, we'll just be moving the cursor. Note that ` and ~ serve as blank tiles; this is just to give layout designers
          ; an option to mark some blank tiles differently. In a multilevel setup, a designer could design a general floorplan template
          ; using ` and ~ in cells to specify where walls and stairs would be, and then base other floorplans/layers off that design.
          moves := moves . "{R}"
          lastAction := ""
          continue
        }
        else
        {
          if (Mode != "b" && RegExMatch(action, "S)^(.+)\((\d+)x(\d+)\)(.*)", rangeMatch) > 0) {
            ; Matches commands of the form a(4x6), which would place a 4 wide x 6 tall
            ; animal stockpile in place mode, using the cursor keys to size it. Object
            ; will be placed with its top-left corner tile at the present cursor
            ; position. Full format is C(WxH)C where C are keystrokes, W is object
            ; width and H is object height
            each := "&" . rangeMatch1
                    . "{Enter}" . RepeatStr("{D}", rangeMatch3 - 1) . RepeatStr("{R}", rangeMatch2 - 1) . "{Enter}"
                    . RepeatStr("{U}", rangeMatch3 - 1) . RepeatStr("{L}", rangeMatch2 - 1)
                    . rangeMatch4
          }
          else if (Mode = "d") {
            if (lastAction == action)
            {
              ; performing same action as last tile. We'll just move right
              each := "&"
            }
            else if (lastAction == "")
            {
              ; no last action, so we need to press the command and then enter now to start placing
              each := "&@{Enter}%"
              lastAction := action
            }
            else {
              ; we have a last action and it's different than this tile's action.
              ; we already took care of committing the last action earlier, so just act like normal here.
              each := "&@{Enter}%"
              lastAction := action
            }
          }
          else if (Mode = "p") {
            each := "%@{Enter}%&"
          }
          else if (Mode = "q") {
            ; Enter is not always needed for query, but it doesn't hurt when it isn't.
            ; A more refined approach would be to adjust this on a per command basis.
            each := "&@{Enter}%"
          }
          else if (Mode = "b") {
            if (action == "p") {
              ; farm plots don't have a materials list
              each := "@&{Enter}%wait%"
            }
            else if (action == "wf" || action == "wv" || action == "D") {
              ; Placing wf, wv, Ms require extra regular Enters (others?).
              each := "@&{Enter}%wait%{Enter}%wait%+{Enter}%wait%"
            }
            else if (SubStr(action, 1, 2) == "Ms") {
              each := "@&{Enter}{Enter}{Enter}{Enter}%wait%"
            }
            else {
              each := "@&{Enter}{Enter}%wait%" ; all other buildings require 2 enters
            }

            if (RegExMatch(action, "S)^([CMTwe])(.+)$", submenuMatch)) {
              ; Build submenus handling

              if (submenuMatch1 == lastSubmenu) {
                ; still in the same submenu as last time. don't need to send submenu opening key again.
                action := subMenuMatch2
              }
              else if (lastSubmenu != "") {
                ; changing from one menu to another. Need to exit current menu with space before entering new submenu.
                action := "{ExitMenu}%" . action
              }

              lastSubmenu := submenuMatch1
              inSubMenu := 1
            }
            else {
              ; this wasn't a submenu command. If lastSubmenu has a value now, we need to send Space to get out of that submenu before the next command.
              if (lastSubmenu != "")
              {
                action := "{ExitMenu}%" action
                lastSubmenu := ""
              }

              ; if /^[dgx]/, we are placing a door, bridge or floodgate. These toggleable pathfinding obstacles can
              ; cause DF to lag for a moment just after placement.
              ;if (RegExMatch(action, "S)^[dgx]")) {
              ;  action := action . "%wait%"
              ;}
              inSubMenu := 0
            }

            if (RegExMatch(action, "S)^(.+)\((\d+)x(\d+)\)(.*)", rangeMatch) > 0) {
              ; Matches commands of the form ga(4x6), which would place a 4 wide x 6 tall bridge which raises to the left.
              ; Object will be placed with its top-left corner tile at the present cursor position.
              ; Full format is C(WxH)C where C are keystrokes, W is object width and H is object height
              each :=   rangeMatch1
                    . moves
                    . RepeatStr("{R}", rangeMatch2 // 2)
                    . RepeatStr("{D}", rangeMatch3 // 2)
                    . (rangeMatch3 > 1 ? RepeatStr("u", rangeMatch3 - 1) : "")
                    . (rangeMatch2 > 1 ? RepeatStr("k", rangeMatch2 - 1) : "")
                    . "{Enter}%wait%+{Enter}%wait%"

              ; store moves needed to get us back into the current next-cursor position for next command's move portion
              moves :=  RepeatStr("{U}", rangeMatch3 // 2)
                      . RepeatStr("{L}", rangeMatch2 // 2)
                      . rangeMatch4
            }
          }

          ; perform the cell action.


          ; Sub the cell value into @ and the move key(s) for this cell into &
          StringReplace, each, each, @, %action%

          if (Instr(each, "&")) {
            ; Only sub in moves and clear moves string if there is a & in each; otherwise we want to keep moves for next iteration
            StringReplace, each, each, &, %moves%
            moves := ""
          }

          ; append cell output (each) to row so far
          outputRow := outputRow . each

          ; add R to moves to get us Right onto the spot we need next iteration
          moves := moves . "{R}"

        }
      }

      ; append row output to final output
      output := output . outputRow

    }

    ; put us back in the position we started from
    moves := moves . "{U}{U}" . GetMovesFromCornerToCorner(2, StartPos, width, height)

    ; add any remaining (unsent) moves
    if (Mode = "b")
    {
      output := output
        . (inSubMenu ? "{ExitMenu}%" : "")
        . "O%"   ; use dirt road (b O) to reposition cursor reliably
        . moves
    }
    else
    {
      output := output . moves
    }



    ; ------------------
    ; handle repeat mode
    ; ------------------
    if (RepeatPattern)
    {
      ; correct for start() pos
      if (StartPosAbsX > 0)
        output := output . GetCursorMoves(StartPosAbsX - 1, StartPosAbsY - 1, 0)

      ; repeat our blueprint as requested
      output := RepeatKeyPattern(output, RepeatPattern, height, width, zLevel + 1)
    }

    Log("`n`nBefore keystroke optimizations: " . output)
    output := OptimizeKeystrokes(output)
  }

  Log("`n`nBefore keystroke transformations: " . output)
  output := TransformKeystrokes(output)

  Log("`n`nFinal output: " . output)

  if (!Visualizing)
  {
    Tooltip = Thinking...
    TurnMouseTipOn()

    FileDelete, %A_ScriptDir%\pyout.txt
    RunWait %comspec% /c ""c:\lang\Python26\python" "d:\code\Quickfort\trunk\QuickfortPy\app_main.py" "%SelectedFile%" "%A_ScriptDir%\pyout.txt"", , Hide

    If FileExist(A_ScriptDir "\pyout.txt")
    {
      FileRead, output, %A_ScriptDir%\pyout.txt
    }
    Else
    {
      MsgBox, Error: QuickfortPy did not return any results.
      return
    }

    ; Migrate SelectedFile to LastSelected file now, so if the user cancels we'll still have it for use with Alt+E (redo).
    LastSelectedFile := SelectedFile
    SelectedFile := ""

    ; Show busy mousetip
    Tooltip = Quickfort running... (hold Alt+C to cancel)
    TurnMouseTipOn()
  }

  ; Send it chunk style, breaking up Sends between % chars to give user a chance to cancel with Alt+C
  ; If a chunk is just "wait" (i.e. %wait%) we'll sleep for a bit (for those CPU intensive actions in DF).
  ; ------------------------------------------------------------------------------------------------------
  if (!DebugOn)
  {
    ActivateGameWin()
    Sleep, 250
    Sleep, 0

    ; Count total number of % chars
    StringSplit, pctarray, output, `%
    numPctChars := pctarray0

    SetKeyDelay, KeyDelay, KeyPressDuration
    SetKeyDelay, 1, 1, Play

    Loop, parse, output, `%
    {
      pctDone := Floor((A_Index/numPctChars) * 100)

      if (!Visualizing)
      {
        Tooltip = Quickfort running (%pctDone%`%)`nHold Alt+C to cancel.
        ForceMouseTipUpdateDelayed()
      }

      Sleep, 0
      Sleep, KeyDelay
      if (!ReadyToGo)
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
              . (EvalMode ? "Hit Alt+D to choose a .csv file." : "Hit Alt+D to choose another .csv file. `nHit Alt+E to redo the same .csv file again.")
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
          Loop {
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
          ControlSend,, %keys% ,Dwarf Fortress
          BlockInput, Off
        }
      }
    }
  }


  ForceMouseTipUpdate()

  if (Visualizing) {
    Building := 0
    return
  }

  ; Reset repeat pattern.
  RepeatPattern =

  ; Show "completed" popup box if option is set and user didn't cancel first
  Sleep, 0
  if (ShowCompletedBox && ReadyToGo && Building && 0) ; DISABLED: Interferes with mousetip being up all the time.
  {
    msg := "Macro completed.`n`n"
      . (EvalMode ? "Hit Alt+D to choose a .csv file." : "Hit Alt+D to choose another .csv file. `nHit Alt+E to redo the same .csv file again.")
      . "`nHit Alt+T to enter a command directly.`n`nShift+Alt+Z suspends/resumes Quickfort hotkeys.`nShift+Alt+X exits QF."
    MsgBox, %msg%
  }

  if (!MuteCompletedSound)
  {
    SoundPlay *64 ; "asterisk"
  }

  ; Show file selection box next time Alt+D is hit
  ReadyToGo := 0
  Building := 0

  ; Clear Eval stuff, tooltip
  EvalCommand := EvalMode := Tooltip := ""

  return
}




; -----------------------
; Keystroke optimizer
; -----------------------
OptimizeKeystrokes(input)
{
  global
  local output := input

  if (!DisableKeyOptimizations)
  {
    ; Optimizations to eliminate several classes of movement redundancy.
    ; We run through this twice to be a little extra aggressive.
    Loop 2
    {
      ; Turn {L}{D}{R}, {L}{D}{D}{R}, ... into just {D}. Lets us avoid going to the beginning of the next row, etc.
      Loop 10
      {
        repeated := RepeatStr("{D}", A_Index)
        Loop 2
        {
          check := (A_Index == 1 ? "{L}" : "{R}") . repeated . (A_Index == 1 ? "{R}" : "{L}")
          output := RepeatReplace(output, check, repeated)
        }
      }

      ; Remove instances of {R}{L}, etc. pairs repeatedly until all gone from output (they'd cancel one another out).
      output := RepeatReplace(output, "{R}{L}", "")
      output := RepeatReplace(output, "{L}{R}", "")
      output := RepeatReplace(output, "{U}{D}", "")
      output := RepeatReplace(output, "{D}{U}", "")
      output := RepeatReplace(output, "><", "")
      output := RepeatReplace(output, "<>", "")

      if (!DisableShiftOptimizations)
      {
        ; Turn {R}x10 into +{R}|, etc. We insert a pipe symbol as a suffix to the replacement and will remove it later;
        ; it acts as a "bar" and makes sure we don't replace something that we already replaced in an earlier step.
        StringReplace, output, output, {R}{R}{R}{R}{R}{R}{R}{R}{R}{R}, +{R}`%|, 1
        StringReplace, output, output, {L}{L}{L}{L}{L}{L}{L}{L}{L}{L}, +{L}`%|, 1
        StringReplace, output, output, {U}{U}{U}{U}{U}{U}{U}{U}{U}{U}, +{U}`%|, 1
        StringReplace, output, output, {D}{D}{D}{D}{D}{D}{D}{D}{D}{D}, +{D}`%|, 1

        if (!DisableBacktrackingOptimization)
        {
          ; Turn {R}x9 into +{R}{L}, etc. This should be doable with a couple of loops, but this works for now.
          ; Could run into problems using these optimizations if you're building right next to the edge of the map,
          ; though it *should* still work fine since you can't build on the 3 tile "margin" around the edge anyway....
          StringReplace, output, output, {R}{R}{R}{R}{R}{R}{R}{R}{R}, +{R}`%{L}|, 1
          StringReplace, output, output, {R}{R}{R}{R}{R}{R}{R}{R}, +{R}`%{L}{L}|, 1
          StringReplace, output, output, {R}{R}{R}{R}{R}{R}{R}, +{R}`%{L}{L}{L}|, 1
          StringReplace, output, output, {L}{L}{L}{L}{L}{L}{L}{L}{L}, +{L}`%{R}|, 1
          StringReplace, output, output, {L}{L}{L}{L}{L}{L}{L}{L}, +{L}`%{R}{R}|, 1
          StringReplace, output, output, {L}{L}{L}{L}{L}{L}{L}, +{L}`%{R}{R}{R}|, 1
          StringReplace, output, output, {U}{U}{U}{U}{U}{U}{U}{U}{U}, +{U}`%{D}|, 1
          StringReplace, output, output, {U}{U}{U}{U}{U}{U}{U}{U}, +{U}`%{D}{D}|, 1
          StringReplace, output, output, {U}{U}{U}{U}{U}{U}{U}, +{U}`%{D}{D}{D}|, 1
          StringReplace, output, output, {D}{D}{D}{D}{D}{D}{D}{D}{D}, +{D}`%{U}|, 1
          StringReplace, output, output, {D}{D}{D}{D}{D}{D}{D}{D}, +{D}`%{U}{U}|, 1
          StringReplace, output, output, {D}{D}{D}{D}{D}{D}{D}, +{D}`%{U}{U}{U}|, 1
        }
      }
    }
  }

  ; Remove the bars.
  if (!DisableShiftOptimizations)
    StringReplace, output, output, |, , 1

  return output
}


; -----------------------
; Transform internally used keystroke codes like {R} into corresponding DF keystrokes.
; -----------------------
TransformKeystrokes(input)
{
  global KeyExitMenu

  ; transform keystrokes
  output := TransformDiagonalKeys(input)
  output := TransformDirectionKeys(output)

  ; transform {ExitMenu} to options.txt's KeyExitMenu value
  StringReplace, output, output, {ExitMenu}, %KeyExitMenu%, 1

  ; fix for shift key use
  output := RegExReplace(output, "S)\+(\{.+?\})", "%+$1%")
  output := RegExReplace(output, "S)(?<!\{)([A-Z])([^A-Z])", "$1%$2")

  return output
}


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
TransformDirectionKeys(str)
{
  global KeyLeft, KeyRight, KeyUp, KeyDown, KeyUpZ, KeyDownZ

  ; Replace LDUR<> with user's desired keystrokes from options.txt
  StringReplace, str, str, {L}, %KeyLeft%, 1
  StringReplace, str, str, {R}, %KeyRight%, 1
  StringReplace, str, str, {U}, %KeyUp%, 1
  StringReplace, str, str, {D}, %KeyDown%, 1
  StringReplace, str, str, <, `%%KeyUpZ%`%, 1
  StringReplace, str, str, >, `%%KeyDownZ%`%, 1

  return str
}

;; ---------------------------------------------------------------------------
TransformDiagonalKeys(str)
{
  global KeyUpRight, KeyUpLeft, KeyDownRight, KeyDownLeft
  global UseDiagonalMoveKeys

  if (UseDiagonalMoveKeys)
  {
    dirs1 := "UR"
    dirs1key := KeyUpRight
    dirs2 := "UL"
    dirs2key := KeyUpLeft
    dirs3 := "DR"
    dirs3key := KeyDownRight
    dirs4 := "DL"
    dirs4key := KeyDownLeft

    Loop 4 {
      j := A_Index
      ;RegExReplace(str, "({[UDLR]}){2,}")

      ; for each contiguous group of (\{[UDLR]\}){2,}
      ;   * count number of each UDLR
      ;   * compute relative new cursor position
      ;   * submit equivalent number of cursor movement keys
      ;     using a new function GetDiagonalCursorMoves
      ;     and replace the group with it in the source string
      Loop 20 {
        str := RepeatReplace(str, RepeatStr("{" . SubStr(dirs%j%, 1, 1) . "}", 21 - A_Index) . RepeatStr("{" . SubStr(dirs%j%, 2, 1) . "}", 21 - A_Index), RepeatStr(dirs%j%key, 21 - A_Index))
        str := RepeatReplace(str, RepeatStr("{" . SubStr(dirs%j%, 2, 1) . "}", 21 - A_Index) . RepeatStr("{" . SubStr(dirs%j%, 1, 1) . "}", 21 - A_Index), RepeatStr(dirs%j%key, 21 - A_Index))
      }
    }
  }

  return str
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
; Return needed keystrokes to move the DF cursor the given number of units in the x, y, and z directions
; (negative numbers permitted). Positive direction for x, y, z is east, south, up respectively.
GetCursorMoves(x, y, z)
{
  return ""
    . (x > 0 ? RepeatStr("{R}", x) : RepeatStr("{L}", -x))
    . (y > 0 ? RepeatStr("{D}", y) : RepeatStr("{U}", -y))
    . (z > 0 ? RepeatStr("<", z) : RepeatStr(">", -z))
}

;; ---------------------------------------------------------------------------
; Moves from one (internal) corner of a certain width/height block to a different (internal) corner
; 01  <-- starting corner positions 0, 1, 2, 3
; 23
GetMovesFromCornerToCorner(startCorner, endCorner, width, height)
{
  keys := ""
  ; from L to R and v/v
  if ((startCorner == 0 || startCorner == 2) && (endCorner == 1 || endCorner == 3))
    keys := keys . GetCursorMoves(width - 1, 0, 0)
  else if ((startCorner == 1 || startCorner == 3) && (endCorner == 0 || endCorner == 2))
    keys := keys . GetCursorMoves(-width + 1, 0, 0)

  ; from top to bottom and v/v
  if ((startCorner == 0 || startCorner == 1) && (endCorner == 2 || endCorner == 3))
    keys := keys . GetCursorMoves(0, height - 1, 0)
  else if ((startCorner == 2 || startCorner == 3) && (endCorner == 0 || endCorner == 1))
    keys := keys . GetCursorMoves(0, -height + 1, 0)

  return keys
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
ConvertToNumpadKeys(keys)
{
  ; let user use {/}{*}{-}{+} to refer to the equivalent numpad keys used by DF
  StringReplace, keys, keys, {/}, {NumpadDiv}, 1
  StringReplace, keys, keys, {*}, {NumpadMult}, 1
  StringReplace, keys, keys, {-}, {NumpadSub}, 1
  StringReplace, keys, keys, {+}, {NumpadAdd}, 1

  ; also convert regular occurrences of + to {+} so that QF sends an actual plus keystroke
  StringReplace, keys, keys, +, `%{+}`%, 1

  return keys
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
  MouseTipOn := 1
  SetTimer, ShowMouseTip, On
  ;SetTimer, HideMouseTip, Off ; make sure a timed mouse tip hiding event (e.g. the splash tip) doesn't close a different tip
  Sleep 50 ; let the timer tick a bit, so the tip gets updated right after being turned on (Send can block the timer otherwise)
  ForceMouseTipUpdate()
}

;; ---------------------------------------------------------------------------
TurnMouseTipOff()
{
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
  CoordMode, Mouse, Screen
  MouseGetPos, xpos, ypos

  if (!ShowMouseTooltip) {
    Tooltip,
    return
  }

  if (!WinActive("Dwarf Fortress"))
  {
    Tooltip,
  }
  else
  {
    ShowingSwitchNotice := 0
    SwitchNoticeShown := 1
    if (Building)
      SetTimer, ShowMouseTip, %MouseTooltipPlaybackUpdateEveryMs%
    else
      SetTimer, ShowMouseTip, %MouseTooltipInGameUpdateEveryMs%

    xpos += 25
    if (ypos + 160 > ScreenHeight)
      ypos -= 160 ; put tooltip above mouse pointer if we're near the bottom
    else
      ypos += 10 ; below

    if (LastTooltip != Tooltip || LastMouseX != xpos || LastMouseY != ypos)
    {
      LastTooltip := Tooltip
      LastMouseX := xpos
      LastMouseY := ypos

      if (Tooltip == "")
      {
        if (!HideTooltip) {
          ; get the filename on its own
          SplitPath, LastSelectedFile, LastSelectedFilename

          tip := ""
          . (LastSelectedFile ? LastSelectedFilename . " complete.`n`nTo begin, hit Alt+D and select a CSV file.`nAlt+E will run " . LastSelectedFilename . " again." : "Quickfort " . Version . "`nhttp://sun2design.com/quickfort`n`nTo begin, hit Alt+D and select a CSV file.")
          . "`n`nAlt+H hides/shows this tooltip.`nAlt+T opens QF command line.`nShift+Alt+Z suspends/resumes QF.`nShift+Alt+X exits QF."

          ToolTip, %tip%, xpos, ypos
        }
        else
          Tooltip,
      }
      else
      {
        tip := "[" SelectedFilename "]" . (RepeatPattern ? "`n** REPEATING: " RepeatPattern " **" : "") . "`n"
        if (StartPosAbsX > 0)
        {
          tip := tip . "START POSITION:" . (StartPosComment ? " " . StartPosComment : "") . " (" . StartPosAbsX . ", " . StartPosAbsY . ")"
        }
        else
        {
          tip := tip . "Start corner: " . StartPositionLabel . (StartPosComment ? "`nUse Alt+E to reset start position." : "")
        }



        tip := tip . "`n`n" . Tooltip

        xpos += 25
        if (ypos + 170 > ScreenHeight)
          ypos -= 170 ; put tooltip above mouse pointer if we're near the bottom
        else
          ypos += 10 ; below

        ToolTip, %tip%, xpos, ypos
      }
    }
  }

  return

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

;; ---------------------------------------------------------------------------
RepeatKeyPattern(keys, pattern, height, width, depth)
{
  ; If there is no repetition to do, just return the original value of keys
  if (pattern == "")
    return keys

  ; Split pattern into the part we want to do the repeat loop for here,
  ; and the following part (if any) which we want to do for each iteration
  ; of said loop.
  RegExMatch(pattern . " ", "^(.*?)(\d+)\s*([udnsew])\w*\s*$", parts)
  repCount := parts2
  repDir := parts3
  rest := parts1

  if (!rest) ; last or only step of the pattern
    block := keys
  else ; recursively call myself to complete the remaining directions
    block := RepeatKeyPattern(keys, rest, height, width, depth)

  return RepeatStr(block . GetRepeatBlockConnector(repDir, height, width, depth, 1), repCount)
      . GetRepeatBlockConnector(repDir, height, width, depth, -repCount) ; connect blocks together
}

;; ---------------------------------------------------------------------------
GetRepeatBlockConnector(direction, height, width, depth, steps)
{
  ;MsgBox, % direction "," height "h " width "w " depth "d x" steps
  if (direction = "n")
    return GetCursorMoves(0, -height * steps, 0)
  if (direction = "s")
    return GetCursorMoves(0, height * steps, 0)
  if (direction = "e")
    return GetCursorMoves(width * steps, 0, 0)
  if (direction = "w")
    return GetCursorMoves(-width * steps, 0, 0)
  if (direction = "u")
    return "%wait%" GetCursorMoves(0, 0, depth * steps) "%wait%"
  if (direction = "d")
    return "%wait%" GetCursorMoves(0, 0, -depth * steps) "%wait%"
}

CountCommands(file)
{
  commandList := ""
  Loop, Read, %file%
  {
    Loop, Parse, A_LoopReadLine, `,
    {
      cmdName := A_LoopField
      usableCommand := (StrLen(cmdName) > 0 && RegExMatch(cmdName, "[^a-zA-Z0-9_@\$\?\[\]\(\)]") == 0)
      if (usableCommand)
      {
        if (RegExMatch(cmdName, "(.+)\((\d+)x(\d+)\)", matches) > 0)
        {
          cmdName := matches1
          cmdCount := matches2 * matches3
        }
        else
        {
          cmdCount := 1
        }

        if (!command%cmdName%)
        {
          commandList := commandList "," cmdName
        }
        command%cmdName% += cmdCount
      }
    }
  }

  uses := ""

  Loop, Parse, commandList, `,
  {
    if (StrLen(A_LoopField) > 0)
    {
      uses := uses command%A_LoopField% ":" A_LoopField "`n"
    }
  }

  Sort, uses, N R

  Loop, Parse, uses, `n
  {
    output := output RegExReplace(A_LoopField, "(\d+):(.+)", "$2: $1 uses") "`n"
  }

  output := RegExReplace(output, "^((.+`n){20}).+", "$1(... more)")
  return output
}
