rmdir /s /q zip_temp 2> nul:
del release.zip 2> nul:

mkdir zip_temp
move release zip_temp
cd zip_temp
ren release quickfort

zip -9 -r release.zip quickfort\*
move release.zip ..
cd ..
