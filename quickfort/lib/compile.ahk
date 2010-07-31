;; ---------------------------------------------------------------------------
CompileToExe:
  CompileToExeFunc()
  return

;; ---------------------------------------------------------------------------
;; "Makes" Quickfort.
CompileToExeFunc()
{
  global Version

  if (A_IsCompiled)
    return

  MsgBox, Compiling as version %Version%
  icon := A_ScriptDir . ReplaceExtension(A_ScriptName, ".ico")

  MsgBox, "c:\Program Files (x86)\AutoHotkey\Compiler\Ahk2Exe.exe" /in "%A_ScriptFullPath%" /icon "%icon%"

  FileDelete, Quickfort.exe
  RunWait, "c:\Program Files (x86)\AutoHotkey\Compiler\Ahk2Exe.exe" /in "%A_ScriptFullPath%" /icon "%icon%"

  FileCopy, Quickfort.exe, release
  Sleep 1000

  FileCopy, releases\*.*, ..\release

  ;RunWait, zip -9 -r releases\Quickfort.zip aliases.txt Blueprints options.txt Quickfort.ahk Quickfort.exe readme.txt
  ;Sleep 1000

  ;FileCopy, releases\Quickfort.zip, releases\Quickfort_%Version%.zip
  ;Sleep 1000

  ;Run, releases\Quickfort_%Version%.zip

  ;MsgBox, 4, , Upload?

  ;IfMsgBox Yes
  ;{
  ;  to := "m:\sun2design.com\quickfort\"
  ;  FileCopy, releases\Quickfort_%Version%.zip, %to%, 1
  ;  FileCopy, releases\Quickfort.zip, %to%, 1
  ;  FileCopy, readme.txt, %to%, 1
  ;  Run, http://sun2design.com/quickfort
  ;}
}
