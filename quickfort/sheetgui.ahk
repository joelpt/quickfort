;; Shows and handles events for the sheet selection and blueprint info GUI
;; which is shown after file selection.


;; ---------------------------------------------------------------------------
;; Initialize the sheet selection/info GUI.
InitGui(withSelector)
{
  global
  local offset

  if (withSelector == LastInitGuiSelectorMode)
    return

  LastInitGuiSelectorMode := withSelector

  Gui, Destroy
  Gui, Font, S9, Verdana

  offset := 175
  if (withSelector) {
    Gui, Add, ListView, r20 w220 h360 gSheetListView vSelectedSheetIndex AltSubmit -Hdr, Blueprint
    offset += 220
  }

  Gui, Font, bold
  Gui, Add, Text, x+5 ym+5 w400 vSheetName, sheetname
  Gui, Font, norm
  Gui, Add, Text, y+10 w400 h300 vSheetInfo, sometext
  Gui, Add, Button, Default y+5 xm+%offset% w75, OK
  Gui, Add, Button, x+5 w75, Cancel
  Gui, Add, Button, x+5 w75 gButtonCopyText, Copy text
  ;Send, {Down 5} ; work around for having to press down twice to initially change selection
}


;; ---------------------------------------------------------------------------
;; Show the sheet selection/info GUI.
ShowSheetInfoGui()
{
  global

  if (SheetCount > 1)
  {
    ; show gui with sheet selector and populate the listview
    InitGui(True)
    LV_Delete()
    Loop, % SheetCount
    {
      index := A_Index - 1
      name := Name%index%
      if (index == SelectedSheetIndex)
        opts := "Select"
      else
        opts := ""
      LV_Add(opts, name)
    }
  }
  else
  {
    ; show gui without sheet selector and default SelectedSheetIndex to 0
    SelectedSheetIndex := 0
    InitGui(False)
  }
  ; Set showing sheet info to first sheet
  UpdateGuiSheetInfo(0)
  Gui, Show
  WinWaitActive, ahk_class AutoHotkeyGUI
  if (SheetCount > 0)
  {
    ; workaround for listview needing an extra keypress to start working (focus issue?)
    Sleep 100
    ControlSend, SysListView321, {Down}{Up}, ahk_class AutoHotkeyGUI
  }
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
