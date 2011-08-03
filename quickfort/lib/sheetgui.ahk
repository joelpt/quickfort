;; Shows and handles events for the sheet selection and blueprint info GUI
;; which is shown after file selection.


;; ---------------------------------------------------------------------------
;; Initialize the sheet selection/info GUI.
InitGui(listViewEnabled)
{
  global

  Gui, Destroy
  Gui, Font, S9, Verdana

  if (listViewEnabled) {
    ;Gui, Add, Text, r20 w220 h20, Worksheets
    Gui, Add, ListView, r20 w160 h460 gSheetListView vSelectedSheetIndex AltSubmit -Hdr -Multi, Blueprint
  }

  Gui, Font, bold
  Gui, Add, Text, x+5 ym+5 w600 vSheetName, sheetname
  Gui, Font, norm
  Gui, Font, S9, Courier
  Gui, Font, S9, Courier New
  Gui, Font, S9, Lucida Console
  Gui, Add, Edit, y+10 w600 h400 vSheetInfo VScroll, sometext
  Gui, Font, S9, Verdana
  Gui, Add, Button, y+5 w75 gButtonCopyText, &Copy text
  Gui, Add, Button, x+5 w100 gButtonEditBlueprint, &Edit blueprint
  Gui, Add, Button, x+265 w75 Default, OK
  Gui, Add, Button, x+5 w75, Cancel
}


;; ---------------------------------------------------------------------------
;; Show the sheet selection/info GUI.
ShowSheetInfoGui()
{
  global
  local listViewEnabled, selectorChanged, needRefresh

  needRefresh := (GuiSelectedFile != SelectedFile)
  listViewEnabled := (SheetCount > 1)

  ;if (needRefresh)
  GuiSelectedSheetIndex := 0 ; default to selecting first row

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
  UpdateGuiSheetInfo(GuiSelectedSheetIndex)
  
  ; Set keyboard focus properly
  if (listViewEnabled)
  {
    GuiControl, Focus, SysListView321
    ; Set the current selection of the ListView
    LV_Modify(GuiSelectedSheetIndex + 1, "Select Focus")
  }
  else
  {
    GuiControl, Focus, Button3
  }

  ; Show the GUI now
  Gui, Show
  WinWaitActive, ahk_class AutoHotkeyGUI

  ; Set keyboard focus properly (again)
  if (listViewEnabled)
  {
    GuiControl, Focus, SysListView321
    ; Set the current selection of the ListView
    LV_Modify(GuiSelectedSheetIndex + 1, "Select Focus")
  }
  else
  {
    GuiControl, Focus, Button3
  }

  GuiSelectedFile := SelectedFile
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
    GuiSelectedSheetIndex := index
    if (A_GuiEvent == "DoubleClick")
      Goto ButtonOK
  }
  return
}


;; ---------------------------------------------------------------------------
;; Handle clicking on the OK button
ButtonOK:
{
  SelectedSheetIndex := GuiSelectedSheetIndex
  Gui, Submit
  ShowTip()
  ReadyToBuild := True

  StartPos := ""
  StartPosLabel := ""
  RepeatPattern := ""
  SetVarsByBuildType(BuildType%SelectedSheetIndex%)

  ActivateGameWin()
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
  MsgBox, Text copied to clipboard.
  return
}

;; ---------------------------------------------------------------------------
;; Handle the Edit Blueprint button
ButtonEditBlueprint:
{
  editing := SelectedFile
  ;Gosub ButtonCancel
  Run, %editing%
  return
}


;; ---------------------------------------------------------------------------
;; Update the GUI's sheet info pane to a new sheet.
UpdateGuiSheetInfo(index)
{
  global
  local newtext, newtitle

  newtitle := SelectedFilename
  if (SelectedFilename != Name%index%)
    newtitle := newtitle " [" Name%index% "]"

  newtext =
  newtext := newtext "#" BuildType%index%

  if (StartPosition%index% != "(1, 1)")
  {
    newtext := newtext " - starts at " StartPosition%index%

    if (StartComment%index%)
    {
      newtext := newtext " (" StartComment%index% ")"
    }
  }

  newtext := newtext "`n`n"
  newtext := newtext Comment%index%
  newtext := newtext "`n"
  
  if (UsesManualMats%index% = "true")
  {
    newtext := newtext "`n** This blueprint uses manual material selection **`n"
  }

  newtext := newtext "`nCommand usage frequencies:`n" CommandUseCounts%index%
  newtext := newtext "`n`nDimensions: " Width%index% "w x " Height%index% "h"
  newtext := newtext "`n`n" BlueprintPreview%index%
  GuiControl,, SheetName, %newtitle%
  GuiControl,, SheetInfo, %newtext%
  GuiText := newtitle "`n`n" newtext
  return
}
