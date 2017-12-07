import tkinter as tk
import json

MAIN_BG = '#ffffff'


class TaskListView:
    def __init__(self, base):
        self.base = base
        self.body = tk.Frame(self.base.root, bg=MAIN_BG)
        self.checkbox_items = {}
        notification = Notification(self.body)

        self.base.views_frame['TaskListView'] = self
        self.body.place(x=0, y=0, width=768, height=680)

        self.title_label = tk.Label(self.body, bg=MAIN_BG, text='TASKS LIST', font=('Helvetica', -16, "bold"))
        self.title_label.place(x=15, y=18)

        # User profile and notifications
        self.my_profile_btn = tk.Label(self.body, text="MY PROFILE", bg="#919191", padx=40, pady=12, fg='white',
                                       font=('Helvetica', -14, 'bold'))
        self.my_profile_btn.bind("<Button-1>", notification.display_or_close)
        self.my_profile_btn.bind("<Enter>", lambda event, h=self.my_profile_btn: h.configure(bg="#919191"))
        self.my_profile_btn.bind("<Leave>", lambda event, h=self.my_profile_btn: h.configure(bg="#919191"))
        self.my_profile_btn.place(x=540, y=5)

        self.notification_btn = tk.Label(self.body, text="0", bg="#919191", padx=16, pady=12, fg='white',
                                         font=('Helvetica', -14, 'bold'))
        self.notification_btn.bind("<Button-1>", notification.display_or_close)
        self.notification_btn.bind("<Enter>", lambda event, h=self.notification_btn: h.configure(bg="#c1c1c1"))
        self.notification_btn.bind("<Leave>", lambda event, h=self.notification_btn: h.configure(bg="#919191"))
        self.notification_btn.place(x=713, y=5)

        self.create_task_btn = tk.Label(self.body, text="CREATE NEW TASK", bg="#10b858", padx=40, pady=12, fg='white',
                                        font=('Helvetica', -14, 'bold'))
        self.create_task_btn.bind("<Button-1>", self.create_job)
        self.create_task_btn.bind("<Enter>", lambda event, h=self.create_task_btn: h.configure(bg="#0f743a"))
        self.create_task_btn.bind("<Leave>", lambda event, h=self.create_task_btn: h.configure(bg="#10b858"))
        self.create_task_btn.place(x=15, y=69)

        self.select_all_checkbox = tk.Label(self.body, text='[ ]', fg='#12502d', bg=MAIN_BG, font=('Helvetica', -17, 'bold'))
        self.select_all_checkbox.bind("<Button-1>", self._on_select_all_checkbox)
        self.select_all_checkbox.selected = False
        self.select_all_checkbox.place(x=35, y=130)

        self.select_label = tk.Label(self.body, bg=MAIN_BG, text='Select all', fg='#12502d', font=('Helvetica', -13))
        self.select_label.place(x=64, y=133)
        self.job_name_label = tk.Label(self.body, bg=MAIN_BG, text='Task Name', fg='#12502d', font=('Helvetica', -14, "bold"))
        self.job_name_label.place(x=143, y=133)

        self.add_date_label = tk.Label(self.body, bg=MAIN_BG, text='Сreate date', fg='#12502d', font=('Helvetica', -14, "bold"))
        self.add_date_label.place(x=368, y=133)

        self.base.start_loading()
        self.load_job_table()

        if self.y_poss > self.canvas_frame['height']:
            self.canv.bind_all("<MouseWheel>", self._on_mousewheel)
        self.base.stop_loading()

    def _on_mousewheel(self, event):
        self.canv.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def logout(self, event):
        self.base.user.delete(self.base.api_server + "/api/sessions")
        self.base.change_view('LoginView')

    def create_job(self, event):
        self.base.change_view('CreateJobView')

    def load_job_table(self):
        self.canvas_frame = tk.Frame(self.body, width=768, height=437)
        self.canvas_frame.place(x=0, y=163)
        self.canv = tk.Canvas(self.canvas_frame, bg=MAIN_BG)

        self.table_frame = tk.Frame(self.canv, width=768, height=437, bg=MAIN_BG)
        self.table_frame.place(x=0, y=0)

        self.canv.config(width=748, height=437)
        self.canv.config(highlightthickness=0)
        self.canv.create_window((0, 200), window=self.table_frame, anchor='w')
        self.sbar = tk.Scrollbar(self.canvas_frame)
        self.sbar.config(command=self.canv.yview)
        self.canv.config(yscrollcommand=self.sbar.set)
        # self.sbar.pack(side='right', fill='y')
        self.canv.pack(side='left', expand='yes', fill='both')

        self.job_list = self.base.user.get(self.base.api_server + "/api/tasks/").json()

        # Циклом виводимо інфу кожен рядок це новий фрейм (line)
        self.y_poss = 5
        self.lines_on_table = []
        if not self.job_list:
            placeholder = tk.Label(self.body, text="YOU DON'T HAVE ANY TASKS YET!", fg='#cecece', bg=MAIN_BG, font=('Helvetica', -20, 'bold'))
            placeholder.place(x=200, y=320)
        else:
            for j in self.job_list:
                line_bg = MAIN_BG
                if self.lines_on_table.__len__() % 2 == 0:
                    line_bg = '#f4f8fb'
                line = tk.Frame(self.table_frame, width=738, height=50, bg=line_bg)
                line.job_id = j['id']
                self.lines_on_table.append(line)
                line.bind("<Button-1>", lambda event, data=j: self.open_job(data=data))
                line.place(x=15, y=self.y_poss)

                checkbox_btn = tk.Label(line, text='[ ]', fg='#12502d', font=('Helvetica', -17, 'bold'), bg=line_bg)
                checkbox_btn.selected = False
                checkbox_btn.place(x=20, y=16)
                self.checkbox_items[j['id']] = checkbox_btn
                checkbox_btn.bind("<Button-1>", lambda event, jid=j['id']: self.change_checkbox(jid=jid))

                name = j['task_name']
                if len(name) > 24:
                    name = j['task_name'][:24] + '...'
                job_name = tk.Label(line, text=name, font=('Helvetica', -13, "bold"), fg='#12502d', bg=line_bg)
                job_name.place(x=128, y=17)
                job_name.bind("<Button-1>", lambda event, data=j: self.open_job(data=data))

                add_date = tk.Label(line, text=j['created_at'].split('T')[0], font=('Helvetica', -12), fg='#12502d', bg=line_bg)
                add_date.place(x=352, y=17)
                add_date.bind("<Button-1>", lambda event, data=j: self.open_job(data=data))

                settings_btn = tk.Label(line, text='S', fg='#545956', font=('Helvetica', -17, 'bold'), bg=line_bg)
                settings_btn.bind("<Button-1>", lambda event, data=j: self.open_settings(data=data))
                settings_btn.bind("<Enter>", lambda event, h=settings_btn: h.configure(font=('Helvetica', -20, 'bold')))
                settings_btn.bind("<Leave>", lambda event, h=settings_btn: h.configure(font=('Helvetica', -17, 'bold')))
                settings_btn.place(x=669, y=17)

                delete_btn = tk.Label(line, text='D', fg='#7a1000', font=('Helvetica', -17, 'bold'), bg=line_bg)
                delete_btn.place(x=705, y=17)
                delete_btn.bind("<Button-1>", lambda event, jid=j: self.on_delete(data=jid['id']))
                delete_btn.bind("<Enter>", lambda event, h=delete_btn: h.configure(font=('Helvetica', -20, 'bold')))
                delete_btn.bind("<Leave>", lambda event, h=delete_btn: h.configure(font=('Helvetica', -17, 'bold')))

                self.y_poss += 50

            self.table_frame.configure(height=self.y_poss)
            self.canv.configure(scrollregion=self.canv.bbox("all"))
            self.canv.yview_moveto(0)
            if self.y_poss < self.canvas_frame['height']:
                self.canv.unbind_all("<MouseWheel>")

    def open_job(self, data):
        self.base.change_view('TaskView_' + str(data['id']), data=data)

    def open_settings(self, data):
        self.base.change_view('EditTaskView', data=data, back_to='TaskListView')

    def delete_job(self, data):
        self.base.user.delete(self.base.api_server + "/api/tasks/{}".format(data))

    def change_checkbox(self, jid):
        if not self.checkbox_items[jid].selected:
            self.checkbox_items[jid].configure(text='[x]')
            self.checkbox_items[jid].selected = True
        else:
            self.checkbox_items[jid].configure(text='[ ]')
            self.checkbox_items[jid].selected = False
            self.select_all_checkbox.configure(text='[ ]')

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

    def on_delete(self, data):
        move_next_line = False
        for_delete = None
        for k in self.lines_on_table:
            if k.job_id == data:
                for_delete = k
                self.delete_job(k.job_id)
                k.place_forget()
                move_next_line = True
                self.y_poss -= 50
                continue
            if move_next_line:
                k.place_configure(x=15, y=int(k.winfo_y()) - 50)
                if k["bg"] == MAIN_BG:
                    k["bg"] = '#f4f8fb'
                else:
                    k["bg"] = MAIN_BG
                for i in k.winfo_children():
                    if i != k.winfo_children()[1]:
                        i.configure(bg=k["bg"])

        self.lines_on_table.remove(for_delete)
        self.table_frame.configure(height=self.y_poss)
        self.canv.configure(scrollregion=self.canv.bbox("all"))
        if self.y_poss < self.canvas_frame['height']:
            self.table_frame.place_configure(x=0, y=0)
            self.canv.unbind_all("<MouseWheel>")

    def open_my_profile(self, event):
        self.base.change_view('MyProfileView')

    def update_total_profiles(self, count, job_id):
        headers = {'content-type': 'application/json'}
        data = {
            "profiles": str(count),
        }
        self.base.user.put(self.base.api_server + "/api/import/jobs/{}".format(job_id),
                           data=json.dumps(data), headers=headers)
        for l in self.lines_on_table:
            if l.job_id == job_id:
                l.children['total_profiles'].config(text=str(count))
                break


