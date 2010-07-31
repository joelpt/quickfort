"c:\Program Files (x86)\AutoHotkey\Compiler\Ahk2Exe.exe" /in "Quickfort.ahk" /icon "Quickfort.ico"
rmdir /s /q release
mkdir release
copy Quickfort.exe release
copy Quickfort.ico release
copy options.txt release
:copy aliases.txt release
copy readme.txt release

