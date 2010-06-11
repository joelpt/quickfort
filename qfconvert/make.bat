set qfpath=D:\code\quickfort\trunk
set pythonexe=c:\lang\Python26_32bit\python.exe

cd %qfpath%\qfconvert
del Release\*.* /y
copy interface.txt Release

%pythonexe% -OO setup.py py2exe

copy dist\*.* Release
rmdir /s /q dist
rmdir /s /q build
cd Release
dir
.\qfconvert.exe  %qfpath%\Blueprints\Tests\dig-5x5.csv -i
.\qfconvert.exe  %qfpath%\Blueprints\Tests\dig-5x5.csv -Cmkey