class Notification:
    def __init__(self, root_window):
        self.body = root_window
        self.single_notification_y_pos = 1

    def display_or_close(self, event):
        if hasattr(self, 'notification_frame'):
            self.notification_frame.place_forget()
            delattr(self, 'notification_frame')
        else:
            self.notification_frame = tk.Frame(self.body, bg='#f4f4f4', width=330, height=200)
            # tk.Label(self.notification_frame, text='No Notifications Yet!', fg='#b5b7b5', bg='#f4f4f4',
            #          font=('Helvetica', -18, 'bold')).place(x=80, y=80)
            self.single_notification_y_pos = 1
            self.display_new_notification('firsssssss')
            self.display_new_notification('dsjdsjdjjfdjsf fdwhfjdf')
            self.display_new_notification('fdfjdshfjkd ufha dshgf wfhwlfh kljwa')
            self.notification_frame.place(x=427, y=51)

    def display_new_notification(self, text=''):
        single_frame = tk.Frame(self.notification_frame, bg='#f4f4f4', width=330, height=50)
        single_frame.place(x=1, y=self.single_notification_y_pos)
        self.single_notification_y_pos += 50

        notif_text = tk.Label(single_frame, text=text)
        notif_text.place(x=5, y=5)
        notif_read = tk.Label(single_frame, text='X', fg='red')
        notif_read.bind("<Button-1>", self.mark_as_read)
        notif_read.place(x=300, y=2)

    def mark_as_read(self, event):
        event.widget.master.place_forget()
        self.single_notification_y_pos = 1
        for wid in event.widget.master.master.winfo_children():
            wid.place_configure(x=1, y=self.single_notification_y_pos)
            self.single_notification_y_pos += 50
