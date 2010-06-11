;; Shows the file picker.

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
  ShowTip()
  return filename
}
