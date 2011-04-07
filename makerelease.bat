@echo off
:This .bat file will probably only work if you use TCC/LE instead of default Windows cmd prompt.
:Also depends on robocopy.exe being on the PATH.

echo ---------------------------------------------------------------------------------
echo ----- BUILDING QFCONVERT
echo ---------------------------------------------------------------------------------

cd qfconvert
call make.bat

cd ..

echo ---------------------------------------------------------------------------------
echo ----- BUILDING QUICKFORT
echo ---------------------------------------------------------------------------------

cd quickfort
call make.bat

cd ..

echo ---------------------------------------------------------------------------------
echo ----- COPYING TO RELEASE FOLDER
echo ---------------------------------------------------------------------------------

call copyrelease.bat

echo ---------------------------------------------------------------------------------
echo ----- ZIPPING RELEASE
echo ---------------------------------------------------------------------------------

call makezip.bat

pause