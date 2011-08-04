; Screen capture modification: rectangle/window/monitor
; Will ask you for filename via Windows file dialog

; Screen capture code:
; http://www.autohotkey.com/forum/topic18146.html


InitScreenClipper() {
   global
}
    

ClipScreenRegionToBitmap(byRef hBM, x, y, w, h) 
{
   mDC := DllCall("CreateCompatibleDC", "Uint", 0)
   hBM := CreateDIBSection(mDC, w, h)
   oBM := DllCall("SelectObject", "Uint", mDC, "Uint", hBM)
   hDC := DllCall("GetDC", "Uint", 0)
   DllCall("BitBlt", "Uint", mDC, "int", 0, "int", 0, "int", w, "int", h, "Uint", hDC, "int", x, "int", y, "Uint", 0x40000000 | 0x00CC0020)
   DllCall("ReleaseDC", "Uint", 0, "Uint", hDC)
   DllCall("SelectObject", "Uint", mDC, "Uint", oBM)
   DllCall("DeleteDC", "Uint", mDC)
}

;GetScreenRegionHash(x, y, w, h)
;{
;   ClipScreenRegionToBitmap(hBM, x, y, w, h)
;   sz := VarSetCapacity(bits, w*h*4, 0)
;   DllCall("GetBitmapBits", "UInt", hBM, "UInt", sz, "UInt", &bits)
;   DllCall("DeleteObject", "Uint", hBM)

;   hash := B64Hash(bits)
;   bits := ""
;   return hash
;}

ScreenRegionWaitChange(x, y, w, h, sendKeys, maxWaitMs, minWaitMs)
{
   sz := VarSetCapacity(bits, w*h*4, 0)

   ClipScreenRegionToBitmap(hBM, x, y, w, h)
   DllCall("GetBitmapBits", "UInt", hBM, "UInt", sz, "UInt", &bits)
   DllCall("DeleteObject", "Uint", hBM)
   init := CRC32(bits, sz)
   current := init

   Send, %sendKeys%
   Sleep, %minWaitMs%

   beginTicks := A_TickCount
   while (init == current)
   {
      if (A_TickCount - maxWaitMs > beginTicks)
         return false   ; waited longer than maxWaitMs
      ClipScreenRegionToBitmap(hBM, x, y, w, h)
      DllCall("GetBitmapBits", "UInt", hBM, "UInt", sz, "UInt", &bits)
      DllCall("DeleteObject", "Uint", hBM)
      current := CRC32(bits, sz)
   }

   return true
}


CaptureScreenRegionToFile(path, x, y, w, h)
{
   ClipScreenRegionToBitmap(hBM, x, y, w, h)   
   FileDelete, % path
   Convert(hBM, path, 95), DllCall("DeleteObject", "Uint", hBM)
   return FileExist(path)
}


;   if (saveToPath)
;   {
;      gosub CleanUp
;   }
   
;   bits := ""
;   ;DllCall("GetBitmapBits", "UInt", hBM, "UInt", cap, "UInt", &bits)
;   avg := "" ; B64Hash(bits)

;   VarSetCapacity(bits, 0)
;   ;DllCall("DeleteObject", "Uint", bits)
;   ;; just get the AvgBitMap color
;   ;;avg := AvgBitMap(hBM, nW * nH)
;   ;avg := "unset"
;   ;;BinaryToString(avg, bits, false)
;   ;;DeleteObject(hBM)
;   ;;DeleteObject(bits)
;   ;;avg := GetHashCode(hBM)
;   ;;avg := StrLen(avg)
;   gosub CleanUp
  
;   return avg
;}

;CaptureCursor(hDC, nL, nT) {
;   VarSetCapacity(mi, 20, 0)
;   mi := Chr(20)
;   DllCall("GetCursorInfo", "Uint", &mi)
;   bShow := NumGet(mi, 4)
;   hCursor := NumGet(mi, 8)
;   xCursor := NumGet(mi,12)
;   yCursor := NumGet(mi,16)
;   VarSetCapacity(ni, 20, 0)
;   DllCall("GetIconInfo", "Uint", hCursor, "Uint", &ni)
;   xHotspot := NumGet(ni, 4)
;   yHotspot := NumGet(ni, 8)
;   hBMMask := NumGet(ni,12)
;   hBMColor := NumGet(ni,16)
;   If bShow
;      DllCall("DrawIcon", "Uint", hDC, "int", xCursor - xHotspot - nL, "int", yCursor - yHotspot - nT, "Uint", hCursor)
;   If hBMMask
;      DllCall("DeleteObject", "Uint", hBMMask)
;   If hBMColor
;      DllCall("DeleteObject", "Uint", hBMColor)
;}

