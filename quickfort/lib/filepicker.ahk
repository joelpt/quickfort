;; Shows the file picker.

;; ---------------------------------------------------------------------------
;; file picker
SelectFile()
{
  global SelectedFolder
  filename =

  ; determine path
  if (!SelectedFolder)
  {
    if (A_IsCompiled)
        SelectedFolder := A_ScriptDir "\blueprints"
    else
        SelectedFolder := A_ScriptDir "\..\blueprints"
  }

  HideTip()

  ; show file selection box
  FileSelectFile, filename, , %SelectedFolder%, Select a Quickfort-compatible blueprint file, Blueprints (*.xls`; *.xlsx`; *.csv)
  ActivateGameWin()

  ShowTip()

  return filename
}
