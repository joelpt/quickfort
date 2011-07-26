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


;; ---------------------------------------------------------------------------
;; Detect when mouse is hovering over a window title bar.
IsMouseOverTitleBar()
{
    return (NCHITTest() == 2)
}

;; ---------------------------------------------------------------------------
;; Magic AHK/Win32 juju
NCHITTest()
{
  SetBatchLines, -1
  CoordMode, Mouse, Screen
  SetMouseDelay, -1 ; no pause after mouse clicks
  SetKeyDelay, -1 ; no pause after keys sent
  MouseGetPos, ClickX, ClickY, WindowUnderMouseID, CtrlUnderMouseID

  if (CtrlUnderMouseID == "ToolbarWindow321")
    return 0

  ;WinActivate, ahk_id %WindowUnderMouseID%
  ; WM_NCHITTEST
  SendMessage, 0x84,, ( ClickY << 16 )|ClickX,, ahk_id %WindowUnderMouseID%
    /*
    #define HTERROR             (-2)
    #define HTTRANSPARENT       (-1)
    #define HTNOWHERE           0
    #define HTCLIENT            1
    #define HTCAPTION           2
    #define HTSYSMENU           3
    #define HTGROWBOX           4
    #define HTSIZE              HTGROWBOX
    #define HTMENU              5
    #define HTHSCROLL           6
    #define HTVSCROLL           7
    #define HTMINBUTTON         8
    #define HTMAXBUTTON         9
    #define HTLEFT              10
    #define HTRIGHT             11
    #define HTTOP               12
    #define HTTOPLEFT           13
    #define HTTOPRIGHT          14
    #define HTBOTTOM            15
    #define HTBOTTOMLEFT        16
    #define HTBOTTOMRIGHT       17
    #define HTBORDER            18
    #define HTREDUCE            HTMINBUTTON
    #define HTZOOM              HTMAXBUTTON
    #define HTSIZEFIRST         HTLEFT
    #define HTSIZELAST          HTBOTTOMRIGHT
    #if(WINVER >= 0x0400)
    #define HTOBJECT            19
    #define HTCLOSE             20
    #define HTHELP              21
    */
  return ErrorLevel
}
