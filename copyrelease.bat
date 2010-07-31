rmdir /s /q release
mkdir release
mkdir release\src
mkdir release\blueprints

copy qfconvert\release\* release
copy quickfort\release\* release
copy /s blueprints release\blueprints

robocopy /s quickfort release\src\quickfort\ Quickfort.ahk options.txt aliases.txt readme.txt Quickfort.ico lib /xd release
robocopy /s qfconvert release\src\qfconvert\ *.py interface.txt /xd release

:cd release
