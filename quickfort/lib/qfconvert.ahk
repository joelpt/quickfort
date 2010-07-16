;; Connector for calling qfconvert.

;; ---------------------------------------------------------------------------
;; call qfconvert.exe with given parameters
ExecQfconvert(infile, outfile, params)
{
  FileDelete, %outfile%

  cmd = "c:\lang\Python26\python" "d:\code\qf\trunk\qfconvert\qfconvert.py" "%infile%" "%outfile%" %params%
  ;MsgBox %cmd%
  RunWait %cmd%, d:\code\qf\trunk\qfconvert, Hide

  ready := False
  Loop 10
  {
    If FileExist(outfile) {
      ready = True
      break
    }
    Sleep 250
  }

  if (!ready)
  {
    MsgBox, Error: qfconvert did not return any results.
    return False
  }

  ; Check for exceptions
  Loop, Read, %outfile%
  {
    if (RegExMatch(A_LoopReadLine, "Exception:"))
    {
      ; Inform the user.
      FileRead, output, %outfile%
      StringReplace, output, output, Exception:, Error:
      StringReplace, output, output, \n, `n
      MsgBox % output
      ClearTip()
      return False
    }
    break
  }
  ClearTip()

  ; Return the call results
  FileRead, output, %outfile%
  return %output%
}


;; ---------------------------------------------------------------------------
GetNewMacroName()
{
  ; We use macro names that should always go in decreasing sort order in DF's UI
  ; (between reboots); and we always delete our macros after use. However DF doesn't
  ; update its macro list when macros are deleted; thus the desire to have our new
  ; macro always be sorted to the top item in DF's macro list. It allows QF to just
  ; use Ctrl+L, Enter to select our just-created macro.
  inverseticks := 4294967296 - A_TickCount
  title = @@@qf%inverseticks%
  return title
}
