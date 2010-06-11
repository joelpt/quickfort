from distutils.core import setup
import py2exe

setup(
        options={"py2exe":{"optimize":2}},
        console=["temp/qfconvert.py"]
)

