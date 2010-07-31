#SingleInstance force
SetKeyDelay 70

; Increase this value if things don't work quite right when digging/building (larger numbers slow down building)
DelayMultiplier := 15

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

; Designation / Construction / Build mode
$!D:: mode := 0
$!C:: mode := 1
$!E:: mode := 2

; Start position switch
$!Q:: startpos := 0
$!W:: startpos := 1
$!A:: startpos := 2
$!S:: startpos := 3

; Helper to mass-demolish misplaced constuctions
$!X:: Send {x 30}

; Reload the script itself
$!R:: Reload

; The actual builder
$!B::
FileDelete, debug.txt
if(mode = 0)
{
    Perform("d","Starting Designation Mode...")
    fname_m := fname
    SetKeyDelay DelayMultiplier*3
}
else if(mode = 1)
{
    Perform("","Starting Construction Mode...")
    fname_m := "C" . fname
    SetKeyDelay DelayMultiplier*5
}
else if(mode = 2)
{
    Perform("","Starting Building Placement Mode...")
    fname_m := "B" . fname
    SetKeyDelay DelayMultiplier*5
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

storedmovesafter := ""
storedmovesbefore := "{Space}"

Loop, Read, %fname_m%
{
    Perform("","`nRow-")
    x := 0
    Loop, parse, A_LoopReadLine, `,
    {
        StringLower, reqdes, A_LoopField
        action := reqdes
        if (reqdes = "#")
        {   
            mod := mod(x, 10)
            tens := round((x - mod) / 10)
            if (mode = 2)
            {
                storedmovesafter = %storedmovesafter%+{Left %tens%}{Left %mod%}
            }
            else
            {
                if(!DebugOn)
                {
                Send +{Left %tens%}{Left %mod%}
                }
            }
            Perform("","#")
            break

        }
        else if(action == "" || action == " ")
        {
            if(mode = 2)
            {
              storedmovesafter = %storedmovesafter%{Right}
            }
            else
            {
                Perform("{Right}","S")
            }
            x := x + 1
            continue
        }
        else if(mode = 1)
        {
            Perform("{Space}","")
            Perform(action,"")
            Perform("{Enter 2}","C")
            Perform("w{Right}","")
        }
        else 
        {

      	    if(mode = 2)
            {
                Perform(storedmovesbefore, storedmovesbefore)
                Perform(action, action)  
                
                ; condense {Right}x10 to +{Right}
                StringReplace, storedmovesafter, storedmovesafter,{Right}{Right}{Right}{Right}{Right}{Right}{Right}{Right}{Right}{Right},+{Right}, 1
                
                Perform(storedmovesafter, storedmovesafter)
                Perform("{Enter 2}","{Enter 2}")
                
                ; extra long pause when building a [d]oor, since the game pauses a moment here recalculating the pathfinding map
                if (action == "d")
                {
                    Sleep, DelayMultiplier*35
                }
                storedmovesafter := "{Right}"
                storedmovesbefore := ""
            }            
            if(mode = 0)
            {
                ;if(currdes != action)
                ;{
                    Perform(action, "")
                ;    currdes := action
                ;}
                Perform("{Enter 2}","D")
                Perform("{Right}","")
            }

        }
       x := x + 1
    }
    if (mode = 2) {
      storedmovesafter = %storedmovesafter%{Down}
    }
    else {
      Perform("{Down}","")
    }
    
}
return

Perform(keys, debugstr)
{
    global DebugOn
    FileAppend, %debugstr%, debug.txt 
    if (DebugOn = 0)
      Send %keys%
}