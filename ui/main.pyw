#!/usr/bin/env python

import tkinter as tk
import sys

from ui.base import Base
from ui.login_view import LoginView

MAIN_BG = '#ffffff'

# Need for disable console when close windows on Windows OS
sys.stderr = open('error.log', 'w')
sys.stdout = open('output.log', 'w')

root = tk.Tk()
root.title('YOnchi v 0.2')
# root.iconbitmap(default='img/logo.ico')
root.configure(background=MAIN_BG)
root.resizable(width=False, height=False)
root.minsize(width=768, height=680)

base = Base(root)

if __name__ == "__main__":
    LoginView(base)
    root.mainloop()
