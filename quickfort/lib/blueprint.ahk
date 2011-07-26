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
  outfile := A_ScriptDir "\" GetRandomFileName() ".tmp"
  result := ExecQfConvert(filename, outfile, params)

  ClearTip()

  if (result)
  {
    ; prepare data for Loop Parse
    StringReplace, result, result, >>>>, ¢, All
    ; parse contents out
    cnt := 0
    Loop, Parse, result, ¢
    {
      info = %A_LoopField% ; AHK style whitespace trim
      if (StrLen(info) > 3)
      {
        needle := "Sheet id (\d+)\RBlueprint name: (.+)\RBuild type: (.+)\RComment: (.*)\RStart position: (.+)\RStart comment: (.*)\RFirst layer width: (.+)\RFirst layer height: (.+)\RLayer count: (.+)\RUses manual material selection: (.+)\RCommand use counts: (.*)\RBlueprint preview:\R((.+\R)+)#"
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
        UsesManualMats%cnt% := matches10
        CommandUseCounts%cnt% := matches11
        BlueprintPreview%cnt% := matches12
        cnt += 1
      }
      SheetCount := cnt
    }
    FileDelete, %outfile%
    return True
  }
  else
    return False
}

