cdd D:\code\quickfort\trunk\qfconvert\Make
rmdir /s /q temp
mkdir temp
copy setup.py temp
copy ..\qfconvert.py temp
copy ..\Packages\*.py temp
python -OO temp\setup.py py2exe
rmdir /s /q temp