;Zoomer(hBM, nW, nH, znW, znH) {
;   mDC1 := DllCall("CreateCompatibleDC", "Uint", 0)
;   mDC2 := DllCall("CreateCompatibleDC", "Uint", 0)
;   zhBM := CreateDIBSection(mDC2, znW, znH)
;   oBM1 := DllCall("SelectObject", "Uint", mDC1, "Uint", hBM)
;   oBM2 := DllCall("SelectObject", "Uint", mDC2, "Uint", zhBM)
;   DllCall("SetStretchBltMode", "Uint", mDC2, "int", 4)
;   DllCall("StretchBlt", "Uint", mDC2, "int", 0, "int", 0, "int", znW, "int", znH, "Uint", mDC1, "int", 0, "int", 0, "int", nW, "int", nH, "Uint", 0x00CC0020)
;   DllCall("SelectObject", "Uint", mDC1, "Uint", oBM1)
;   DllCall("SelectObject", "Uint", mDC2, "Uint", oBM2)
;   DllCall("DeleteDC", "Uint", mDC1)
;   DllCall("DeleteDC", "Uint", mDC2)
;   DllCall("DeleteObject", "Uint", hBM)
;   Return zhBM
;}

Convert(sFileFr = "", sFileTo = "", nQuality = "") {
   If sFileTo =
      exit
   SplitPath, sFileTo, , sDirTo, sExtTo, sNameTo
   ;If Not hGdiPlus := DllCall("LoadLibrary", "str", "gdiplus.dll")
   ;MsgBox % sFileFr ", " sDirTo ", " sNameTo
   return sFileFr+0 ? SaveHBITMAPToFile(sFileFr, sDirTo . "\" . sNameTo . ".bmp") : ""
   ;MsgBox, % "got r of " r

   VarSetCapacity(si, 16, 0), si := Chr(1)
   DllCall("gdiplus\GdiplusStartup", "UintP", pToken, "Uint", &si, "Uint", 0)
   If !sFileFr
   {
      DllCall("OpenClipboard", "Uint", 0)
      If DllCall("IsClipboardFormatAvailable", "Uint", 2) && (hBM:=DllCall("GetClipboardData", "Uint", 2))
      DllCall("gdiplus\GdipCreateBitmapFromHBITMAP", "Uint", hBM, "Uint", 0, "UintP", pImage)
      DllCall("CloseClipboard")
   }
   Else If sFileFr Is Integer
   DllCall("gdiplus\GdipCreateBitmapFromHBITMAP", "Uint", sFileFr, "Uint", 0, "UintP", pImage)
   Else DllCall("gdiplus\GdipLoadImageFromFile", "Uint", Unicode4Ansi(wFileFr,sFileFr), "UintP", pImage)
   DllCall("gdiplus\GdipGetImageEncodersSize", "UintP", nCount, "UintP", nSize)
   VarSetCapacity(ci,nSize,0)
   DllCall("gdiplus\GdipGetImageEncoders", "Uint", nCount, "Uint", nSize, "Uint", &ci)
   Loop, % nCount                                                                         ;%
   If InStr(Ansi4Unicode(NumGet(ci,76*(A_Index-1)+44)), "." . sExtTo)
   {
      pCodec := &ci+76*(A_Index-1)
      Break
   }
   If InStr(".JPG.JPEG.JPE.JFIF", "." . sExtTo) && nQuality<>"" && pImage && pCodec
   {
      DllCall("gdiplus\GdipGetEncoderParameterListSize", "Uint", pImage, "Uint", pCodec, "UintP", nSize)
      VarSetCapacity(pi,nSize,0)
      DllCall("gdiplus\GdipGetEncoderParameterList", "Uint", pImage, "Uint", pCodec, "Uint", nSize, "Uint", &pi)
      Loop, % NumGet(pi)                                                                     ;%
      If NumGet(pi,28*(A_Index-1)+20)=1 && NumGet(pi,28*(A_Index-1)+24)=6
      {
         pParam := &pi+28*(A_Index-1)
         NumPut(nQuality,NumGet(NumPut(4,NumPut(1,pParam+0)+20)))
         Break
      }
   }
   If pImage
      pCodec ? DllCall("gdiplus\GdipSaveImageToFile", "Uint", pImage, "Uint", Unicode4Ansi(wFileTo,sFileTo), "Uint", pCodec, "Uint", pParam) :    DllCall("gdiplus\GdipCreateHBITMAPFromBitmap", "Uint", pImage, "UintP", hBitmap, "Uint", 0) . SetClipboardData(hBitmap), DllCall("gdiplus\GdipDisposeImage", "Uint", pImage)
   DllCall("gdiplus\GdiplusShutdown" , "Uint", pToken)
   DllCall("FreeLibrary", "Uint", hGdiPlus)
}

CreateDIBSection(hDC, nW, nH, bpp = 24, ByRef pBits = "") {
   NumPut(VarSetCapacity(bi, 40, 0), bi)
   NumPut(nW, bi, 4)
   NumPut(nH, bi, 8)
   NumPut(bpp, NumPut(1, bi, 12, "UShort"), 0, "Ushort")
   NumPut(0, bi,16)
   Return DllCall("gdi32\CreateDIBSection", "Uint", hDC, "Uint", &bi, "Uint", 0, "UintP", pBits, "Uint", 0, "Uint", 0)
}

SaveHBITMAPToFile(hBitmap, sFile) {
   ;MsgBox, % "app " sFile 
   DllCall("GetObject", "Uint", hBitmap, "int", VarSetCapacity(oi,84,0), "Uint", &oi)
   hFile:= DllCall("CreateFile", "Uint", &sFile, "Uint", 0x40000000, "Uint", 0, "Uint", 0, "Uint", 2, "Uint", 0, "Uint", 0)
   DllCall("WriteFile", "Uint", hFile, "int64P", 0x4D42|14+40+NumGet(oi,44)<<16, "Uint", 6, "UintP", 0, "Uint", 0)
   DllCall("WriteFile", "Uint", hFile, "int64P", 54<<32, "Uint", 8, "UintP", 0, "Uint", 0)
   DllCall("WriteFile", "Uint", hFile, "Uint", &oi+24, "Uint", 40, "UintP", 0, "Uint", 0)
   DllCall("WriteFile", "Uint", hFile, "Uint", NumGet(oi,20), "Uint", NumGet(oi,44), "UintP", 0, "Uint", 0)
   DllCall("CloseHandle", "Uint", hFile)
   ;MsgBox, % "crapp " sFile 
}

SetClipboardData(hBitmap) {
   DllCall("GetObject", "Uint", hBitmap, "int", VarSetCapacity(oi,84,0), "Uint", &oi)
   hDIB := DllCall("GlobalAlloc", "Uint", 2, "Uint", 40+NumGet(oi,44))
   pDIB := DllCall("GlobalLock", "Uint", hDIB)
   DllCall("RtlMoveMemory", "Uint", pDIB, "Uint", &oi+24, "Uint", 40)
   DllCall("RtlMoveMemory", "Uint", pDIB+40, "Uint", NumGet(oi,20), "Uint", NumGet(oi,44))
   DllCall("GlobalUnlock", "Uint", hDIB)
   DllCall("DeleteObject", "Uint", hBitmap)
   DllCall("OpenClipboard", "Uint", 0)
   DllCall("EmptyClipboard")
   DllCall("SetClipboardData", "Uint", 8, "Uint", hDIB)
   DllCall("CloseClipboard")
}

Unicode4Ansi(ByRef wString, sString) {
   nSize := DllCall("MultiByteToWideChar", "Uint", 0, "Uint", 0, "Uint", &sString, "int", -1, "Uint", 0, "int", 0)
   VarSetCapacity(wString, nSize * 2)
   DllCall("MultiByteToWideChar", "Uint", 0, "Uint", 0, "Uint", &sString, "int", -1, "Uint", &wString, "int", nSize)
   Return &wString
}

Ansi4Unicode(pString) {
   nSize := DllCall("WideCharToMultiByte", "Uint", 0, "Uint", 0, "Uint", pString, "int", -1, "Uint", 0, "int", 0, "Uint", 0, "Uint", 0)
   VarSetCapacity(sString, nSize)
   DllCall("WideCharToMultiByte", "Uint", 0, "Uint", 0, "Uint", pString, "int", -1, "str", sString, "int", nSize, "Uint", 0, "Uint", 0)
   Return sString
}
return

SetSystemCursor(IDC = 0) {
   CursorHandle := DllCall( "LoadCursor", Uint,0, Int,IDC )
   Cursors = 32512,32513,32514,32515,32516,32640,32641,32642,32643,32644,32645,32646,32648,32649,32650,32651
   Loop, Parse, Cursors, `,
   {
      DllCall( "SetSystemCursor", Uint,CursorHandle, Int,A_Loopfield )
   }
}

RestoreCursors() {
   if cursor=1
      gosub, ChangeCursor
}

ChangeCursor:
   result1 := DllCall("LoadCursor", "Uint", NULL, "Int", IDC_CROSS, "Uint")
   result2 := DllCall("SetSystemCursor", "Uint", result1, "Int", IDC_ARROW, "Uint")
   cursor := !cursor
return

Morse(timeout = 200) {
   tout := timeout/1000
   key := RegExReplace(A_ThisHotKey,"[\*\~\$\#\+\!\^]")
   Loop {
      t := A_TickCount
      KeyWait %key%
      Pattern .= A_TickCount-t > timeout
      KeyWait %key%,DT%tout%
      If (ErrorLevel)
         Return Pattern
   }
}