set pythonexe=c:\lang\Python27\python.exe

rmdir /s /q /k release 2> nul: || rmdir /s /q release 2> nul:
mkdir release
mkdir release\config

copy config\*.* release\config

:%pythonexe% -OO setup.py py2exe
call cxfreeze -OO -s qfconvert.py

copy dist\*.* release
rmdir /s /q /k dist || rmdir /s /q dist
del *.pyc 2> nul:
del *.pyo 2> nul: