set qfpath=D:\code\qf\trunk
set pythonexe=c:\lang\Python26_32bit\python.exe

cd %qfpath%\qfconvert
rmdir /s /q release
mkdir release
copy interface.txt release

%pythonexe% -OO setup.py py2exe

copy dist\*.* release
rmdir /s /q dist
rmdir /s /q build
cd release
dir
.\qfconvert.exe  %qfpath%\Blueprints\Tests\dig-5x5.csv -i
.\qfconvert.exe  %qfpath%\Blueprints\Tests\dig-5x5.csv -Cmkey
cd ..

