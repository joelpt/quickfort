;; Functions related to reading/writing/checking DF's init.txt

;; ---------------------------------------------------------------------------
;; Check DF's init.txt for [MACRO_MS:1+] and give the user an opportunity
;; to have QF modify the file to have [MACRO_MS:0] instead.
CheckDFMacroMS()
{
  global DoMacroMSCheck

  if (!DoMacroMSCheck)
    return

  WinWaitActive, Dwarf Fortress

  val := GetDFInitTxtSetting("MACRO_MS")

  if (val == -255)
    return  ; file/setting not found
  
  if (val == 0)
    return  ; already set to 0ms
  
  msg =
  (
Quickfort has detected that this instance of Dwarf Fortress has a
setting of [MACRO_MS:%val%] in its data/init/init.txt file.

Values for MACRO_MS higher than 0 can make Quickfort's
macro-based playback run very slowly.

Quickfort can change this setting for you. Please choose:

YES: Modify my DF's init.txt and set [MACRO_MS:0]
NO: Don't modify now, but ask again next time
CANCEL: Don't modify and never ask me again
  )

  MsgBox, 3, Quickfort - Warning, %msg%
  IfMsgBox, Yes
  {
    ActivateGameWin()
    path := SetDFInitTxtSetting("MACRO_MS", "0")
    if (path == -255)
    {
      MsgBox, There was a problem modifying init.txt. Quickfort will continue.
      return
    }
    MsgBox, MACRO_MS set successfully. Please restart Dwarf Fortress for the change to take effect.`n`nModified file path:`n%path%
    return
  }

  IfMsgBox, Cancel
  {
    DoMacroMSCheck := 0
    SaveAppState()
    return
  }

  ; User clicked No - do nothing
  return
}


;; ---------------------------------------------------------------------------
;; Examine DF data/init/init.txt and retrieve value of named setting.
;; Currently expects DF window to be active (this allows for multiple
;; simultaneous DF instances).
;; Returns the setting's value, or -255 if file or setting could not be found.
GetDFInitTxtSetting(name)
{
  dfpath := GetWinPath("A") ; active window is the instance of DF we want 
  SplitPath, dfpath, , dfpath
  initpath := dfpath "\data\init\init.txt"

  FileRead, data, %initpath%
  if (!data)
  {
    ;; Did not locate init.txt
    return -255
  }

  evalOK := RegExMatch(data, "\[" name "\:(.*)\]", evalMatch)
  if (!evalOK)
  {
    ;; Did not locate setting
    return -255
  }

  ;; Got a match
  return evalMatch1
}

;; ---------------------------------------------------------------------------
;; Set the value of an EXISTING setting in DF data/init/init.txt.
;; Currently expects DF window to be active (this allows for multiple
;; simultaneous DF instances).
;; Returns the setting's new value, or -255 if file could not be found.
SetDFInitTxtSetting(name, newValue)
{
  dfpath := GetWinPath("A") ; active window is the instance of DF we want 
  SplitPath, dfpath, , dfpath
  initpath := dfpath "\data\init\init.txt"

  FileRead, data, %initpath%
  if (!data)
  {
    ;; Did not locate init.txt
    return -255
  }

  changed := RegExReplace(data, "\[" name "\:(.*)\]", "[" name ":" newValue "]")
  FileDelete, %initpath%
  FileAppend, %changed%, %initpath%
  return initpath
}

