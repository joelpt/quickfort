rmdir /s /q /k release 2> nul: || rmdir /s /q release 2> nul:
rmdir /s /q /k qfconvert\release 2> nul: || rmdir /s /q qfconvert\release 2> nul:
rmdir /s /q /k quickfort\release 2> nul: || rmdir /s /q quickfort\release 2> nul:
rmdir /s /q /k zip_temp 2> nul: || rmdir /s /q zip_temp 2> nul:
del qfconvert\release 2> nul:
del quickfort\release 2> nul:
del release.zip
