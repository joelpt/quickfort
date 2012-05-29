;; Quickfort main entry point.

#SingleInstance force
#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.

; Quickfort version number.
Version := "2.04"

; Initialize Quickfort.
Init()

; Done with startup stuff.
return

; Includes are best put at the end of AHK scripts because they are added and executed inline
; wherever the #include appears
#include lib/blueprint.ahk
#include lib/compile.ahk
#include lib/convert.ahk
#include lib/df_init_txt.ahk
#include lib/df_interact.ahk
#include lib/df_manualmats.ahk
#include lib/filepicker.ahk
#include lib/hotkeys.ahk
#include lib/init.ahk
#include lib/log.ahk
#include lib/misc.ahk
#include lib/mousetip.ahk
#include lib/qfconvert.ahk
#include lib/screenclipper.ahk
#include lib/sheetgui.ahk
#include lib/state.ahk
#include lib/util.ahk
#include lib/win32.ahk
