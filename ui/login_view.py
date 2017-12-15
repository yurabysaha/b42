import configparser
import tkinter as tk
from tkinter import messagebox
import requests
from requests import ConnectionError
import webbrowser

MAIN_BG = '#ffffff'


class LoginView:
    def __init__(self, base):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.base = base
        self.body = tk.Frame(self.base.root, bg=MAIN_BG, width=768, height=680)

        self.base.views_frame['LoginView'] = self
        self.body.place(x=0, y=0)

        self.login_label = tk.Label(self.body, bg=MAIN_BG, text='LOG IN', fg='#029f5b', font=('Helvetica', -18, 'bold'))
        self.login_label.place(x=354, y=129)

        self.email_label = tk.Label(self.body, bg=MAIN_BG, text='EMAIL', fg='#12502d', font=('Helvetica', -12, 'bold'))
        self.email_label.place(x=208, y=229)

        self.pass_label = tk.Label(self.body, bg=MAIN_BG, text='PASSWORD', fg='#12502d', font=('Helvetica', -12, 'bold'))
        self.pass_label.place(x=208, y=327)

        self.email_input = tk.Text(self.body, bg='#e6f1ea', borderwidth=1, padx=5, pady=10, highlightbackground='#dddee1', width=44, height=1, fg='#18281f', font=('Helvetica', -15))
        if self.config.get('REMEMBER', 'login') and self.config.getboolean('REMEMBER', 'remember'):
            self.email_input.insert('end', self.config.get('REMEMBER', 'login'))
        self.email_input.bind("<Tab>", self.focus_next_input)
        self.email_input.place(x=207, y=251)

        self.pass_input = tk.Text(self.body, bg='#e6f1ea', borderwidth=1, padx=5, pady=10, highlightbackground='#dddee1', width=44, height=1, fg='#18281f', font=('Helvetica', -15))

        if self.config.get('REMEMBER', 'password') and self.config.getboolean('REMEMBER', 'remember'):
            self.pass_input.insert('end', self.config.get('REMEMBER', 'password'))
        self.pass_input.bind("<Tab>", self.focus_next_input)
        self.pass_input.bind("<Return>", self.login)
        self.pass_input.place(x=207, y=350)

        if self.config.getboolean('REMEMBER', 'remember'):
            self.remember_me_check = tk.Label(self.body, bg=MAIN_BG, text='[x]', fg='#0f743a', font=('Helvetica', -14, 'bold'))
        else:
            self.remember_me_check = tk.Label(self.body, bg=MAIN_BG, text='[ ]', fg='#0f743a',
                                        font=('Helvetica', -14, 'bold'))
        self.remember_me_check.bind("<Button-1>", self.remember_me)
        self.remember_me_check.place(x=210, y=392)

        self.remember_me_label = tk.Label(self.body, bg=MAIN_BG, text='Remember me', fg='#0f743a',
                                          font=('Helvetica', -12, 'bold'))
        self.remember_me_label.place(x=230, y=394)

        self.forgot_btn = tk.Label(self.body, bg=MAIN_BG, text='FORGOT PASSWORD?', fg='#0f743a', font=('Helvetica', -12, 'bold'))
        self.forgot_btn.bind("<Button-1>", self.forgot_password)
        self.forgot_btn.bind("<Enter>", lambda event, h=self.forgot_btn: h.configure(bg=MAIN_BG, fg='#10b858'))
        self.forgot_btn.bind("<Leave>", lambda event, h=self.forgot_btn: h.configure(bg=MAIN_BG, fg='#0f743a'))
        self.forgot_btn.place(x=428, y=421)

        self.reqister_btn = tk.Label(self.body, bg=MAIN_BG, text='NOT REGISTER YET?', fg='#0f743a',
                                   font=('Helvetica', -12, 'bold'))
        self.reqister_btn.bind("<Button-1>", self.register)
        self.reqister_btn.bind("<Enter>", lambda event, h=self.reqister_btn: h.configure(bg=MAIN_BG, fg='#10b858'))
        self.reqister_btn.bind("<Leave>", lambda event, h=self.reqister_btn: h.configure(bg=MAIN_BG, fg='#0f743a'))
        self.reqister_btn.place(x=210, y=421)

        self.login_btn = tk.Label(self.body, text='LOGIN', bg="#10b858", padx=160, pady=20, fg='white', font=('Helvetica', -14, 'bold'))
        self.login_btn.bind("<Button-1>", self.login)
        self.login_btn.bind("<Enter>", lambda event, h=self.login_btn: h.configure(bg="#0f743a"))
        self.login_btn.bind("<Leave>", lambda event, h=self.login_btn: h.configure(bg="#10b858"))
        self.login_btn.place(x=205, y=494)

    def login(self, event):
        self.base.start_loading()
        data = {
                'username': str(self.email_input.get(1.0, 'end')).rstrip(),
                'password': str(self.pass_input.get(1.0, 'end')).rstrip(),
                'version': self.base.version_app
                }
        self.base.user = requests.Session()
        try:
            r = self.base.user.post(self.base.api_server + "/api-token-auth/", data=data)

            if r.status_code == 200:
                self.base.current_user = r.json()

                # Save remember if set
                if self.remember_me_check.cget('text') == '[x]':
                    self.config['REMEMBER']['login'] = str(self.email_input.get(1.0, 'end')).rstrip()
                    self.config['REMEMBER']['password'] = str(self.pass_input.get(1.0, 'end')).rstrip()
                    self.config['REMEMBER']['remember'] = 'True'
                else:
                    self.config['REMEMBER']['login'] = ''
                    self.config['REMEMBER']['password'] = ''
                    self.config['REMEMBER']['remember'] = 'False'
                with open('config.ini', 'w') as configfile:
                    self.config.write(configfile)

                # Clear field and change view
                self.email_input.delete(1.0, 'end')
                self.pass_input.delete(1.0, 'end')

                self.base.user.headers['Authorization'] = 'Token ' + self.base.current_user['token']
                self.base.stop_loading()
                self.base.change_view('TaskListView')
            else:
                self.base.stop_loading()
                self.pass_input.delete(1.0, 'end')
                messagebox.showerror("Error", "Incorrect email or password")
        except ConnectionError:
            self.base.stop_loading()
            self.pass_input.delete(1.0, 'end')
            messagebox.showerror("Error", "Server or internet connection problem")

    def register(self, event):
        webbrowser.open('http://yonchi.net.ua/login')

    def forgot_password(self, event):
        webbrowser.open('http://yonchi.net.ua/login')

    def focus_next_input(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def remember_me(self, event):
        if self.remember_me_check.cget('text') == '[ ]':
            self.remember_me_check.config(text='[x]')
        else:
            self.remember_me_check.config(text='[ ]')
