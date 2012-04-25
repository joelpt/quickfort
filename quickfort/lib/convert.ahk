;; High level functions used by the hotkeys to read and play blueprints.


;; ---------------------------------------------------------------------------
;; convert blueprint to specification, move output macro file to DF macros dir
;; and execute the macro in the DF window
ConvertAndPlayMacro()
{
  global
  local title, starttime, elapsed, destfile

  ; construct a somewhat useful title for the macro
  if (CommandLineMode)
  {
    title := EvalMode "-cmd"
  }
  else
  {
    title := ""
    buildType := BuildType%SelectedSheetIndex%
    sheetName := Name%SelectedSheetIndex%
    if (sheetName && sheetName != SelectedFilename)
    {
      if (buildType != SubStr(sheetName, 1, StrLen(buildType)))
      {
        title := title . buildType . "-"
      }

      title := title . RegExReplace(RegExReplace(Name%SelectedSheetIndex% , "[^\w\(\)]", "-"), "-{2,}", "-")
    }
    else
    {
      title := title . buildType
    }
    title := title . "-" . SelectedFilename
  }

  title := GetRandomFileName() "-" SubStr(title, 1, 30)

  ; Clock how long it takes
  starttime := A_TickCount

  ; convert and save
  destfile := ConvertAndSaveMacro(title)

  ; measure elapsed time for run
  elapsed := A_TickCount - starttime

  ; Play the macro.

  ; TODO: strip this block of textplanation out if PlayMacro(0) proves to be safe
  ; The macro playback delay is made proportional to the time it takes to execute
  ; qfconvert.exe because it is a good signal of the current response speed of
  ; the OS; a too-short delay here will cause DF to miss our macro-loading-and-playing
  ; keystrokes. The first time we go through this process usually is (and needs to be)
  ; much slower than subsequent runs.
  ; PlayMacro(elapsed)

  ; We'll just do a micro-delay here as it appears that we can do ^L{Enter}^P very
  ; quickly without issue, as long as we don't delete the .mak file too quickly
  PlayMacro(0)

  ; remember for repeated use of Alt+D
  LastMacroWasPlayed := true

  if (elapsed > 5000)
    elapsed := 5000 ; 5sec max sleep
  Sleep, %elapsed% ; sleeping for the same time it took qfconvert to run

  ; discard the file (DF will retain a memory of it anyway as it currently works)
  FileDelete, %destfile%

  return true
}


;; ---------------------------------------------------------------------------
;; convert blueprint to specification, then place the output macro file
;; in the DF macros dir with the specified title. Returns the path
;; to the file in its final location.
ConvertAndSaveMacro(title)
{
  global
  local outfile, dfpath, destfile, result

  outfile := A_Temp "\" title ".mak"
  ActivateGameWin() ; TODO try to get dfpath without focusing the game window
  dfpath := GetWinPath("A") ; active window is the instance of DF we want to send to
  SplitPath, dfpath, , dfpath
  destfile := dfpath "\data\init\macros\" title ".mak"


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
    return -1
  }

  ; Move to DF dir
  FileMove, %outfile%, %destfile%, 1
  if (ErrorLevel > 0)
  {
    MsgBox, Error: Could not move macro file`nFrom: %outfile%`nTo: %destfile%
    return -1
  }

  ; Read file in new location - this is to try and delay the starting of
  ; DF macro playback an appropriate length of time to avoid DF-side
  ; macro-I/O errors; if we can read the whole file DF should be ready to
  Loop, Read, %destfile%
  {
    Sleep, 0
  }

  return destfile
}


;; ---------------------------------------------------------------------------
;; convert blueprint to specification and output keystrokes to game window
;; if visualizing is true we just outline the blueprint perimeter
ConvertAndSendKeys(visualizing)
{
  global
  local outfile, output

  outfile := A_Temp "\keys.tmp"
  FileDelete, %outfile%
  ActivateGameWin()

  if (CommandLineMode)
  {
    result := ConvertBlueprint(CommandLineFile, outfile, 1, "keylist", "", StartPos, RepeatPattern, visualizing)
  }
  else
  {
    result := ConvertBlueprint(SelectedFile, outfile, SelectedSheetIndex, "keylist", "", StartPos, RepeatPattern, visualizing)
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
