;; Shows and handles events for the sheet selection and blueprint info GUI
;; which is shown after file selection.


;; ---------------------------------------------------------------------------
;; Initialize the sheet selection/info GUI.
InitGui(listViewEnabled)
{
  global
  local offset =

  Gui, Destroy
  Gui, Font, S9, Verdana

  offset := 175
  if (listViewEnabled) {
    Gui, Add, ListView, r20 w220 h360 gSheetListView vSelectedSheetIndex AltSubmit -Hdr -Multi, Blueprint
    offset += 220
  }

  Gui, Font, bold
  Gui, Add, Text, x+5 ym+5 w400 vSheetName, sheetname
  Gui, Font, norm
  Gui, Add, Text, y+10 w400 h300 vSheetInfo, sometext
  Gui, Add, Button, y+5 w75 gButtonCopyText, &Copy text
  Gui, Add, Button, x+5 w100 gButtonEditBlueprint, &Edit blueprint
  Gui, Add, Button, x+65 w75 Default, OK
  Gui, Add, Button, x+5 w75, Cancel
}


;; ---------------------------------------------------------------------------
;; Show the sheet selection/info GUI.
ShowSheetInfoGui()
{
  global
  local listViewEnabled, selectorChanged, needRefresh

  needRefresh := (SheetGuiSelectedFile != SelectedFile)
  listViewEnabled := (SheetCount > 1)

  if (needRefresh)
    SelectedSheetIndex := 0 ; default to selecting first row

  if (needRefresh) ; need to update the GUI layout/listview?
  {
    ; rebuild the gui
    InitGui(listViewEnabled)

    if (listViewEnabled)
    {
      ; reload the ListView's elements
      LV_Delete()
      Loop, % SheetCount
      {
        index := A_Index - 1
        name := Name%index%
        LV_Add("", name)
      }
    }
  }

  ; Update gui to our current sheet
  UpdateGuiSheetInfo(SelectedSheetIndex)

  ; Show the GUI now
  Gui, Show
  WinWaitActive, ahk_class AutoHotkeyGUI

  ; Set keyboard focus properly
  if (listViewEnabled)
  {
    GuiControl, Focus, SysListView321
    ; Set the current selection of the ListView
    LV_Modify(SelectedSheetIndex + 1, "Select Focus")
  }
  else
  {
    GuiControl, Focus, Button3
  }

  SheetGuiSelectedFile := SelectedFile
  return
}


;; ---------------------------------------------------------------------------
;; Handle events for the sheet selector listview.
SheetListView:
{
  if ( (A_GuiEvent == "I" && InStr(ErrorLevel, "S", true)) || (A_GuiEvent == "DoubleClick") )
  {
    LV_GetText(RowText, A_EventInfo)  ; Get the text from the row's first field.
    ;MsgBox, You selected row number %A_EventInfo%. Text: "%RowText%"
    index := A_EventInfo - 1
    UpdateGuiSheetInfo(index)
    SelectedSheetIndex := index
    if (GuiEvent == "DoubleClick")
      Goto ButtonOK
  }
  return
}


;; ---------------------------------------------------------------------------
;; Handle clicking on the OK button
ButtonOK:
{
  Gui, Submit
  ShowTip()
  ReadyToBuild := True

  StartPos := ""
  StartPosLabel := ""
  RepeatPattern := ""
  SetVarsByBuildType(BuildType%SelectedSheetIndex%)

  ShowTip()
  return
}


;; ---------------------------------------------------------------------------
;; Handle cancelling/escaping/closing the GUI
ButtonCancel:
GuiClose:
GuiEscape:
{
  Gui, Cancel
  if (!ReadyToBuild)
  {
    SelectedFile =
  }
  ShowTip()
  return
}


;; ---------------------------------------------------------------------------
;; Handle the Copy Text button
ButtonCopyText:
{
  clipboard := GuiText
}

;; ---------------------------------------------------------------------------
;; Handle the Edit Blueprint button
ButtonEditBlueprint:
{
  editing := SelectedFile
  Gosub ButtonCancel
  Run, %editing%
}


;; ---------------------------------------------------------------------------
;; Update the GUI's sheet info pane to a new sheet.
UpdateGuiSheetInfo(index)
{
  global
  local newtext, newtitle

  newtitle := SelectedFilename
  if (SelectedFilename != Name%index%)
    newtitle := newtitle ": " Name%index%

  newtext =
  if (StartPosition%index% != "(1, 1)" && !StartComment%index%)
  {
    newtext := "Starts at " StartPosition%index%

    if (StartComment%index%)
    {
      newtext := newtext " (" StartComment%index% ")"
    }
    newtext := newtext "`n`n"
  }

  newtext := newtext Comment%index%
  newtext := newtext "`n`nCommand usage frequencies:`n" CommandUseCounts%index%
  GuiControl,, SheetName, %newtitle%
  GuiControl,, SheetInfo, %newtext%
  GuiText := newtitle "`n`n" newtext
  return
}
