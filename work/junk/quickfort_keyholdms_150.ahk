#SingleInstance force

Version := "1.01"

SetTitleMatchMode, 3
Menu, Tray, MainWindow

; -----------------------------
; Load options from options.txt
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
RepeatCount := 0
RepeatDir := ""
ShowCSVIntro := 0
EvalMode := ""
EvalCommands := ""
MouseTipOn := 0
LastTooltip := ""
LastMouseX := 0
LastMouseY := 0
SuspendMouseTipOn := 0

if (ShowSplashBox)
{ 
  Tooltip := "splash" ; we don't sent the actual splash text here because tooltip is assembled in ShowMouseTip
  SetTimer, ShowMouseTip, 10
  MouseTipOn := 1
  ;SetTimer, HideMouseTip, -6000
}
else {
  SetTimer, ShowMouseTip, 10
  TurnMouseTipOff()
}

; Reload the script (Shift-Alt-R)
$+!R::
  Reload
  return

; Toggle suspend of the script (Shift-Alt-Z)
$+!Z::
  Suspend, Permit
  if (A_IsSuspended) {
    Suspend, Off
    ; show mouse tip if it was visible before
    if (SuspendMouseTipOn) {
      ForceMouseTipUpdate()
      TurnMouseTipOn()
    }
  }
  else {
    ; store mouse tip state
    SuspendMouseTipOn := (MouseTipOn && StrLen(Tooltip) > 0)
    TurnMouseTipOff()
    Suspend, On
  }
  return

; Exit the script (Shift-Alt-X)
$+!X:: 
  TurnMouseTipOff()
  ExitApp
  return



#IfWinActive Dwarf Fortress

; Cancel build (Alt+C)
$!C::
  Critical
  TurnMouseTipOff()
  if (ReadyToGo)
  {
    ReadyToGo := 0
    Building := 0
    RepeatCount := 0
    RepeatDir := ""
    MsgBox, Build cancelled.`n`nPress Alt+E to redo the same CSV file again, or Alt+D to choose another.`n`nPress Alt+T to enter a command directly.`nShift+Alt+Z suspends/resumes Quickfort hotkeys.
  }
  return

; Start position switch
$!Q:: 
  StartPos := 0
  StartPositionLabel = Top left
  ForceMouseTipUpdate()
  return

$!W:: 
  StartPos := 1
  StartPositionLabel = TOP RIGHT
  ForceMouseTipUpdate()
  return

$!A:: 
  StartPos := 2
  StartPositionLabel = BOTTOM LEFT
  ForceMouseTipUpdate()
  return

$!S:: 
  StartPos := 3
  StartPositionLabel = BOTTOM RIGHT
  ForceMouseTipUpdate()
  return

; Helper to mass-demolish misplaced constuctions
$!X::
  Send {x 30}
  return

; redo last construction effort (Alt+E)
; Only does anything after a build finishes (successfully or cancelled)
$!E:: 
  if (!ReadyToGo)
  {
    if (LastSelectedFile = "")
    {
      MsgBox, No file selected yet. Use Alt+D to select a file, or Alt+T to enter a command directly.`n`nShift+Alt+Z suspends/resumes Quickfort hotkeys.
      return
    }
    
    SelectedFile := LastSelectedFile
    ShowCSVIntro := 0
    ForceMouseTipUpdate()
    BuildRoutine()
  }
  else
  {
    Tooltip := "CANNOT USE Alt+E NOW.`nUse Alt+D to build or Alt+C to cancel."
  }
  return

; Autorepeat build (Alt+R)
$!R::
  if (!Building && ReadyToGo)
  {
    InputBox, count, Auto-repeat blueprint, How many times do you want to repeat this blueprint?
    if (count > 0) {
      InputBox, dir, Auto-repeat blueprint, Repeat %count% times in which direction?`n`nEnter exactly one of: down up north south east west
      ; we actually work with 1 letter abbreviations
      if (RegExMatch(dir, "S)^([dunsew])", RepeatDirMatch)) {
        RepeatDir := RepeatDirMatch1
        StringUpper, RepeatDir, RepeatDir
        RepeatCount := count
        ForceMouseTipUpdate()
      }
    }
  }
  return

