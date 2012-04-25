;; Connector for calling qfconvert.

;; ---------------------------------------------------------------------------
;; call qfconvert.exe with given parameters
ExecQfconvert(infile, outfile, params)
{
  FileDelete, %outfile%

  if (A_IsCompiled) {
    basedir := A_ScriptDir
    cmd = "%A_ScriptDir%\qfconvert.exe" "%infile%" "%outfile%" %params%
  }
  else {
    basedir := RegExReplace(A_ScriptDir, "(.+)[/\\].*", "$1") "\qfconvert"
    cmd = "python.exe" "%basedir%\qfconvert.py" "%infile%" "%outfile%" %params%
  }

  ;MsgBox %cmd%
  RunWait %cmd%, %basedir%, Hide

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
      StringReplace, output, output, Exception:, Error in qfconvert:
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
GetRandomFileName()
{
  ; We use macro names that should always go in increasing sort order in DF's UI.
  ; This is done by recording the datetime in local timezone and current tick
  ; count when QF launches, then whenever this method is called we compute
  ; the delta in the tick count from launch and add that amount of time to the
  ; remembered launch datetime. This helps ensure that if the machine date/time
  ; changes while QF is running we won't start getting out-of-order entries
  ; in the DF macro menu.

  ; We always delete our macros after use. However DF doesn't
  ; update its macro list when macros are deleted; thus the desire to have our new
  ; macro always be sorted to the top item in DF's macro list. It allows QF to just
  ; use Ctrl+L, Up, Enter to select the last macro in the list, which should always
  ; be our just-created macro due to this naming methodology.

  global LaunchedOn, LaunchedTickCount

  elapsedMS := A_TickCount - LaunchedTickCount
  elapsedSec := elapsedMS / 1000
  newDate := LaunchedOn
  EnvAdd, newDate, %elapsedSec%, Seconds
  dateStr := SubStr(newDate, 3, 14)
  title = ~qf%dateStr% ;%A_MSec% <-- not needed; we'll never do 2 in 1 second
  return title
}
