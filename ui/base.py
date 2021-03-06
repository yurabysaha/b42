import json
import subprocess
from threading import Thread
from websocket import WebSocketApp, enableTrace

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

# --------------- WEBSOCKET LOGIC --------------------

    def connect_to_socket(self):
        """Its method run thread for websocket connection."""
        t = Thread(target=self.connection)
        t.start()

    def on_message(self, ws, message):
        """All message we receive here and convert from json."""
        response = json.loads(message)
        # IF we get message about notification!
        if response['stream'] == 'notifications':
            if response['payload']['action'] in ['subscribe', 'create', 'update']:

                # Notification instances data save in this var
                self.notifications_data = response['payload']['data']

                # When we receive data for notification we try update counter and notification block!
                self.views_frame['TaskListView'].notification.update_counter(self.notifications_data.__len__())
                self.views_frame['TaskListView'].notification.update_notification_block()
        # If we get new value of points!
        if response['stream'] == 'points':
            self.views_frame['TaskListView'].update_point_counter(response['payload']['data']['point'])
        return

    def on_error(self, ws, error):
        print(error)
        return

    def on_close(self, ws):
        print("### closed ###")
        return

    def on_open(self, ws):
        """Send subscribe message after connect."""
        msg = {
            'stream': "notifications",
            'payload': {
                'action': "subscribe",
                'data': {},
                'token': self.current_user['token']
            }
        }
        msg = json.dumps(msg)
        ws.send(msg)
        return

    def send_to_server(self, msg):
        """We can send message to server here.

        :param msg : dict which we send to server
        """
        msg = json.dumps(msg)
        self.ws.send(msg)
        return

    def connection(self):
        """Its method just create websocket connection."""
        enableTrace(True)
        self.ws = WebSocketApp("ws://95.46.44.227/", on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        # self.ws = WebSocketApp("ws://127.0.0.1:8000/", on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        self.ws.on_open = self.on_open

        self.ws.run_forever()
        return
