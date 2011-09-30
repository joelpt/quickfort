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
  SelectedModifiedOn =
  CommandLineMode := False
  CommandLineFile =
  StartPos := ""
  StartPosLabel := ""
  RepeatPattern =
  SheetGuiSelectedFile := ""
  SheetGuiLastListViewEnabled =
  ShowFullTip := 1
  LastSendKeys =
  LastMacroWasPlayed := false
  LaunchedOn := A_Now
  LaunchedTickCount := A_TickCount
  MemorizedMats := {}
  MatMenuCoords := {}
  SelectingMat := false
  LastMacroSentToWinID =

  ; Init saved gui state
  LoadAppState()

  ; Init subsystems
  InitHotkeys()
  InitMouseTip()
  InitScreenClipper()

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

  ; Ready our MACRO_MS checker
  CheckDFMacroMS()
  return
}

;; ---------------------------------------------------------------------------
;; Called when AHK exits.
ExitSub:
  CleanUpTempFiles()
  ExitApp

;; ---------------------------------------------------------------------------
;; Set default options so players don't necessarily have to overwrite
;; their options.txt with new QF versions' options.txt
SetDefaultOptions()
{
  global
  PlaybackMode := "macro"
  DelayMultiplier := 1
  KeyPressDuration := 1
  EmbeddedDelayDuration := 250
  SendMode := "ControlSend"
  ShowStartupTrayTip := 1
  ShowMouseTooltip := 1
  MouseTooltipUpdateMs := 15
  KeyMacroLoad = ^l
  KeyMacroHighlightLastMacro = {Up}
  KeyMacroSelectMacro = {Enter}
  KeyMacroPlay = ^p
  KeyMacroRecord = ^r
  KeyMacroSave = ^s
  KeyEnter = {Enter}
  KeySelectAll = +{Enter}
  KeyNextMenuItem = {+}
  KeyPrevMenuPage = {/}
  WaitForMatMenuMaxMS := 15000
  MaxMatSearchChecks := 200
  MatMenuSearchDelay := 50

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
;; Load app state from config/state.ini
LoadAppState()
{
  global

  IniRead, PlaybackMode, config/state.ini, GUI, PlaybackMode
  IniRead, SelectedFolder, config/state.ini, GUI, LastFolder
  IniRead, LastRepeatPattern, config/state.ini, GUI, LastRepeatPattern
  IniRead, LastCommandLine, config/state.ini, GUI, LastCommandLine
  IniRead, ShowFullTip, config/state.ini, GUI, ShowFullTip
  IniRead, DoMacroMSCheck, config/state.ini, GUI, DoMacroMSCheck

  ; defaults used when no such INI key exists
  if (PlaybackMode == "ERROR")
    PlaybackMode := "macro"

  if (SelectedFolder == "ERROR")
    SelectedFolder := ""

  if (LastRepeatPattern == "ERROR")
    LastRepeatPattern := ""

  if (LastCommandLine == "ERROR")
    LastCommandLine := ""

  if (ShowFullTip == "ERROR")
    ShowFullTip := 1

  if (DoMacroMSCheck == "ERROR")
    DoMacroMSCheck := 1

  return
}

;; ---------------------------------------------------------------------------
;; Save app state to config/state.ini
SaveAppState()
{
  global

  IniWrite, %PlaybackMode%, config/state.ini, GUI, PlaybackMode
  IniWrite, %ShowFullTip%, config/state.ini, GUI, ShowFullTip
  IniWrite, %SelectedFolder%, config/state.ini, GUI, LastFolder
  IniWrite, %DoMacroMSCheck%, config/state.ini, GUI, DoMacroMSCheck

  if (LastCommandLine)
    IniWrite, %LastCommandLine%, config/state.ini, GUI, LastCommandLine

  if (LastRepeatPattern)
    IniWrite, %LastRepeatPattern%, config/state.ini, GUI, LastRepeatPattern

  return
}


;; ---------------------------------------------------------------------------
;; Clean up old temp files
CleanUpTempFiles()
{
  FileDelete, %A_ScriptDir%\~qf*.*
}