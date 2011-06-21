del Quickfort.exe
"c:\Program Files (x86)\AutoHotkey\Compiler\Ahk2Exe.exe" /in "Quickfort.ahk" /icon "Quickfort.ico"
del release
rmdir /s /q release
mkdir release
mkdir release\config
move Quickfort.exe release
copy Quickfort.ico release
copy config\options.txt release\config

