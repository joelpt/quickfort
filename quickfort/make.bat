del /q Quickfort.exe 2> nul:
"c:\Program Files (x86)\AutoHotkey\Compiler\Ahk2Exe.exe" /in "Quickfort.ahk" /icon "Quickfort.ico"
rmdir /s /q release 2> nul:
del /q release 2> nul:
mkdir release
mkdir release\config
move Quickfort.exe release
copy Quickfort.ico release
copy config\options.txt release\config

