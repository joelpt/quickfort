;; Functions related to managing QF's application state (global variables).

;; ---------------------------------------------------------------------------
;; Set StartPos/Label and update the mouse tip
SetStartPos(position, label)
{
  global StartPos, StartPosLabel, LastMacroWasPlayed, LastSendKeys

  ; set start pos
  StartPos := position
  StartPosLabel := label

  ; ensure a new conversion is performed
  LastMacroWasPlayed := false
  LastSendKeys =

  UpdateTip()
}


;; ---------------------------------------------------------------------------
;; Set global variables which are dependent on the current build type
SetVarsByBuildType(buildtype)
{
  global UserInitKey, UserInitText, KeyDelay, DelayMultiplier

  ; Set user-init key description based on build buildtype
  if (buildtype = "build")
  {
    UserInitKey = b o
    UserInitText = build road
    KeyDelay := DelayMultiplier * 3
  }
  else if (buildtype = "dig")
  {
    UserInitKey = d
    UserInitText = designations
    KeyDelay := DelayMultiplier
  }
  else if (buildtype = "place")
  {
    UserInitKey = p
    UserInitText = stockpiles
    KeyDelay := DelayMultiplier * 2
  }
  else if (buildtype = "query")
  {
    UserInitKey = q
    UserInitText = set building tasks/prefs
    KeyDelay := DelayMultiplier * 2
  }
  else
  {
    MsgBox, Unrecognized buildtype '%buildtype%' specified in %SelectedFilename%. buildtype should be one of #build #dig #place #query
    return false
  }
  return true
}


;; ---------------------------------------------------------------------------
;; Set global variables which are dependent on the current filepath
SetSelectedFile(filepath)
{
  global SelectedFile, SelectedSheetIndex, SelectedFilename, SelectedFolder, SelectedModifiedOn
  
  SelectedFile := filepath
  SelectedSheetIndex =

  ; split filename up into parts we use elsewhere
  SplitPath, SelectedFile, SelectedFilename, SelectedFolder

  FileGetTime, SelectedModifiedOn, %SelectedFile%, M
}
