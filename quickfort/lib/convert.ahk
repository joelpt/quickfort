;; High level functions used by the hotkeys to read and play blueprints.


;; ---------------------------------------------------------------------------
;; convert blueprint to specification, move output macro file to DF macros dir
;; and execute the macro in the DF window
ConvertAndPlayMacro()
{
  global
  local title, outfile, dfpath, destfile, starttime, result

  title := GetRandomFileName()
  outfile := A_ScriptDir "\" title ".mak"
  ActivateGameWin()
  dfpath := GetWinPath("A") ; active window is the instance of DF we want to send to
  SplitPath, dfpath, , dfpath
  destfile := dfpath "\data\init\macros\" title ".mak"

  ; Clock how long it takes
  starttime := A_TickCount

  if (CommandLineMode)
  {
    result := ConvertBlueprint(CommandLineFile, outfile, 1, "macro", title, StartPos, RepeatPattern, false)
  }
  else
  {
    result := ConvertBlueprint(SelectedFile, outfile, SelectedSheetIndex, "macro", title, StartPos, RepeatPattern, false)
  }

  if (!result)
  {
    MsgBox, Error: ConvertBlueprint() returned false
    return false
  }
  
  ; Move to DF dir
  FileMove, %outfile%, %destfile%, 1
  if (ErrorLevel > 0)
  {
    MsgBox, Error: Could not move macro file`nFrom: %outfile%`nTo: %destfile%
    return false
  }

  ; measure elapsed time for run
  elapsed := A_TickCount - starttime
  
  ; Play the macro.
  ; The macro playback delay is made proportional to the time it takes to execute
  ; qfconvert.exe because it is a good signal of the current response speed of
  ; the OS; a too-short delay here will cause DF to miss our macro-loading-and-playing
  ; keystrokes. The first time we go through this process usually is (and needs to be)
  ; much slower than subsequent runs.
  PlayMacro(elapsed / 2) 

  ; remember for repeated use of Alt+D
  LastMacroWasPlayed := true

  FileDelete, %destfile%
  FileDelete, %outfile%
  return true
}


;; ---------------------------------------------------------------------------
;; convert blueprint to specification and output keystrokes to game window
;; if visualizing is true we just outline the blueprint perimeter
ConvertAndSendKeys(visualizing)
{
  global
  local outfile, output

  outfile := A_ScriptDir "\keys.tmp"
  FileDelete, %outfile%
  ActivateGameWin()

  if (CommandLineMode)
  {
    result := ConvertBlueprint(CommandLineFile, outfile, 1, "key", "", StartPos, RepeatPattern, visualizing)
  }
  else
  {
    result := ConvertBlueprint(SelectedFile, outfile, SelectedSheetIndex, "key", "", StartPos, RepeatPattern, visualizing)
  }

  if (!result)
  {
    MsgBox, Error: ConvertBlueprint() returned false
    return false
  }

  ; Read file contents
  FileRead, output, %outfile%
  if (!output)
  {
    MsgBox, Error: Could not read keys output file`nFrom: %outfile%`
    return false
  }

  ;MsgBox % output
  SendKeys(output)

  ; clean up
  FileDelete, %outfile%

  ; remember for repeated use of Alt+D
  LastSendKeys := output

  return true
}

;; ---------------------------------------------------------------------------
;; convert command line given by mode, commands into a qfconvert-compatible
;; CSV file and write it to filepath
WriteCommandLineToCSVFile(mode, commands, filepath)
{
  StringReplace, commands, commands, #, `n, All   ;  # -> newline

  output := "#" . mode . "`n" . commands

  FileDelete, %filepath%
  FileAppend, %output%, %filepath%
}
