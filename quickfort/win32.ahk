;; This stuff is Windows OS specific.


;; ---------------------------------------------------------------------------
;; Get the path of the window with given title parameter.
GetWinPath(title)
{
  WinGet, pid, PID, %title%

  VarSetCapacity(sFilePath, 260)

  pFunc := DllCall("GetProcAddress"
     , "Uint", DllCall("GetModuleHandle", "str", "kernel32.dll")
     , "str", "GetCommandLineA")

  hProc := DllCall("OpenProcess", "Uint", 0x043A, "int", 0, "Uint", pid)

  hThrd := DllCall("CreateRemoteThread", "Uint", hProc, "Uint", 0, "Uint", 0
     , "Uint", pFunc, "Uint", 0, "Uint", 0, "Uint", 0)

  DllCall("WaitForSingleObject", "Uint", hThrd, "Uint", 0xFFFFFFFF)
  DllCall("GetExitCodeThread", "Uint", hThrd, "UintP", pcl)

  DllCall("psapi\GetModuleFileNameExA", "Uint", hProc, "Uint", 0, "str", sFilePath, "Uint", 260)
  ; DllCall("psapi\GetProcessImageFileNameA", "Uint", hProc, "str", sFilePath, "Uint", 281)

  DllCall("CloseHandle", "Uint", hThrd)
  DllCall("CloseHandle", "Uint", hProc)

  return sFilePath
}