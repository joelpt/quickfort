;; High level functions used by the hotkeys to read and play blueprints.


;; ---------------------------------------------------------------------------
;; convert blueprint to specification, move output macro file to DF macros dir
;; and execute the macro in the DF window
ConvertAndPlayMacro()
{
  global
  local title, outfile, dfpath, destfile, starttime

  title := GetNewMacroName()
  outfile := A_ScriptDir "\" title ".mak"
  ActivateGameWin()
  dfpath := GetWinPath("A") ; active window is the instance of DF we want to send to
  SplitPath, dfpath, , dfpath
  destfile := dfpath "\data\init\macros\" title ".mak"

  ; Clock how long it takes
  starttime := A_TickCount
  if (ConvertBlueprint(SelectedFile, outfile, SelectedSheetIndex, "macro", title, StartPos, RepeatPattern, false))
  {
    ; Copy to DF dir
    FileCopy, %outfile%, %destfile%, 1
    if (ErrorLevel > 0)
    {
      MsgBox, Error: Could not copy macro file`nFrom: %outfile%`nTo: %destfile%
      return false
    }
    else
    {
      elapsed := A_TickCount - starttime
      PlayMacro(elapsed / 3) ; macro playback delays are proportional to qfconvert runtime
      FileDelete, %destfile%
      FileDelete, %outfile%
    }
  }
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

  if (ConvertBlueprint(SelectedFile, outfile, SelectedSheetIndex, "key", "visualize", StartPos, RepeatPattern, visualizing))
  {
    ; Read file contents
    FileRead, output, %outfile%
    if (!output)
    {
      MsgBox, Error: Could not read keys output file`nFrom: %outfile%`
      return false
    }
    else
    {
      ;MsgBox % output
      SendKeys(output)
    }
  }
  ; clean up
  FileDelete, %outfile%
  return true
}
