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
  ShowFullTip := 1

  ; Init saved gui state
  LoadAppState()

  ; Init mousetip
  InitMouseTip()

  ; Show mousetip
  ShowTip()

  ; Clean up possible leftover temp files
  CleanUpTempFiles()

  ; Set onexit handler
  OnExit, ExitSub

  ; Show tray tip unless we're already in DF
  if (ShowStartupTrayTip && !WinActive("Dwarf Fortress"))
  {
    TrayTip, Quickfort, Version %Version%, , 1
  }

  return
}

;; ---------------------------------------------------------------------------
;; Called when AHK exits.
ExitSub:
  CleanUpTempFiles()
  ExitApp

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
  ShowStartupTrayTip := 1
  ShowMouseTooltip := 1
  EnableSafetyAbort := 1
  MouseTooltipUpdateMs := 15
  return
}

;; ---------------------------------------------------------------------------
;; Load options from options.txt
LoadOptions()
{
  if (!FileExist("config/options.txt"))
  {
    MsgBox, Error: Quickfort missing config/options.txt. Make sure options.txt exists and you are launching Quickfort from its own directory.`n`nExiting.
    ExitApp
  }

  Loop, Read, config/options.txt
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
  global SelectedFolder, LastRepeatPattern, LastCommandLine, ShowFullTip, PlaybackMode
  IniRead, PlaybackMode, state.ini, GUI, PlaybackMode
  IniRead, SelectedFolder, state.ini, GUI, LastFolder
  IniRead, LastRepeatPattern, state.ini, GUI, LastRepeatPattern
  IniRead, LastCommandLine, state.ini, GUI, LastCommandLine
  IniRead, ShowFullTip, state.ini, GUI, ShowFullTip

  if (SelectedFolder == "ERROR")
    SelectedFolder := ""

  if (LastRepeatPattern == "ERROR")
    LastRepeatPattern := ""

  if (LastCommandLine == "ERROR")
    LastCommandLine := ""

  if (ShowFullTip == "ERROR")
    ShowFullTip := 1

  return
}


;; ---------------------------------------------------------------------------
;; Save app state to state.ini
SaveAppState()
{
  global SelectedFolder, LastRepeatPattern, LastCommandLine, ShowFullTip, PlaybackMode
  IniWrite, %PlaybackMode%, state.ini, GUI, PlaybackMode
  IniWrite, %SelectedFolder%, state.ini, GUI, LastFolder
  IniWrite, %ShowFullTip%, state.ini, GUI, ShowFullTip

  if (LastCommandLine)
    IniWrite, %LastCommandLine%, state.ini, GUI, LastCommandLine

  if (LastRepeatPattern)
    IniWrite, %LastRepeatPattern%, state.ini, GUI, LastRepeatPattern

  return
}


;; ---------------------------------------------------------------------------
;; Clean up old temp files
CleanUpTempFiles()
{
  FileDelete, %A_ScriptDir%\@qf*.*
}