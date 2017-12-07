import tkinter as tk

MAIN_BG = '#ffffff'


class MyProfileView:
    def __init__(self, base):
        self.base = base
        self.body = tk.Frame(self.base.root, bg=MAIN_BG, width=768, height=680)

        self.base.views_frame['MyProfileView'] = self
        self.body.place(x=0, y=0)
