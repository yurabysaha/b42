import os
import platform
import time
import datetime
from selenium import webdriver

os.environ['HEADLESS_DRIVER'] = 'drivers/chromedriver.exe'


class BaseMethod:
    def __init__(self):
        self.with_browser_gui = 1
        self.every = self.view.data['brake_every'] or 0
        self.period = self.view.data['brake_for'] or 0
        self.script_was_started = datetime.datetime.utcnow()
        self.script_will_stop = self.script_was_started + datetime.timedelta(minutes=self.every)

        if self.with_browser_gui == 0:  # Run without browser gui
            if platform.system() == 'Windows':
                self.chrome = webdriver.Chrome('drivers/headless_ie_selenium.exe')
            else:
                chrome_options = webdriver.ChromeOptions()
                prefs = {"profile.default_content_setting_values.notifications": 2}
                chrome_options.add_experimental_option("prefs", prefs)
                chrome_options.add_argument('--lang=en')
                chrome_options.add_argument('--disable-popup-blocking')
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("start-maximized")
                self.chrome = webdriver.Chrome(executable_path='drivers/chromedriver', chrome_options=chrome_options)
        else:
            if platform.system() == 'Windows':

                chrome_options = webdriver.ChromeOptions()
                prefs = {"profile.default_content_setting_values.notifications": 2}
                chrome_options.add_experimental_option("prefs", prefs)
                chrome_options.add_argument('--lang=en')
                chrome_options.add_argument("--start-maximized")
                self.chrome = webdriver.Chrome(executable_path='drivers/chromedriver.exe', chrome_options=chrome_options)
            else:
                chrome_options = webdriver.ChromeOptions()
                prefs = {"profile.default_content_setting_values.notifications": 2}
                chrome_options.add_experimental_option("prefs", prefs)
                chrome_options.add_argument('--lang=en')
                chrome_options.add_argument('--disable-popup-blocking')
                chrome_options.add_argument("start-maximized")
                self.chrome = webdriver.Chrome(executable_path='drivers/chromedriver', chrome_options=chrome_options)

    def login(self):
        try:
            # self.chrome.get(url='https://www.linkedin.com')
            # self.chrome.get(url='https://www.linkedin.com/uas/login?session_redirect=%2Fvoyager%2FloginRedirect%2Ehtml&fromSignIn=true&trk=uno-reg-join-sign-in')
            self.chrome.get(url='https://www.linkedin.com/uas/login')
            self.check_pause()
            self.view.process_log("Trying login ...")
            email = self.view.data['linkedin_email']
            password = self.view.data['linkedin_password']
            self.chrome.find_element_by_css_selector("input[type='text']").send_keys(email)
            self.chrome.find_element_by_css_selector("input[type='password']").send_keys(password)
            self.chrome.find_element_by_css_selector("input[type='submit']").click()
            self.check_pause()
            self.view.process_log("Login successful")
            time.sleep(2)

        except Exception as e:
            self.view.base.root.after_idle(self.view.stopped_work, 'Problem with login')
            self.chrome.close()
            exit()

    def check_pause(self):
        while self.view.work == 'PAUSE':
            time.sleep(1)

        if self.view.work == 'STOP':
            self.chrome.close()
            self.view.base.root.after_idle(self.view.stopped_work)
            exit()

        # Logic with automatically pause
        if self.every >= 1 and self.period >= 1:
            if datetime.datetime.utcnow() > self.script_will_stop:
                timer = self.period
                while timer > 0:
                    self.view.process_log("Periodic pause. Process'll continue after: " + str(timer) + " min.")
                    time.sleep(60)
                    timer -= 1

                self.script_will_stop = self.script_will_stop + datetime.timedelta(minutes=self.every + self.period)

    def security_check(self):
        """Sometimes linkedin make auto logout. We check if this happen there."""
        if 'https://www.linkedin.com/m/login' in self.chrome.current_url or 'https://www.linkedin.com/authwall' in self.chrome.current_url or 'captcha-v2' in self.chrome.current_url:
            while 'https://www.linkedin.com/m/login' in self.chrome.current_url or 'https://www.linkedin.com/authwall' in self.chrome.current_url or 'captcha-v2' in self.chrome.current_url:
                try:
                    email = self.view.data['linkedin_email']
                    password = self.view.data['linkedin_password']
                    self.chrome.find_element_by_css_selector("input[type='text']").send_keys(email)
                    self.chrome.find_element_by_css_selector("input[type='password']").send_keys(password)
                    self.chrome.find_element_by_css_selector("input[type='submit']").click()
                    time.sleep(1)
                except:
                    pass
                self.view.process_log("Security problem. You need login manually")
                time.sleep(2)
            self.view.process_log("Try back to work...")

    def get_formatted_text_for_message(self, full_name, text):
        """Insert first_name or full_name into message text.

        :return new_text - Text after inserting
        """
        splitted_name = full_name.split(' ')
        if '.' in splitted_name[0]:
            splitted_name[0] = splitted_name[0] + ' ' + splitted_name[1]
        first_name = splitted_name[0].title()
        new_text = text.replace('{full_name}', full_name).replace('{first_name}', first_name)
        return new_text