; One-off command line (Alt+T)
$!T::
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
    
    if (command != "")
    {
      evalOK := RegExMatch(command, "S)^([bdpq])\w*\s+(.+)", evalMatch)
      if (!evalOK)
      {
        MsgBox, Error: Command '%command%' syntax error: not of form [b|d|p|q] cmd(,cmd2,..,cmdN)
        Exit
      }
      else
      {
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
   
; Build starter (Alt+D)
$!D:: 
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

; and its routine
BuildRoutine()
{    
  global SelectedFile, LastSelectedFile, Comment, Mode, StartPos, ReadyToGo, Tooltip, KeyDelay, DelayMultiplier
  global ShowCompletedBox, UseLongConstructions, DebugOn, AliasesPath, DisableKeyOptimizations, SelectedFilename
  global RepeatCount, RepeatDir, ShowCSVIntro, ShowCommentBox, EvalMode, EvalCommands
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
        ;SelectedFile = aaatest.csv
        
        if (!SelectedFile)
        {
          MsgBox, No file selected. Use Alt+D again to select a Quickfort .csv file, or Alt+T to enter a command directly.`n`nShift+Alt+Z suspends/resumes QF.
          Exit
        }
      }
  
      ; make sure we have a #mode line
      FileReadLine, firstline, %SelectedFile%, 1
      StringReplace, firstline, firstline, ", , 1
      if (!RegExMatch, firstline, )
      {
        MsgBox, Error: First line of .csv file must be one of: #dig #build #place #query (optionally followed by a space and a comment)`n`nUse Shift+Alt+Z to suspend/resume QF.
        Exit
      }
  
      ; Extract mode and comment, if any
      RegExMatch(firstline, "S)^#(\w+)( .+)?", modeLineMatch)
      FullMode := modeLineMatch1
      Mode := Substr(modeLineMatch1, 1, 1)

      Comment := modeLineMatch2
      Comment := TrimSpaces(Comment) ; trim spaces off
      Comment := RegExReplace(Comment, "S),{2,}") ; throw out unwanted strings of commas
      Comment := RegExReplace(Comment, "S),+$") ; discard any trailing commas
      Comment := RegExReplace(Comment, "S)\\n", "`n") ; Turn \\n into `n (AHK-style newline)

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
      startKeys := "{Space}"
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
      Exit
    }
    
    ReadyToGo := 1
    
    ; -----------------------------
    ; Show CSV comment box
    ; -----------------------------
    if (ShowCommentBox && ShowCSVIntro)
    {
      MsgBox, , Quickfort - %SelectedFilename% [%FullMode%], %SelectedFilename% (%FullMode% mode)`n`n%Comment%
    }
    
  
    ; -----------------------------
    ; Show howto mouse-tip
    ; -----------------------------
    Tooltip = TYPE %userInitKey% (%userInitText%). Position cursor with KEYBOARD.`nHit Alt+D to run script.`n`nAlt+Q/W/A/S changes starting corner.`nAlt+C cancels. Alt+R for repeat mode.
    TurnMouseTipOn()
    ForceMouseTipUpdate()
    Exit
  }
  ; else:
  
  ; -----------------------
  ; Start the build process  
  ; -----------------------
  Building := 1
  Tooltip = Quickfort running (hold Alt+C to cancel)
  

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
  
  ; Initial moves are just to get to the top left corner if not there already.
  moves := GetMovesFromCornerToCorner(StartPos, 0, width, height)
  
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
          needle := "S)(" . longItem . ",){" . reps . "}"
          replaceWith := longItem . "(" . reps . "x1)" . RepeatStr(",", reps)
          row := RegExReplace(row, needle, replaceWith)
        }
      }
    }

    colNum := 0
  
    ; -------------------------------------------
    ; Cell loop  
    ; -------------------------------------------
    Loop, parse, row, `,
    {
      each := ""
      afterEach := ""
      outputCell := ""
      action := A_LoopField
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
          ; Matches commands of the form a(4x6), which would place a 4 wide x 6 tall animal stockpile in place mode, using the cursor keys to size it.
          ; Object will be placed with its top-left corner tile at the present cursor position.
          ; Full format is C(WxH)C where C are keystrokes, W is object width and H is object height
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
          each := "@&{Enter}+{Enter}%wait%"
          
          ; Placing wf, wv, Ms require extra regular Enters (others?).
          if (action == "wf" || action == "wv") {
            each := "@&{Enter}%wait%{Enter}%wait%+{Enter}%wait%"
          }
          else if (SubStr(action, 1, 2) == "Ms") {
            each := "@&{Enter}{Enter}{Enter}{Enter}%wait%"
          }
                    
          if (RegExMatch(action, "S)^([CMTwe])(.+)$", submenuMatch)) {
            ; Build submenus handling
            
            if (submenuMatch1 == lastSubmenu) {
              ; still in the same submenu as last time. don't need to send submenu opening key again.
              action := subMenuMatch2
            }
            else if (lastSubmenu != "") {
              ; changing from one menu to another. Need to exit current menu with space before entering new submenu.
              action := "{Space}" . action
            }
    
            lastSubmenu := submenuMatch1
            inSubMenu := 1
          }
          else {
            ; this wasn't a submenu command. If lastSubmenu has a value now, we need to send Space to get out of that submenu before the next command.
            if (lastSubmenu != "")
            {
              action := "{Space}" . action
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
                  . (rangeMatch3 > 1 ? "{u " . (rangeMatch3 - 1) . "}" : "")
                  . (rangeMatch2 > 1 ? "{k " . (rangeMatch2 - 1) . "}" : "")
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
    
    ; if this was an eval'd command, we're all done now.
    ;if (evalCommands) {
    ;  EvalCommands := EvalMode := Mode := SelectedFile := SelectedFilename := ""
    ;  break
    ;}
    
  }

  ; put us back in the position we started from
  moves := moves . "{U}{U}" . GetMovesFromCornerToCorner(2, StartPos, width, height)
  
  ; add any remaining (unsent) moves
  if (Mode = "b")
  {
    output := output
      . (inSubMenu ? "{Space}" : "")
      . "O"   ; use dirt road (b O) to reposition cursor reliably
      . moves
  }
  else
  {
    output := output . moves
  }

  
  ; ------------------
  ; handle repeat mode
  ; ------------------
  ; if we're doing repeats (Alt+R) we handle it here. output is repeated and chained together with necessary movement commands
  ; to get to the correct next tile for each successive output.
  if (RepeatCount > 1) {
    moves := ""
    
    ; targetZLevel is the level, relative to the level we started the initial block on, that we want to be on in order to begin the
    ; next block. zLevel currently contains the level we actually are on now, again relative to the initial block (0 = same level,
    ; 1 = one level above)
    if (RepeatDir = "d" || RepeatDir = "u") {
      ; next placement needs to occur on the z-level above or below the initial one. adjust targetZLevel accordingly.
      ; To accommodate for multilevel blueprints, we multiply this z-level shift by the number of floors in the blueprint.
      targetZLevel := (RepeatDir = "u" ? 1 : -1) * (1 + Abs(zLevel))
    }
    else {
      ; repeating in a cardinal direction - we need to start back on the same level we built the last block on every time
      targetZLevel := 0
    }

    ; Now make targetZLevel relative to our CURRENT level, by subtracting our current level from it.
    targetZLevel -= zLevel
      
    ; Finally we can issue any moves needed to get onto the correct relative z-level
    if (targetZLevel < 0) {
      moves := moves . RepeatStr(">", -targetZLevel)
    }
    else if (targetZLevel > 0) {
      moves := moves . RepeatStr("<", targetZLevel)
    }
    
    ; Then move one of the four cardinal directions (exactly one 'block' away, touching the current block) or down/up (directly above or below)
    ;if (RepeatDir = "u")
    ;  moves := moves . "<"
    ;else if (RepeatDir = "d")
    ;  moves := moves . ">"
    ;else 
    if (RepeatDir = "n")
      moves := moves . RepeatStr("{U}", height)
    else if (RepeatDir = "s")
      moves := moves . RepeatStr("{D}", height)
    else if (RepeatDir = "e")
      moves := moves . RepeatStr("{R}", width)
    else if (RepeatDir = "w")
      moves := moves . RepeatStr("{L}", width)
    
    output := RepeatStr(output . moves, RepeatCount - 1) . output
    
    
    RepeatCount := 0
    RepeatDir := ""
  }
    
    
  
  
  Log("`n`nBefore keystroke optimizations: " . output)
  
  ; -----------------------
  ; Keystroke optimizations
  ; -----------------------
  if (DisableKeyOptimizations)
  {
    ; Replace {R} with {Right}, etc.
    StringReplace, output, output, {R}, {Right}, 1
    StringReplace, output, output, {L}, {Left}, 1
    StringReplace, output, output, {U}, {Up}, 1
    StringReplace, output, output, {D}, {Down}, 1
  }
  else
  {
    ; Optimizations to eliminate several classes of movement redundancy.
    
    ; Turn {L}{D}{R}, {L}{D}{D}{R}, ... into just {D}. Lets us avoid going to the beginning of the next row, etc.
    Loop 10
    {
      repeated := RepeatStr("{D}", A_Index)
      Loop 2 
      {
        check := (A_Index == 1 ? "{L}" : "{R}") . repeated . (A_Index == 1 ? "{R}" : "{L}")
    
        Loop
        {
          StringReplace, output, output, %check%, %repeated%, UseErrorLevel
          if ErrorLevel = 0
            break
        }
      }
    }
    
    ; Remove instances of {R}{L}, etc. pairs repeatedly until all gone from output (they'd cancel one another out).
    ; {R}{L}
    Loop {
      StringReplace, output, output, {R}{L}, , UseErrorLevel
      if (ErrorLevel = 0)
        break
    }
    ; {L}{R}
    Loop {
      StringReplace, output, output, {L}{R}, , UseErrorLevel
      if (ErrorLevel = 0)
        break
    }
    ; {U}{D}
    Loop {
      StringReplace, output, output, {U}{D}, , UseErrorLevel
      if (ErrorLevel = 0)
        break
    }               
    ; {D}{U}
    Loop {
      StringReplace, output, output, {D}{U}, , UseErrorLevel
      if (ErrorLevel = 0)
        break
    }               
    
    ; Replace {R} with {Right}, etc.
    StringReplace, output, output, {R}, {Right}, 1
    StringReplace, output, output, {L}, {Left}, 1
    StringReplace, output, output, {U}, {Up}, 1
    StringReplace, output, output, {D}, {Down}, 1
    
    ; Turn {Right}x10 into +{Right}|, etc. We insert a pipe symbol as a suffix to the replacement and will remove it later;
    ; it acts as a "bar" and makes sure we don't replace something that we already replaced in an earlier step.
    StringReplace, output, output, {Right}{Right}{Right}{Right}{Right}{Right}{Right}{Right}{Right}{Right}, +{Right}|, 1
    StringReplace, output, output, {Left}{Left}{Left}{Left}{Left}{Left}{Left}{Left}{Left}{Left}, +{Left}|, 1
    StringReplace, output, output, {Up}{Up}{Up}{Up}{Up}{Up}{Up}{Up}{Up}{Up}, +{Up}|, 1
    StringReplace, output, output, {Down}{Down}{Down}{Down}{Down}{Down}{Down}{Down}{Down}{Down}, +{Down}|, 1
    
    if (!DisableBacktrackingOptimization)
    {
      ; Turn {Right}x9 into +{Right}{Left}, etc. This should be doable with a couple of loops, but this works for now.
      ; Could run into problems using these optimizations if you're building right next to the edge of the map,
      ; though it *should* still work fine since you can't build on the 3 tile "margin" around the edge anyway....
      StringReplace, output, output, {Right}{Right}{Right}{Right}{Right}{Right}{Right}{Right}{Right}, +{Right}{Left}|, 1
      StringReplace, output, output, {Right}{Right}{Right}{Right}{Right}{Right}{Right}{Right}, +{Right}{Left}{Left}|, 1
      StringReplace, output, output, {Right}{Right}{Right}{Right}{Right}{Right}{Right}, +{Right}{Left}{Left}{Left}|, 1
      StringReplace, output, output, {Left}{Left}{Left}{Left}{Left}{Left}{Left}{Left}{Left}, +{Left}{Right}|, 1
      StringReplace, output, output, {Left}{Left}{Left}{Left}{Left}{Left}{Left}{Left}, +{Left}{Right}{Right}|, 1
      StringReplace, output, output, {Left}{Left}{Left}{Left}{Left}{Left}{Left}, +{Left}{Right}{Right}{Right}|, 1
      StringReplace, output, output, {Up}{Up}{Up}{Up}{Up}{Up}{Up}{Up}{Up}, +{Up}{Down}|, 1
      StringReplace, output, output, {Up}{Up}{Up}{Up}{Up}{Up}{Up}{Up}, +{Up}{Down}{Down}|, 1
      StringReplace, output, output, {Up}{Up}{Up}{Up}{Up}{Up}{Up}, +{Up}{Down}{Down}{Down}|, 1
      StringReplace, output, output, {Down}{Down}{Down}{Down}{Down}{Down}{Down}{Down}{Down}, +{Down}{Up}|, 1
      StringReplace, output, output, {Down}{Down}{Down}{Down}{Down}{Down}{Down}{Down}, +{Down}{Up}{Up}|, 1
      StringReplace, output, output, {Down}{Down}{Down}{Down}{Down}{Down}{Down}, +{Down}{Up}{Up}{Up}|, 1
    }
    
    ; Remove the bars.  
    StringReplace, output, output, |, , 1

		; Convert LDUR<> into user preference for these keystrokes.
		StringReplace, output, output, {Left}, KeyLeft
		StringReplace, output, output, {Right}, KeyRight
		StringReplace, output, output, {Up}, KeyUp
		StringReplace, output, output, {Down}, KeyDown
		StringReplace, output, output, <, KeyUpZ
		StringReplace, output, output, >, KeyDownZ

  }
  
  
  Log("`n`nFinal output: " . output)
  
  
  ; Migrate SelectedFile to LastSelected file now, so if the user cancels we'll still have it for use with Alt+E (redo).
  LastSelectedFile := SelectedFile
  SelectedFile := ""
  
  ; Show busy mousetip
  Tooltip = Quickfort running... (hold Alt+C to cancel)
  TurnMouseTipOn()
      
  ; Wait a moment before we start so keys are released by user.
  Sleep, 250
  Sleep, 0
    
  ; Send it chunk style, breaking up Sends between % chars to give user a chance to cancel with Alt+C
  ; If a chunk is just "wait" (i.e. %wait%) we'll sleep for a bit (for those CPU intensive actions in DF).
  ; ------------------------------------------------------------------------------------------------------
  if (!DebugOn)
  {
    ; Count total number of % chars
    StringSplit, pctarray, output, `%
    numPctChars := pctarray0
    
    
    Loop, parse, output, `%
    { 
      pctDone := Floor((A_Index/numPctChars) * 100)
      Tooltip = Quickfort running (%pctDone%`%)... (hold Alt+C to cancel)
      
      SetKeyDelay, KeyDelay, 50    

      ForceMouseTipUpdate()
      Sleep, 0
      Sleep, KeyDelay
      if (!ReadyToGo)
      {
        ; build was cancelled by user.
        break
      }
      
      if (A_LoopField = "wait")
      {
        Sleep, (DelayMultiplier * 5)
      }
      else                    
      { 
        IfWinNotActive Dwarf Fortress
        {      
          ; prevent mass sending keys to wrong window (no reliable way to make DF receive all keys in background - ControlSend is flaky w/ DF)
          Building := 0
          TurnMouseTipOff()
          msg := "Macro aborted!`n`nYou switched windows. The Dwarf Fortress window must be focused while Quickfort is running.`n`n"
            . (Mode = "b" ? "Use Alt+X to send the x key 30 times to DF (useful for destructing aborted builds).`n`n" : "")
            . (EvalMode ? "Hit Alt+D to choose a .csv file." : "Hit Alt+D to choose another .csv file. `nHit Alt+E to redo the same .csv file again.")
            . "`nHit Alt+T to enter a command directly.`n`nShift+Alt+Z suspends/resumes Quickfort hotkeys.`nShift+Alt+X exits QF."
          MsgBox, %msg%
          break
        }
        
        ; actually send the keys!
        Send %A_LoopField%
      }
    }
  }
  
  
  TurnMouseTipOff()
  
  ; Show "completed" popup box if option is set and user didn't cancel first
  Sleep, 0
  if (ShowCompletedBox && ReadyToGo && Building)
  {
    msg := "Macro completed.`n`n"
      . (EvalMode ? "Hit Alt+D to choose a .csv file." : "Hit Alt+D to choose another .csv file. `nHit Alt+E to redo the same .csv file again.")
      . "`nHit Alt+T to enter a command directly.`n`nShift+Alt+Z suspends/resumes Quickfort hotkeys.`nShift+Alt+X exits QF."
    MsgBox, %msg%
  }
  
  ; Show file selection box next time Alt+D is hit
  ReadyToGo := 0
  Building := 0
  
  ; Clear Eval stuff, tooltip
  EvalCommand := EvalMode := Tooltip := ""
  
  return
}






;----------------------------------------------------
; Helper Functions
;----------------------------------------------------

; Return needed keystrokes to move the DF cursor the given number of units in the x, y, and z directions
; (negative numbers permitted). Positive direction for x, y, z is east, south, up respectively.
GetCursorMoves(x, y, z)
{
  return ""
    . (x > 0 ? RepeatStr("{R}", x) : RepeatStr("{L}", -x))
    . (y > 0 ? RepeatStr("{D}", y) : RepeatStr("{U}", -y))
    . (z > 0 ? RepeatStr("{<}", z) : RepeatStr("{>}", -z))
}
                      
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


RepeatStr(str, count)
{
  output := ""
  Loop %count%
  {
    output = %output%%str%
  }
  return output
}  

ConvertToNumpadKeys(keys)
{
  ; let user use {/}{*}{-}{+} to refer to the equivalent numpad keys used by DF
  StringReplace, keys, keys, {/}, {NumpadDiv}, 1
  StringReplace, keys, keys, {*}, {NumpadMult}, 1
  StringReplace, keys, keys, {-}, {NumpadSub}, 1
  StringReplace, keys, keys, {+}, {NumpadAdd}, 1
  
  ; also convert regular occurrences of + to {+} so that QF sends an actual plus keystroke
  StringReplace, keys, keys, +, {+}, 1
  
  return keys
}

TrimSpaces(str)
{
  str := RegExReplace(str ,"S)^ +")
  str := RegExReplace(str ,"S) +$")
  
  return str
}

Log(debugstr)
{
    global DebugOn
    FileAppend, %debugstr%, debug.txt 
}

TurnMouseTipOn()
{
  MouseTipOn := 1
  SetTimer, ShowMouseTip, On
  ;SetTimer, HideMouseTip, Off ; make sure a timed mouse tip hiding event (e.g. the splash tip) doesn't close a different tip
  Sleep 50 ; let the timer tick a bit, so the tip gets updated right after being turned on (Send can block the timer otherwise)
}
  
TurnMouseTipOff()
{
  SetTimer, ShowMouseTip, Off
  MouseTipOn := 0
  ToolTip,
}

ForceMouseTipUpdate()
{         
  global LastMouseX, LastMouseY
  
  ; this forces the mouse tip to get updated next timer tick
  LastMouseX := LastMouseY := 0
}

ShowMouseTip:
  MouseGetPos, xpos, ypos

  if (!WinActive("Dwarf Fortress"))
  {
    SetTimer, ShowMouseTip, 75
    tip := "Switch to the Dwarf Fortress window.`nShift+Alt+Z suspends/resumes Quickfort."
    ToolTip, %tip%, xpos + 25, ypos + 10
    LastTooltip := ""
  }
  else if (LastTooltip != Tooltip || LastMouseX != xpos || LastMouseY != ypos && Tooltip != "")
  {
    SetTimer, ShowMouseTip, 10
    
    LastTooltip := Tooltip
    LastMouseX := xpos
    LastMouseY := ypos
    
    if (Tooltip == "splash")
    {
      tip = Quickfort %Version%`nhttp://sun2design.com/qf`n`nTo begin, hit Alt+D and select a CSV file.`n`nAlt+T opens QF command line.`nShift+Alt+Z suspends/resumes QF.`nShift+Alt+X exits QF.
    }
    else
    {
      tip := "[" . SelectedFilename . "]" . (RepeatCount > 0 ? " REPEAT " . RepeatCount . "-" . RepeatDir : "")
        . "`nStart corner: " . StartPositionLabel . "`n`n"
        . Tooltip
    }
    
    ToolTip, %tip%, xpos + 25, ypos + 10
  }

  return
  
HideMouseTip:
  TurnMouseTipOff()
  Tooltip := ""
  return
