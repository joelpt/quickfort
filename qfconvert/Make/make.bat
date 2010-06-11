set qfpath=D:\code\quickfort\trunk
set pythonexe=c:\lang\Python26_32bit\python.exe

cd %qfpath%\qfconvert
del Release\*.* /y
copy interface.txt Release
cd Make
mkdir temp
cd temp
del *.* /y
del dist\*.* /y
copy ..\setup.py .
copy ..\..\qfconvert.py .
copy ..\..\Packages\*.py .
%pythonexe% -OO setup.py py2exe
copy dist\*.* ..\..\Release
cd ..\..\Release
dir
.\qfconvert.exe  %qfpath%\Blueprints\Tests\dig-5x5.csv -i
.\qfconvert.exe  %qfpath%\Blueprints\Tests\dig-5x5.csv -Cmkey