;; Quickfort main entry point.

#SingleInstance force
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.

; Quickfort version number.
Version := "2.00"

; Initialize Quickfort.
Init()

; Done with startup stuff.
return


; Includes are best put at the end of AHK scripts because they are added and executed inline
; wherever the #include appears
#include blueprint.ahk
#include compile.ahk
#include convert.ahk
#include df.ahk
#include filepicker.ahk
#include hotkeys.ahk
#include init.ahk
#include log.ahk
#include misc.ahk
#include mousetip.ahk
#include qfconvert.ahk
#include sheetgui.ahk
#include win32.ahk
