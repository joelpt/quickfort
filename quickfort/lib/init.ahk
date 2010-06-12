;; General startup initialization related stuff.

;; ---------------------------------------------------------------------------
;; Initialize on startup
Init()
{
  global
  SetTitleMatchMode, 3

  ; Win-Alt-C "makes" the release if you're running the .ahk script
  if (!A_IsCompiled)
    Hotkey, #!C, CompileToExe

  ; load options
  SetDefaultOptions()
  LoadOptions()

  ; Get display dimensions
  SysGet, ScreenWidth, 16
  SysGet, ScreenHeight, 17

  ; set global variable defaults
  ReadyToBuild := 0
  Building := 0
  Comment := ""
  SelectedFile := ""
  SelectedFilename := ""
  SelectedSheetIndex =
  SelectedFolder := ""
  StartPos := ""
  StartPosLabel := ""
  RepeatPattern =
  SheetGuiSelectedFile := ""
  SheetGuiLastListViewEnabled =

  ; Init saved gui state
  LoadAppState()

  ; Init mousetip
  InitMouseTip()

  ; Show mousetip
  ShowTip()


  if (ShowStartupTrayTip && !WinActive("Dwarf Fortress"))
  {
    TrayTip, Quickfort, Version %Version%, , 1
  }

  return
}


;; ---------------------------------------------------------------------------
;; Set default options so players don't necessarily have to overwrite
;; options.txt with new QF versions
SetDefaultOptions()
{
  global
  PlaybackMode := "key"
  DelayMultiplier := 1
  KeyPressDuration := 1
  EmbeddedDelayDuration := 250
  SendMode := "ControlSend"
  KeyExitMenu := "{Esc}"
  KeyLeft := "4"
  KeyRight := "6"
  KeyUp := "8"
  KeyDown := "2"
  KeyUpZ := "+5"
  KeyDownZ := "^5"
  KeyUpLeft := "7"
  KeyUpRight := "9"
  KeyDownLeft := "1"
  KeyDownRight := "3"
  UseDiagonalMoveKeys := 1
  UseLongConstructions := 1
  DisableBacktrackingOptimization := 0
  DisableKeyOptimizations := 0
  DisableShiftOptimizations := 1
  ShowSplashBox := 1
  ShowStartupTrayTip := 1
  ShowMouseTooltip := 1
  ShowCommentBox := 1
  MutedSound := 0
  DisableSafetyAbort := 0
  MouseTooltipUpdateMs := 20
  AliasesPath := "aliases.txt"
  DebugOn := 0
  return
}

;; ---------------------------------------------------------------------------
;; Load options from options.txt
LoadOptions()
{
  if (!FileExist("options.txt"))
  {
    MsgBox, Error: Quickfort missing options.txt. Make sure options.txt exists and you are launching Quickfort from its own directory.`n`nExiting.
    ExitApp
  }

  Loop, Read, options.txt
  {
    if (SubStr(A_LoopReadLine, 1, 1) != "#" && StrLen(A_LoopReadLine) > 3) ; skip comments and empty lines
    {
      StringSplit, optionsArray, A_LoopReadLine, `=, %A_Space%%A_Tab%
      if (optionsArray0 == 2) {
        %optionsArray1% := optionsArray2  ; sometimes AHK is pretty cool
      }
    }
  }
}


;; ---------------------------------------------------------------------------
;; Load app state from state.ini
LoadAppState()
{
  global SelectedFolder, LastRepeatPattern
  IniRead, SelectedFolder, state.ini, GUI, LastFolder
  IniRead, LastRepeatPattern, state.ini, GUI, LastRepeatPattern

  if (SelectedFolder == "ERROR")
    SelectedFolder := ""

  if (LastRepeatPattern == "ERROR")
    LastRepeatPattern := ""

  return
}


;; ---------------------------------------------------------------------------
;; Save app state to state.ini
SaveAppState()
{
  global SelectedFolder, LastRepeatPattern
  IniWrite, %SelectedFolder%, state.ini, GUI, LastFolder

  if (LastRepeatPattern)
    IniWrite, %LastRepeatPattern%, state.ini, GUI, LastRepeatPattern

  return
}
