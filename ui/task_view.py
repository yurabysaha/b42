import json
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox
import time
import datetime

from logic.accept import Accept
from logic.connect import Connect
from logic.fast_connect import FastConnect
from logic.forward_message import ForwardMessage
from logic.message import Message

MAIN_BG = '#ffffff'
enter_time_for_search = None


class TaskView:
    def __init__(self, base, data, back_to=None):
        self.base = base
        self.data = data
        self.work = 'WORK'
        self.body = tk.Frame(self.base.root, bg=MAIN_BG, width=768, height=680)
        self.checkbox_items = {}
        self.view_name = 'TaskView_' + str(data['id'])

        self.base.views_frame[self.view_name] = self
        self.body.place(x=0, y=0)

        self.back_label = tk.Label(self.body, bg=MAIN_BG, fg='#12502d', text='< back')
        self.back_label.bind("<Button-1>", self.back)
        self.back_label.place(x=14, y=19)

        self.title_label = tk.Label(self.body, bg=MAIN_BG, text=self.data['task_name'], font=('Helvetica', -16, "bold"))
        self.title_label.place(x=70, y=18)

        self.process_label = tk.Label(self.body, text='', font=('Helvetica', -14), fg='#171c34', bg=MAIN_BG)
        self.process_label.place(x=self.title_label.winfo_reqwidth() + 120, y=20)

        self.settings_btn = tk.Label(self.body, bg=MAIN_BG, text='S', fg='#545956', font=('Helvetica', -17, 'bold'))
        self.settings_btn.bind("<Button-1>", lambda event: self.open_settings(data=self.data))
        self.settings_btn.bind("<Enter>", lambda event, h=self.settings_btn: h.configure(font=('Helvetica', -20, 'bold')))
        self.settings_btn.bind("<Leave>", lambda event, h=self.settings_btn: h.configure(font=('Helvetica', -17, 'bold')))
        self.settings_btn.place(x=self.title_label.winfo_reqwidth() + 80, y=18)

        self.process_label = tk.Label(self.body, text='', font=('Helvetica', -14), fg='#171c34', bg=MAIN_BG)
        self.process_label.place(x=self.title_label.winfo_reqwidth() + 120, y=20)

        # --------------------------- MENU BLOCK ----------------------------------------

        self.menu_frame = tk.Frame(self.body, bg='#f9fff9', width=768, height=40)
        self.menu_frame.place(x=0, y=60)

        self.menu_connect = tk.Label(self.menu_frame, name='connect', bg='#10b858', text="CONNECT", fg='white', padx=15, pady=8,
                                     font=('Helvetica', -13, 'bold'))
        self.menu_connect.bind("<Button-1>", self.change_tab)
        self.menu_connect.place(x=160, y=0)

        if self.data['task_type'] != 'fast':
            self.menu_accept = tk.Label(self.menu_frame, name='accept', bg='#f9fff9', text="ACCEPT", fg='#0f743a', padx=15, pady=8,
                                        font=('Helvetica', -13, 'bold'))
            self.menu_accept.bind("<Button-1>", self.change_tab)
            self.menu_accept.place(x=260, y=0)

            self.menu_message = tk.Label(self.menu_frame,name='message', bg='#f9fff9', text="MESSAGE", fg='#0f743a', padx=15, pady=8,
                                         font=('Helvetica', -13, 'bold'))
            self.menu_message.bind("<Button-1>", self.change_tab)
            self.menu_message.place(x=360, y=0)

            self.menu_forward_mess = tk.Label(self.menu_frame, name='forward', bg='#f9fff9', text="FORWARD", fg='#0f743a', padx=15, pady=8,
                                              font=('Helvetica', -13, 'bold'))
            self.menu_forward_mess.bind("<Button-1>", self.change_tab)
            self.menu_forward_mess.place(x=460, y=0)

        self.start_task_btn = tk.Label(self.body, bg='#10b858', text="START TASK", fg='white', padx=20, pady=10,
                                       font=('Helvetica', -14, 'bold'))
        self.start_task_btn.bind("<Button-1>", self.start_task)
        self.start_task_btn.place(x=20, y=120)

        # PAUSE BUTTON
        self.pause_task_btn = tk.Label(self.body, bg='#10b858', text="PAUSE TASK", fg='white', padx=20, pady=10,
                                       font=('Helvetica', -14, 'bold'))
        self.pause_task_btn.bind("<Button-1>", self.pause_task)

        # CONTINUE BUTTON
        self.continue_task_btn = tk.Label(self.body, bg='#10b858', text="CONTINUE TASK", fg='white', padx=20, pady=10,
                                       font=('Helvetica', -14, 'bold'))
        self.continue_task_btn.bind("<Button-1>", self.unpause_task)

        # STOP BUTTON
        self.stop_task_btn = tk.Label(self.body, bg='#10b858', text="STOP TASK", fg='white', padx=20, pady=10,
                                       font=('Helvetica', -14, 'bold'))
        self.stop_task_btn.bind("<Button-1>", self.stop_task)

        # Notification area
        self.notification_area = tk.Label(self.body, text='', fg='#12502d',
                                    font=('Helvetica', -15), bg='#f9fff9')
        self.notification_area.place(x=300, y=130)

        # Option Button
        self.option_btn = tk.Label(self.body, bg='#10b858', text="OPTIONS +", fg='white', padx=20, pady=10,
                                   font=('Helvetica', -14, 'bold'))
        self.option_btn.place(x=620, y=120)

        self.select_all_checkbox = tk.Label(self.body, text='[ ]', fg='#12502d', bg=MAIN_BG,
                                            font=('Helvetica', -17, 'bold'))
        self.select_all_checkbox.bind("<Button-1>", self._on_select_all_checkbox)
        self.select_all_checkbox.selected = False
        self.select_all_checkbox.place(x=35, y=200)

        select_label = tk.Label(self.body, bg=MAIN_BG, text='Select all', fg='#12502d', font=('Helvetica', -13))
        select_label.place(x=64, y=200)

        self.search_entry = tk.Entry(self.body, bg=MAIN_BG, bd=1, width=17, highlightcolor='#ffffff', fg='#999ca6',
                                     font=('Helvetica', -14))
        self.search_entry.insert(0, 'Search by name')
        self.search_entry.bind('<FocusIn>', self.on_entry_click)
        self.search_entry.bind("<KeyRelease>", self.search_by_name)
        self.search_entry.bind('<FocusOut>', self.on_focusout)

        self.search_entry.place(x=143, y=200)

        stage_label = tk.Label(self.body, bg=MAIN_BG, text='Stage', fg='#12502d',
                                       font=('Helvetica', -14, "bold"))
        stage_label.place(x=320, y=200)

        # Hint for Stage
        stage_hint = tk.Label(self.body, bg='#e0ebeb', padx=2, text='?', fg='#12502d', font=('Helvetica', -9))
        stage_hint.bind("<Enter>", self.stage_hint_show)
        stage_hint.bind("<Leave>", self.stage_hint_hide)
        stage_hint.place(x=370, y=202)

        add_date_label = tk.Label(self.body, bg=MAIN_BG, text='Add date', fg='#12502d',
                                       font=('Helvetica', -14, "bold"))
        add_date_label.place(x=460, y=200)

        self.base.start_loading()
        self.load_job_table()
        self.recount_status()

        self.active_tab = ConnectOptions(self)
        self.active_tab.refresh_status()
        self.base.stop_loading()

    def change_tab(self, event):
        """Change tab in menu to active."""
        tabs = {'connect': 'ConnectOptions', 'accept': 'AcceptOptions', 'message': 'MessageOptions', 'forward': 'ForwardOptions'}
        self.active_tab.close_options()
        for i in event.widget.master.winfo_children():
            i.config(bg='#f9fff9', fg='#0f743a')
        event.widget.config(bg='#10b858', fg='white')
        self.active_tab = eval(tabs[event.widget.winfo_name()])(self)
        self.active_tab.refresh_status()

    def start_task(self, event):
        check_version = self.base.user.get(self.base.api_server + "/api/check_version?version=" + self.base.version_app).json()
        if check_version['actual']:
            self.start_task_btn.place_forget()
            self.pause_task_btn.place(x=20, y=120)
            self.stop_task_btn.place(x=160, y=120)
            if type(self.active_tab).__name__ == 'ConnectOptions':
                if self.data['continue_from_page']:
                    if messagebox.askyesno("From Start or Continue", "At last time you stop this task at page {} Click 'YES' if you want to continue or 'NO' if you want start from beginning.".format(self.data['continue_from_page'])):
                        self.active_tab.start_task(continue_from_page=self.data['continue_from_page'])
                    else:
                        self.active_tab.start_task()
                else:
                    self.active_tab.start_task()
            else:
                self.active_tab.start_task()
        else:
            messagebox.showerror("Need Update", "You need update program. Visit our website and download new version")
            # self.base.update_app() # for auto-update but now its not realized yet

    def pause_task(self, event):
        self.pause_task_btn.place_forget()
        self.continue_task_btn.place(x=20, y=120)
        self.work = 'PAUSE'

    def unpause_task(self, event):
        self.continue_task_btn.place_forget()
        self.pause_task_btn.place(x=20, y=120)
        self.work = 'WORK'

    def stop_task(self, event):
        self.process_log('Stopping work please wait..')
        self.work = 'STOP'

    def stopped_work(self, text='Work stopped!'):
        """Change buttons when work stopped."""
        self.work = 'WORK'
        self.pause_task_btn.place_forget()
        if hasattr(self, 'continue_task_btn'):
            self.continue_task_btn.place_forget()
        self.stop_task_btn.place_forget()
        self.start_task_btn.place(x=20, y=120)
        self.process_log(text)

    def back(self, event):
        self.base.change_view('TaskListView')

    def _on_select_all_checkbox(self, event):
        if self.select_all_checkbox.selected:
            self.select_all_checkbox.configure(text='[ ]')
            self.select_all_checkbox.selected = False
            for c, v in self.checkbox_items.items():
                v.configure(text='[ ]')
                v.selected = False
        else:
            self.select_all_checkbox.configure(text='[x]')
            self.select_all_checkbox.selected = True
            for c, v in self.checkbox_items.items():
                v.configure(text='[x]')
                v.selected = True

    def load_job_table(self, search_query=None):
        """Load main table with candidates.

        :param: query -- Search query from UI.
        """
        self.canvas_frame = tk.Frame(self.body, width=768, height=364)
        self.canvas_frame.place(x=0, y=236)
        self.canv = tk.Canvas(self.canvas_frame, bg=MAIN_BG)

        self.table_frame = tk.Frame(self.canv, width=768, height=364, bg=MAIN_BG)
        self.table_frame.place(x=0, y=0)

        self.canv.config(width=748, height=364)
        self.canv.config(highlightthickness=0)
        self.canv.create_window((0, 200), window=self.table_frame, anchor='w')
        self.sbar = tk.Scrollbar(self.canvas_frame)
        self.sbar.config(command=self.canv.yview)
        self.canv.config(yscrollcommand=self.sbar.set)
        self.sbar.pack(side='right', fill='y')
        self.canv.pack(side='left', expand='yes', fill='both')

        self.candidate_list = self.base.user.get(
                self.base.api_server + "/api/tasks/" + str(self.data['id']) + "/candidates/").json()

        if search_query and search_query != '':
            self.candidate_list = [i for i in self.candidate_list if search_query.lower() in i['candidate']['full_name'].lower()]
        # The loop is output every row as a new frame (line)
        self.y_poss = 5
        self.lines_on_table = []
        for j in self.candidate_list:
            self._add_new_line_in_table(j)

        self.table_frame.configure(height=self.y_poss)
        self.canv.configure(scrollregion=self.canv.bbox("all"))
        self.canv.yview_moveto(0)
        if self.y_poss < self.canvas_frame['height']:
            self.canv.unbind_all("<MouseWheel>")
        else:
            self.canv.bind_all("<MouseWheel>", self._on_mousewheel)

    def add_new_profile(self, data):
        """Add new candidate profile with parsed data to our table.

        :param: data -- candidate data
        :returns: created profile id or 'Already exist' - if this user already exist.
        """
        headers = {'content-type': 'application/json'}
        data.pop('element', None)
        data = {'candidate': data, 'task': self.data['id']}
        data['send_connect'] = data['candidate'].pop('send_connect', None)

        resp = self.base.user.post(self.base.api_server + "/api/candidate/", data=json.dumps(data),
                                   headers=headers)
        if resp.status_code == 201:
            data = resp.json()
            self._add_new_line_in_table(data)
            self.base.root.after_idle(self.frame_upd)
            self.candidate_list.append(data)
            # Recount status and update text
            self.recount_status()
            self.active_tab.refresh_status()

    def frame_upd(self):
        """Method for update table size and scroll region and recount_status."""
        self.table_frame.config(height=self.y_poss)
        self.canv.configure(scrollregion=self.canv.bbox("all"))
        if self.y_poss < self.canvas_frame['height']:
            self.canv.unbind_all("<MouseWheel>")
        else:
            self.canv.bind_all("<MouseWheel>", self._on_mousewheel)

    def _add_new_line_in_table(self, line_data):
        """Display new line in table.

        :param: line_data -- data for line.
        """
        line = tk.Frame(self.table_frame, width=738, height=50, bg=MAIN_BG)
        line.candidate_id = line_data['id']
        line.linkedin_url = line_data['candidate']['linkedin_url']
        self.lines_on_table.append(line)

        line.place(x=15, y=self.y_poss)
        separ = tk.Frame(line, width=738, height=1, bg='#DADBDF')
        separ.place(x=0, y=0)

        checkbox_btn = tk.Label(line, text='[ ]', fg='#12502d', font=('Helvetica', -17, 'bold'), bg=MAIN_BG)
        checkbox_btn.selected = False
        self.checkbox_items[line_data['id']] = checkbox_btn
        checkbox_btn.bind("<Button-1>", lambda event, jid=line_data['id']: self.change_checkbox(jid=jid))
        checkbox_btn.place(x=20, y=17)

        full_name = tk.Label(line, text=line_data['candidate']['full_name'], font=('Helvetica', -13, "bold"), fg='#171c34',
                            bg=MAIN_BG)
        full_name.place(x=128, y=17)

        send_connect = tk.Label(line, bg='#e6f1ea', text='C', fg='white', padx=5, pady=2, font=('Helvetica', -12, "bold"))
        send_connect.bind("<Button-1>", self.change_status)
        send_connect.place(x=311, y=17)
        if line_data['send_connect']:
            send_connect.config(bg='green', fg='white')

        accept_connect = tk.Label(line, bg='#e6f1ea', text='A', fg='white', padx=5, pady=2, font=('Helvetica', -12, "bold"))
        accept_connect.bind("<Button-1>", self.change_status)
        accept_connect.place(x=341, y=17)
        if line_data['accept_connect']:
            accept_connect.config(bg='green', fg='white')

        send_message = tk.Label(line, bg='#e6f1ea', text="M", fg='white', padx=5, pady=2, font=('Helvetica', -12, "bold"))
        send_message.bind("<Button-1>", self.change_status)
        send_message.place(x=371, y=17)
        if line_data['send_message']:
            send_message.config(bg='green', fg='white')

        send_forward = tk.Label(line, bg='#e6f1ea', text="F", fg='white', padx=5, pady=2, font=('Helvetica', -12, "bold"))
        send_forward.bind("<Button-1>", self.change_status)
        send_forward.place(x=401, y=17)
        if line_data['send_forward']:
            send_forward.config(bg='green', fg='white')

        add_date = tk.Label(line, text=line_data['created_at'].split('T')[0], font=('Helvetica', -12), fg='#171c34',
                            bg=MAIN_BG)
        add_date.place(x=446, y=17)

        if line_data['candidate'].get('linkedin_url', None):
            browser_btn = tk.Label(line, text='in', fg='white', padx=1, pady=0, font=('Helvetica', -16, 'bold'), bg='#0077B7')
            browser_btn.bind("<Button-1>", lambda event, url=line_data['candidate']['linkedin_url']: webbrowser.open(url))
            browser_btn.bind("<Enter>", lambda event, h=browser_btn: h.configure(font=('Helvetica', -19, 'bold')))
            browser_btn.bind("<Leave>", lambda event, h=browser_btn: h.configure(font=('Helvetica', -16, 'bold')))
            browser_btn.place(x=678, y=17)

        delete_btn = tk.Label(line, text='D', fg='#7a1000', font=('Helvetica', -17, 'bold'), bg=MAIN_BG)
        delete_btn.bind("<Button-1>", lambda event, jid=line_data: self.on_delete(data=jid['id']))
        delete_btn.bind("<Enter>", lambda event, h=delete_btn: h.configure(font=('Helvetica', -20, 'bold')))
        delete_btn.bind("<Leave>", lambda event, h=delete_btn: h.configure(font=('Helvetica', -17, 'bold')))
        delete_btn.place(x=705, y=17)

        self.y_poss += 50

    def change_status(self, event):
        if messagebox.askyesno("Change Status", "Do you want to change status?"):
            status = {'C': 'send_connect', 'A': 'accept_connect', 'M': 'send_message', 'F': 'send_forward'}
            headers = {'content-type': 'application/json'}

            field = status[event.widget.cget('text')]
            state = False
            if event.widget.cget('bg') == '#e6f1ea':
                state = True

            data = {field: state}
            resp = self.base.user.patch(self.base.api_server + "/api/candidate/" + str(event.widget.master.candidate_id), data=json.dumps(data),
                                        headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if state:
                    event.widget.config(bg='green')
                else:
                    event.widget.config(bg='#e6f1ea')
                # MAYBE NEED BETTER CODE FOR UPDATE DATA IN LIST HERE
                self.candidate_list.remove([i for i in self.candidate_list if i['id'] == data['id']][0])
                self.candidate_list.append(data)
                # Recount status and update text
                self.recount_status()
                self.active_tab.refresh_status()

    def change_checkbox(self, jid):
        if not self.checkbox_items[jid].selected:
            self.checkbox_items[jid].configure(text='[x]')
            self.checkbox_items[jid].selected = True
        else:
            self.checkbox_items[jid].configure(text='[ ]')
            self.checkbox_items[jid].selected = False
            self.select_all_checkbox.configure(text='[ ]')

    def on_delete(self, data):
        move_next_line = False
        for_delete = None
        for k in self.lines_on_table:
            if k.candidate_id == data:
                for_delete = k
                self.delete_candidate(k.candidate_id)
                k.place_forget()
                move_next_line = True
                self.y_poss -= 50
                continue
            if move_next_line:
                k.place_configure(x=15, y=int(k.winfo_y()) - 50)

        self.lines_on_table.remove(for_delete)
        self.table_frame.configure(height=self.y_poss)
        self.canv.configure(scrollregion=self.canv.bbox("all"))
        if self.y_poss < self.canvas_frame['height']:
            self.table_frame.place_configure(x=0, y=0)
            self.canv.unbind_all("<MouseWheel>")

    def delete_candidate(self, cand_id):
        self.base.user.delete(self.base.api_server + "/api/candidate/" + str(cand_id))
        self.candidate_list.remove([i for i in self.candidate_list if i['id'] == cand_id][0])
        # Recount status and update text
        self.recount_status()
        self.active_tab.refresh_status()

    def _on_mousewheel(self, event):
        self.canv.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def process_log(self, text):
        """Display process status for current job.

        :param: text -- Text to display
        """
        self.process_label.config(text=text)

    def open_settings(self, data):
        self.base.change_view('EditTaskView', data=data, back_to=self.view_name)

    def update_info_block(self, data):
        self.data = data
        self.title_label.config(text=self.data['task_name'])
        self.settings_btn.place_configure(x=self.title_label.winfo_reqwidth() + 70, y=20)
        self.process_label.place_configure(x=self.title_label.winfo_reqwidth() + 120, y=20)

    def recount_status(self):
        self.count_connected_today = [i for i in self.candidate_list if i['send_connect'] and datetime.datetime.strptime(i['created_at'].split('T')[0], "%Y-%m-%d").date() == datetime.date.today()].__len__()
        self.count_connected_all = [i for i in self.candidate_list if i['send_connect']].__len__()
        self.count_accepted_all = [i for i in self.candidate_list if i['accept_connect']].__len__()
        self.count_wait_accept = self.count_connected_all - self.count_accepted_all
        self.count_send_message_all = [i for i in self.candidate_list if i['send_message']].__len__()
        self.count_can_send_message_to = self.count_accepted_all - self.count_send_message_all
        self.count_send_forward_all = [i for i in self.candidate_list if i['send_forward']].__len__()
        self.count_can_send_forward = [i for i in self.candidate_list if i['send_connect'] and i['accept_connect'] and i['send_message'] and not i['send_forward']].__len__()

    def stage_hint_show(self, event):
        self.stage_hint_frame = tk.Frame(self.body, width=250, height=150, bg='#1a1a1a')
        self.stage_hint_frame.place(x=100, y=100)
        hint_text = tk.Label(self.stage_hint_frame, fg='white', bg='#1a1a1a', justify='left',  text="Stage display current situation for candidate.\n \n C - Connected \n A - Accepted \n M - Message was send \n F - Forward message was send"
                                                                                  "\n\n     You can change any stage if you need \n"
                                                                                  "            Just click on some of them")
        hint_text.place(x=5, y=5)

    def stage_hint_hide(self, event):
        self.stage_hint_frame.place_forget()

    def on_entry_click(self, event):
        """function that gets called whenever entry is clicked"""
        if self.search_entry.get() == 'Search by name':
            self.search_entry.delete(0, "end")  # delete all the text in the entry
            self.search_entry.insert(0, '')  # Insert blank for user input
            self.search_entry.config(fg='black')

    def search_by_name(self, event):
        """Search in candidates by name.

        Searching start after 1 second after last entered char.
        We save this time in global variable enter_time_for_search
        """
        global enter_time_for_search
        enter_time_for_search = time.time()

        def go_search():
            global enter_time_for_search
            if time.time() - enter_time_for_search > 1:
                self.search_entry['state'] = 'disabled'
                self.base.start_loading()
                self.canvas_frame.place_forget()
                self.base.root.update()
                self.load_job_table(self.search_entry.get())
                self.base.stop_loading()
                self.base.root.update()
                self.search_entry['state'] = 'normal'

        if self.search_entry.get().__len__() > 1 and event.keysym not in ['Shift_L', 'Caps_Lock', 'Tab', 'Alt_L', 'Control_L'] or event.keysym == 'BackSpace':
            self.base.root.after(1100, go_search)

    def on_focusout(self, event):
        if self.search_entry.get() == '':
            self.search_entry.insert(0, 'Search by name')
            self.search_entry.config(fg='#999ca6')


class ConnectOptions:
    def __init__(self, window):
        self.window = window
        self.window.option_btn.bind("<Button-1>", self.show_body)

    def show_body(self, event):
        self.options_frame = tk.Frame(self.window.body, bg='#f9fff9', width=768, height=200, highlightbackground="#b5bcb7", highlightcolor="#b5bcb7", highlightthickness=1)
        self.options_frame.place(x=0, y=170)
        self.window.option_btn.config(text='OPTIONS -')
        self.window.option_btn.config(text='    SAVE    ')
        self.window.start_task_btn.place_forget()
        message_note_label = tk.Label(self.options_frame, text='Message for connect with note         {first_name} - Change to first name,   {full_name} - Change to full name',
                                      fg='#12502d', font=('Helvetica', -13), bg='#f9fff9')
        message_note_label.place(x=15, y=1)

        self.count_label = tk.Label(self.options_frame, bg='#f9fff9', text='0/300', font=('Helvetica', -14, "bold"))
        self.count_label.place(x=670, y=1)

        self.message_note = tk.Text(self.options_frame, width=90, height=8)
        self.message_note.bind("<KeyRelease>", self.message_count)
        self.message_note.place(x=15, y=23)

        if self.window.data['connect_note_text']:
            self.message_note.insert(1.0, self.window.data['connect_note_text'])
            self.message_count()

        if self.window.data['connect_with_message']:
            self.checkbox_btn = tk.Label(self.options_frame, text='[x]', fg='#12502d', font=('Helvetica', -17, 'bold'), bg='#f9fff9')
            self.checkbox_btn.selected = True
        else:
            self.checkbox_btn = tk.Label(self.options_frame, text='[ ]', fg='#12502d', font=('Helvetica', -17, 'bold'),
                                         bg='#f9fff9')
            self.checkbox_btn.selected = False
        self.checkbox_btn.bind("<Button-1>", self.change_checkbox_state)
        self.checkbox_btn.place(x=15, y=165)

        checkbox_label = tk.Label(self.options_frame, text='Connect with note', fg='#12502d', font=('Helvetica', -13), bg='#f9fff9')
        checkbox_label.place(x=40, y=167)

        max_connect_label = tk.Label(self.options_frame, text='MAX send connect to', fg='#12502d', bg='#f9fff9', font=('Helvetica', -13))
        max_connect_label.place(x=200, y=167)
        self.max_connect_entry = tk.Entry(self.options_frame, width=5, font=('Helvetica', -17, 'bold'))
        if self.window.data['max_send_connect']:
            self.max_connect_entry.insert(0, self.window.data['max_send_connect'])
        self.max_connect_entry.place(x=340, y=167)

        self.window.option_btn.bind("<Button-1>", self.save_data)

    def close_options(self):
        """Close option frame if he opens.

        :returns: True - if we close or False - if options not be opened"""
        if hasattr(self, 'options_frame'):
            self.options_frame.place_forget()
            self.window.option_btn.config(text='OPTIONS +')
            self.window.start_task_btn.place(x=20, y=120)
            return True
        else:
            return False

    def save_data(self, event):
        headers = {'content-type': 'application/json'}

        data = {
            "connect_note_text": str(self.message_note.get(1.0, 'end')).rstrip() or None,
            "connect_with_message": self.checkbox_btn.selected,
            "max_send_connect": self.max_connect_entry.get() or None
        }
        resp = self.window.base.user.patch(self.window.base.api_server + "/api/tasks/" + str(self.window.data['id']), data=json.dumps(data), headers=headers)
        if resp.status_code == 200:
            self.window.data = resp.json()
            self.close_options()
            self.window.option_btn.bind("<Button-1>", self.show_body)
        else:
            messagebox.showerror("Error", "Server or internet connection problem")

    def change_checkbox_state(self, event):
        if event.widget.selected:
            event.widget.configure(text='[ ]')
            event.widget.selected = False
        else:
            event.widget.configure(text='[x]')
            event.widget.selected = True

    def message_count(self, event=None):
        count = len(self.message_note.get(1.0, 'end').rstrip())
        self.count_label.config(text=str(count)+'/300')
        if count > 300:
            self.count_label.config(fg='red')
        else:
            self.count_label.config(fg='black')

    def start_task(self, continue_from_page=None):
        self.window.process_log('Starting connect people..')
        if self.window.data['task_type'] == 'fast':
            t = threading.Thread(target=FastConnect, args=(self.window, continue_from_page, ))
        else:
            t = threading.Thread(target=Connect, args=(self.window, continue_from_page, ))
        t.start()

    def refresh_status(self):
        self.window.notification_area.config(text='All Connected: %s  |  Today Connected: %s' % (self.window.count_connected_all, self.window.count_connected_today))


class AcceptOptions:
    def __init__(self, window):
        self.window = window
        self.window.option_btn.bind("<Button-1>", self.show_body)

    def show_body(self, event):
        self.options_frame = tk.Frame(self.window.body, bg='#f9fff9', width=768, height=200, highlightbackground="#b5bcb7", highlightcolor="#b5bcb7", highlightthickness=1)
        self.options_frame.place(x=0, y=170)
        self.window.option_btn.config(text='    SAVE    ')
        self.window.start_task_btn.place_forget()
        no_content_yet_label = tk.Label(self.options_frame, text='NO SETTINGS FOR ACCEPT YET!', fg='#b5b7b5', font=('Helvetica', -20), bg='#f9fff9')
        no_content_yet_label.place(x=230, y=60)

        self.window.option_btn.bind("<Button-1>", self.save_data)

    def save_data(self, event):
        # SAVE DATA WILL BE HERE!
        self.close_options()
        self.window.option_btn.bind("<Button-1>", self.show_body)

    def close_options(self):
        """Close option frame if he opens.

        :returns: True - if we close or False - if options not be opened"""
        if hasattr(self, 'options_frame'):
            self.options_frame.place_forget()
            self.window.option_btn.config(text='OPTIONS +')
            self.window.start_task_btn.place(x=20, y=120)
            return True
        else:
            return False

    def start_task(self):
        self.window.process_log('Starting review accept people..')
        t = threading.Thread(target=Accept, args=(self.window,))
        t.start()

    def refresh_status(self):
        self.window.notification_area.config(text='All Accepted: %s  |  Wait Accept: %s' % (self.window.count_accepted_all, self.window.count_wait_accept))


class MessageOptions:
    def __init__(self, window):
        self.window = window
        self.window.option_btn.bind("<Button-1>", self.show_body)

    def show_body(self, event):
        self.options_frame = tk.Frame(self.window.body, bg='#f9fff9', width=768, height=200, highlightbackground="#b5bcb7", highlightcolor="#b5bcb7", highlightthickness=1)
        self.options_frame.place(x=0, y=170)
        self.window.option_btn.config(text='    SAVE    ')
        self.window.start_task_btn.place_forget()
        message_note_label = tk.Label(self.options_frame, text='Text for Message', fg='#12502d',
                                      font=('Helvetica', -13), bg='#f9fff9')
        message_note_label.place(x=15, y=1)

        self.message_note = tk.Text(self.options_frame, width=90, height=8)
        self.message_note.place(x=15, y=23)
        if self.window.data['connect_message_text']:
            self.message_note.insert(1.0, self.window.data['connect_message_text'])

        self.window.option_btn.bind("<Button-1>", self.save_data)

    def close_options(self):
        """Close option frame if he opens.

        :returns: True - if we close or False - if options not be opened"""
        if hasattr(self, 'options_frame'):
            self.options_frame.place_forget()
            self.window.option_btn.config(text='OPTIONS +')
            self.window.start_task_btn.place(x=20, y=120)
            return True
        else:
            return False

    def save_data(self, event):
        headers = {'content-type': 'application/json'}

        data = {
            "connect_message_text": str(self.message_note.get(1.0, 'end')).rstrip() or None
        }
        resp = self.window.base.user.patch(self.window.base.api_server + "/api/tasks/" + str(self.window.data['id']),
                                           data=json.dumps(data), headers=headers)
        if resp.status_code == 200:
            self.window.data = resp.json()
            self.close_options()
            self.window.option_btn.bind("<Button-1>", self.show_body)
        else:
            messagebox.showerror("Error", "Server or internet connection problem")

    def start_task(self):
        self.window.process_log('Starting send messages..')
        t = threading.Thread(target=Message, args=(self.window,))
        t.start()

    def refresh_status(self):
        self.window.notification_area.config(text='Send Message: %s  |  Can Send Message: %s' % (self.window.count_send_message_all, self.window.count_can_send_message_to))


class ForwardOptions:
    def __init__(self, window):
        self.window = window
        self.window.option_btn.bind("<Button-1>", self.show_body)

    def show_body(self, event):
        self.options_frame = tk.Frame(self.window.body, bg='#f9fff9', width=768, height=200, highlightbackground="#b5bcb7", highlightcolor="#b5bcb7", highlightthickness=1)
        self.options_frame.place(x=0, y=170)
        self.window.option_btn.config(text='    SAVE    ')
        self.window.start_task_btn.place_forget()
        message_note_label = tk.Label(self.options_frame, text='Text for Forward Message', fg='#12502d',
                                      font=('Helvetica', -13), bg='#f9fff9')
        message_note_label.place(x=15, y=1)
        self.message_note = tk.Text(self.options_frame, width=90, height=8)
        self.message_note.place(x=15, y=23)
        if self.window.data['forward_message_text']:
            self.message_note.insert(1.0, self.window.data['forward_message_text'])
        self.window.option_btn.bind("<Button-1>", self.save_data)

    def close_options(self):
        """Close option frame if he opens.

        :returns: True - if we close or False - if options not be opened"""
        if hasattr(self, 'options_frame'):
            self.options_frame.place_forget()
            self.window.option_btn.config(text='OPTIONS +')
            self.window.start_task_btn.place(x=20, y=120)
            return True
        else:
            return False

    def save_data(self, event):

        headers = {'content-type': 'application/json'}

        data = {
            "forward_message_text": str(self.message_note.get(1.0, 'end')).rstrip() or None
        }
        resp = self.window.base.user.patch(self.window.base.api_server + "/api/tasks/" + str(self.window.data['id']),
                                           data=json.dumps(data), headers=headers)
        if resp.status_code == 200:
            self.window.data = resp.json()
            self.close_options()
            self.window.option_btn.bind("<Button-1>", self.show_body)
        else:
            messagebox.showerror("Error", "Server or internet connection problem")

    def start_task(self):
        self.window.process_log('Starting send forward messages..')
        t = threading.Thread(target=ForwardMessage, args=(self.window,))
        t.start()

    def refresh_status(self):
        self.window.notification_area.config(text='Send Forward: %s  |  Can Send Forward: %s' % (self.window.count_send_forward_all, self.window.count_can_send_forward))
