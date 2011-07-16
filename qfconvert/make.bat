set pythonexe=c:\lang\Python27\python.exe

rmdir /s /q release 2> nul:
mkdir release
mkdir release\config

copy config\*.* release\config

:%pythonexe% -OO setup.py py2exe
cxfreeze -OO qfconvert.py

copy dist\*.* release
rmdir /s /q dist
rmdir /s /q build
del *.pyc
del *.pyo