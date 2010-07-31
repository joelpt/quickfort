#SingleInstance force
SetKeyDelay 70

DebugOn := 0
mode := 0

fname := "roomdef1.csv"

; Filename selector
$!1:: fname:= "roomdef1.csv"
$!2:: fname:= "roomdef2.csv"
$!3:: fname:= "roomdef3.csv"
$!4:: fname:= "roomdef4.csv"
$!5:: fname:= "roomdef5.csv"
$!6:: fname:= "roomdef6.csv"
$!7:: fname:= "roomdef7.csv"
$!8:: fname:= "roomdef8.csv"
$!9:: fname:= "roomdef9.csv"

; Designation / Construction mode
$!D:: mode := 0
$!C:: mode := 1

; Start position switch
$!Q:: startpos := 0
$!W:: startpos := 1
$!A:: startpos := 2
$!S:: startpos := 3

; Helper to mass-demolish misplaced constuctions
$!X:: Send {x 30}

; The actual builder
$!B::
FileDelete, debug.txt
if(mode = 0)
{
    Perform("d","Starting Designation Mode...")
    fname_m := fname
    SetKeyDelay 45
}
else
{
    Perform("","Starting Construction Mode...")
    fname_m := "C" . fname
    SetKeyDelay 70
}
;Initial correction for different start positions
FileReadLine, firstline, %fname_m%, 1
StringSplit, firstarr, firstline, `,
numcols := firstarr0 - 2
numrows := 0
Loop, Read, %fname_m%
{
    StringMid, firstchar, A_LoopReadLine, 2, 1
    if(firstchar != "#")
        numrows += 1
}
numrows := numrows - 1

if(startpos == 1 or startpos == 3)
    Send {Left %numcols%}
if(startpos == 2 or startpos == 3)
    Send {Up %numrows%}

Loop, Read, %fname_m%
{
    Perform("","`nRow-")
    x := 0
    Loop, parse, A_LoopReadLine, `,
    {
        StringLower, reqdes, A_LoopField
        action := reqdes
        if reqdes = "#"
        {
            mod := mod(x, 10)
            tens := (x - mod) / 10
            if(!DebugOn)
                Send +{Left %tens%}{Left %mod%}
            Perform("","#")
            break

        }
        else if(action == "")
        {
            x := x + 1
            Perform("{Right}","S")
            continue
        }
        else if(action == "D")
        {
            if(mode = 1)
        {
            Perform("{Space}","")
            Perform(action,"")
            Perform("{Enter 2}","C")
            Perform("w{Right}","")
        }
        else 
        {
            Perform(action, "")

        }
       x := x + 1
    }
    Perform("{Down}","")
    
}
return

Perform(keys, debugstr)
{
    global DebugOn
    if DebugOn
    {
        FileAppend, %debugstr%, debug.txt 
    }
    else
        Send %keys%
}