import os
import shutil
import tkinter as tk
import zipfile

import requests

MAIN_BG = '#ffffff'


root = tk.Tk()
root.title('Update Program')
# root.iconbitmap(default='img/logo.ico')
root.configure(background=MAIN_BG)
root.resizable(width=False, height=False)
root.minsize(width=400, height=200)


def update_app():
    # Download new version
    r = requests.get(
        "http://file-st12.karelia.ru/24gztv/0611730b96a0285a6cadbda55111a5aa/c2d0076f6a7ac2ccbcabc8da80fd1b10/faby%202.8.2.zip?force")
    with open("../new_version.zip", "wb") as code:
        code.write(r.content)

    # Unzip new version
    zip_ref = zipfile.ZipFile('../new_version.zip', 'r')
    zip_ref.extractall('../')
    zip_ref.close()

    # # Copy files from previous version
    # shutil.copy('config.ini', '../new_version/')
    shutil.copy('../new_version/', '/')

    # Rename dirs
    # os.rename(os.getcwd(), "old_YOnchi")
    # os.rename("../new_version", "../YOnchi")

   # shutil.rmtree(os.getcwd())

if __name__ == "__main__":
    update_app()
    root.mainloop()
