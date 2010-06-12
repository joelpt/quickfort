;; Functions related to blueprints and processing them.


;; ---------------------------------------------------------------------------
;; do blueprint conversion via qfconvert
ConvertBlueprint(filename, outfile, sheetid, mode, title, startpos, transformation, visualize)
{
  Tip("Thinking...")

  modecmd = --mode="%mode%"

  titlecmd =
  if (title) {
    titlecmd = --title="%title%"
  }

  transcmd =
  if (transformation) {
    transcmd = --transform="%transformation%"
  }

  startposcmd =
  if (startpos) {
    startposcmd = --position="%startpos%"
  }

  sheetidcmd =
  if (sheetid) {
    sheetidcmd = --sheetid="%sheetid%"
  }

  visualizecmd =
  if (visualize) {
    visualizecmd = --visualize
  }


  params = %modecmd% %titlecmd% %transcmd% %startposcmd% %sheetidcmd% %visualizecmd%
  return ExecQfConvert(filename, outfile, params)
}


;; ---------------------------------------------------------------------------
;; get info about blueprint via qfconvert
GetBlueprintInfo(filename)
{
  global
  local params
  local outfile
  local result

  Tip("Reading blueprint...")

  params = --info
  outfile := A_ScriptDir "\" GetNewMacroName() ".tmp"
  result := ExecQfConvert(filename, outfile, params)
  FileDelete, %outfile%

  ClearTip()

  if (result)
  {
    ; prepare data for Loop Parse
    StringReplace, result, result, ----, ¢, All
    ; parse contents out
    cnt := 0
    Loop, Parse, result, ¢
    {
      info = %A_LoopField% ; whitespace trim
      if (StrLen(info) > 3)
      {
        needle := "Sheet id (\d+)\RBlueprint name: (.+)\RBuild type: (.+)\RComment: (.*)\RStart position: (.+)\RStart comment: (.*)\RFirst layer width: (.+)\RFirst layer height: (.+)\RLayer count: (.+)\RCommand use counts: (.*)\R*"
        if (!RegExMatch(info, needle, matches))
        {
          MsgBox, Error reading blueprint information from qfconvert.py output file %outfile%
          return False
        }
        Name%cnt% := matches2
        BuildType%cnt% := matches3
        StringReplace, Comment%cnt%, matches4, \n, `n, All
        StartPosition%cnt% := matches5
        StartComment%cnt% := matches6
        Width%cnt% := matches7
        Height%cnt% := matches8
        LayerCount%cnt% := matches9
        CommandUseCounts%cnt% := matches10

        cnt += 1
      }
      SheetCount := cnt
    }
    return True
  }
  else
    return False
}


;; ---------------------------------------------------------------------------
;; Set StartPos/Label and update the mouse tip
SetStartPos(position, label)
{
  global StartPos, StartPosLabel

  ; set start pos
  StartPos := position
  StartPosLabel := label

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
