import os
import idna

os.environ['TCL_LIBRARY'] = r'C:\Python3\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Python3\tcl\tk8.6'

import cx_Freeze
import sys

base = None

if sys.platform == 'win32':
    base = "Win32GUI"

executables = [cx_Freeze.Executable("ui/main.pyw", base=base)]

cx_Freeze.setup(
    name="YOnchi",
    options={"build_exe": {"packages": ["tkinter", "idna"]}},
    version="0.1",
    description="Sea of BTC trading application",
    executables=executables
    )
