; Returns a CRC32 of the bytes in Buffer. Uses machine code for speed.
CRC32(ByRef Buffer, Bytes=0, Start=-1) {
   Static crcfn
   If crcfn =
    MCode(crcfn,"558bec8b450c85c07e388b5508535689450c8b4510578a0a6a08425e8bf80fb6d9c"
    . "1ef1833fb03c0f7c780ffffff740333451402c94e75e4ff4d0c75d95f5e5b5dc38b45105dc3")
   If Bytes <= 0
      Bytes := StrLen(Buffer)*2
   Return DllCall(&crcfn, uint,&Buffer, uint,Bytes, int,Start, uint,0x04C11DB7, "cdecl uint")
}

; allocate memory and write Machine Code there
MCode(ByRef code, hex) { 
   VarSetCapacity(code,StrLen(hex)//2)
   Loop % StrLen(hex)//2
      NumPut("0x" . SubStr(hex,2*A_Index-1,2), code, A_Index-1, "Char")
}

; Swap a and b (passed by reference).
Swap(byRef a, byRef b)
{
    s := a
    a := b
    b := s
}

; Order a and b in ascending order (passed by reference).
;   Order(1, 2) => 1, 2
;   Order(2, 1) => 1, 2
Order(byRef a, byRef b)
{
    if (a > b)
        Swap(a, b)
}

; Return lesser of two values
Min( value1, value2 ) {
   If ( value1 < value2 )
      return value1
   Else
      return value2
}
