set pythonexe=c:\lang\Python26_32bit\python.exe

rmdir /s /q release 2> nul:
mkdir release
mkdir release\config

copy config\*.* release\config

%pythonexe% -OO setup.py py2exe

copy dist\*.* release
rmdir /s /q dist
rmdir /s /q build
