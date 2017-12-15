import subprocess

from ui.login_view import LoginView
from ui.task_list_view import TaskListView
from ui.create_job_view import CreateJobView
from ui.edit_task_view import EditTaskView
from ui.task_view import TaskView
import tkinter as tk

MAIN_BG = '#ffffff'


class Base:
    def __init__(self, root):
        self.views_frame = {}
        self.root = root
        self.version_app = '0.2'  # Change App version here!
        # self.api_server = 'http://127.0.0.1:8000'
        self.api_server = 'http://95.46.44.227'

    def change_view(self, to, data=None, back_to=None):
        self.to = to
        for i in self.views_frame:
            self.views_frame[i].body.place_forget()
        self.root.unbind_all("<MouseWheel>")

        # If open Settings screen
        if to == 'EditTaskView':
            return eval(to)(self, data, back_to)

        # If view not created yet
        if to not in self.views_frame:
            if '_' in to:
                return eval(to.split('_')[0])(self, data, back_to)
            eval(to)(self)
        else:
            self.views_frame[to].body.place(x=0, y=0, width=768, height=680)
            # Show scroll if need
            if to.split('_')[0] == 'TaskView' or to == "TaskListView":
                self.views_frame[to].canv.bind_all("<MouseWheel>", self.on_mousewheel)
                if self.views_frame[to].y_poss < self.views_frame[to].canvas_frame['height']:
                    self.views_frame[to].canv.unbind_all("<MouseWheel>")

    def on_mousewheel(self, event):
        self.views_frame[self.to].canv.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def start_loading(self, x=300, y=300):
        self.loading = tk.Label(self.root, text='Loading Please wait...', fg='#0f743a', font=('Helvetica', -14, 'bold'), bg=MAIN_BG)
        self.loading.place(x=x, y=y)
        self.root.update_idletasks()

    def stop_loading(self):
        self.loading.place_forget()

    def update_app(self):

        subprocess.Popen("update.exe")
        self.root.destroy()

