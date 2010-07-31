rmdir /s /q release
mkdir release
mkdir release\src
mkdir release\blueprints

:: Copy compiled release stuff
copy qfconvert\release\* release
copy quickfort\release\* release
copy /s blueprints release\blueprints

:: Copy source code
robocopy /s quickfort release\src\quickfort\ Quickfort.ahk options.txt aliases.txt readme.txt Quickfort.ico /xd release
robocopy /s quickfort\lib release\src\quickfort\lib
robocopy /s qfconvert release\src\qfconvert\ *.py interface.txt /xd release

:: Move finalized release folder up one folder (keeping it out of trunk to avoid HG messiness)
rmdir /s /q ..\release
move release ..

:cd release
