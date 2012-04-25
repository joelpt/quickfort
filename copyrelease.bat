rmdir /s /q release 2> nul:
mkdir release
mkdir release\src
mkdir release\blueprints
mkdir release\config

:: Copy compiled release stuff
copy qfconvert\release\* release
copy quickfort\release\* release
copy qfconvert\release\config\* release\config
copy quickfort\release\config\* release\config
copy /s blueprints release\blueprints

:: Copy source code
robocopy /s quickfort release\src\quickfort\ Quickfort.ahk Quickfort.ico /xd release
robocopy /s quickfort\lib release\src\quickfort\lib
robocopy /s qfconvert release\src\qfconvert\ *.py /xd release
robocopy /s quickfort\config release\src\quickfort\config
robocopy /s qfconvert\config release\src\qfconvert\config

:: Copy readme
copy README.md release\README.md
copy README.md release\README.txt
