cd ..
ren release quickfort
del release.zip
zip -9 -r release.zip quickfort\*
ren quickfort release
dir
cd trunk
