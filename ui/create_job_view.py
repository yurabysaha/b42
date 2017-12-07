import tkinter as tk
import json
from tkinter import messagebox
from requests import ConnectionError

MAIN_BG = '#ffffff'


class CreateJobView:
    def __init__(self, base):
        self.base = base
        self.body = tk.Frame(self.base.root, bg=MAIN_BG)

        self.base.views_frame['CreateJobView'] = self
        self.body.place(x=0, y=0, width=768, height=680)

        self.name_label = tk.Label(self.body, bg=MAIN_BG, fg='#12502d', text='CREATE NEW TASK', font=('Helvetica', -16, "bold"))
        self.name_label.place(x=70, y=18)

        self.back_label = tk.Label(self.body, bg=MAIN_BG, fg='#12502d', text='< back')
        self.back_label.bind("<Button-1>", self.back)
        self.back_label.place(x=14, y=18)

        self.name_label = tk.Label(self.body, bg=MAIN_BG, fg='#12502d', text='TASK NAME', font=('Helvetica', -12, "bold"))
        self.name_label.place(x=15, y=78)
        self.name_input = tk.Text(self.body, bg='#e6f1ea', borderwidth=1, padx=5, pady=10, highlightbackground='#dddee1', width=80, height=1, font=('Helvetica', -16))
        self.name_input.bind("<Tab>", self.focus_next_input)
        self.name_input.bind("<Return>", self.validate_enter)
        self.name_input.place(x=15, y=101)

        self.url_label = tk.Label(self.body, bg=MAIN_BG, fg='#12502d', text='LINKEDIN URL', font=('Helvetica', -12, "bold"))
        self.url_label.place(x=15, y=157)
        self.url_input = tk.Text(self.body, bg='#e6f1ea', borderwidth=1, padx=5, pady=10, highlightbackground='#dddee1', width=80, height=1, font=('Helvetica', -16))
        self.url_input.bind("<Tab>", self.focus_next_input)
        self.url_input.bind("<Return>", self.validate_enter)
        self.url_input.place(x=15, y=180)

        # Hint for Linkedin url
        url_hint = tk.Label(self.body, bg='#e0ebeb', padx=2, text='?', fg='#12502d', font=('Helvetica', -9))
        url_hint.bind("<Enter>", self.url_hint_show)
        url_hint.bind("<Leave>", self.url_hint_hide)
        url_hint.place(x=105, y=158)

        self.email_label = tk.Label(self.body, bg=MAIN_BG, fg='#12502d', text='LINKEDIN EMAIL', font=('Helvetica', -12, "bold"))
        self.email_label.place(x=15, y=236)
        self.email_input = tk.Text(self.body, bg='#e6f1ea', borderwidth=1, padx=5, pady=10, highlightbackground='#dddee1',
                                 width=80, height=1, font=('Helvetica', -16))
        self.email_input.bind("<Tab>", self.focus_next_input)
        self.email_input.bind("<Return>", self.validate_enter)
        self.email_input.place(x=15, y=259)

        self.password_label = tk.Label(self.body, bg=MAIN_BG, fg='#12502d', text='LINKEDIN PASSWORD', font=('Helvetica', -12, "bold"))
        self.password_label.place(x=15, y=315)
        self.password_input = tk.Text(self.body, bg='#e6f1ea', borderwidth=1, padx=5, pady=10,
                                   highlightbackground='#dddee1',
                                   width=80, height=1, font=('Helvetica', -16))
        self.password_input.bind("<Tab>", self.focus_next_input)
        self.password_input.bind("<Return>", self.validate_enter)
        self.password_input.place(x=15, y=338)

        self.create_task_btn = tk.Label(self.body, text="CREATE NEW TASK", bg="#10b858", padx=40, pady=12, fg='white',
                                        font=('Helvetica', -14, 'bold'))
        self.create_task_btn.bind("<Button-1>", self.create_task)
        self.create_task_btn.bind("<Enter>", lambda event, h=self.create_task_btn: h.configure(bg="#0f743a"))
        self.create_task_btn.bind("<Leave>", lambda event, h=self.create_task_btn: h.configure(bg="#10b858"))
        self.create_task_btn.place(x=530, y=615)

    def validate_enter(self, event):
        if event.keysym == "Return":
            return 'break'

    def create_task(self, event):
        if not self.email_input.get(1.0, 'end').rstrip():
            messagebox.showinfo("Info", "Fill all fields before")
            return
        if 'https://www.linkedin.com/search/' not in self.url_input.get(1.0, 'end').rstrip():
            messagebox.showinfo("Incorrect url", "Please check your linkedin search url because it not correct now")
            return
        headers = {'content-type': 'application/json'}

        data = {
                "task_name": str(self.name_input.get(1.0, 'end')).rstrip(),
                "linkedin_url": str(self.url_input.get(1.0, 'end')).rstrip(),
                "linkedin_email": str(self.email_input.get(1.0, 'end')).rstrip(),
                "linkedin_password": str(self.password_input.get(1.0, 'end')).rstrip()
                }
        try:
            resp = self.base.user.post(self.base.api_server + "/api/tasks/", data=json.dumps(data), headers=headers)
            if resp.status_code == 201:
                data = resp.json()
                self.clear_all_fields()
                self.base.views_frame['TaskListView'].load_job_table()
                self.base.change_view('TaskView_' + str(data['id']), data=data)
        except ConnectionError:
            messagebox.showerror("Error", "Server or internet connection problem")

    def back(self, event):
        self.base.change_view('TaskListView')

    def clear_all_fields(self):
        self.name_input.delete(1.0, 'end')
        self.url_input.delete(1.0, 'end')
        self.email_input.delete(1.0, 'end')
        self.password_input.delete(1.0, 'end')

    def focus_next_input(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def url_hint_show(self, event):
        self.url_hint_frame = tk.Frame(self.body, width=555, height=30, bg='#1a1a1a')
        self.url_hint_frame.place(x=15, y=180)
        hint_text = tk.Label(self.url_hint_frame, fg='white', bg='#1a1a1a', justify='left',  text="You should copy url from linkedin after you select all needs criteria on search page for your candidates")
        hint_text.place(x=5, y=5)

    def url_hint_hide(self, event):
        self.url_hint_frame.place_forget()
