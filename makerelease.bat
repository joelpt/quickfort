@echo off
:This .bat file may only work if you use TCC/LE instead of default Windows cmd prompt.

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

cd ..
ren release quickfort
del release.zip
zip -9 -r release.zip quickfort\*
ren quickfort release
dir
cd trunk

pause