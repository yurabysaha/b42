import json

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from random import randint

from logic.basic import BaseMethod


class ForwardMessage(BaseMethod):
    def __init__(self, view):
        self.view = view
        BaseMethod.__init__(self)

        self.login()

        candidate_for_message = [i for i in self.view.candidate_list if
                                 i['send_connect'] and i['accept_connect'] and i['send_message'] and not i['send_forward']]
        for user in candidate_for_message:
            try:
                if self.send_message(user):
                    self.update_on_view(user['candidate']['linkedin_url'])
                    time.sleep(randint(20, 40))  # Pause after send message
            except Exception:
                self.view.base.root.after_idle(self.view.stopped_work)
                self.chrome.close()

        self.chrome.close()
        self.view.base.root.after_idle(self.view.stopped_work)

    def send_message(self, user):
        """Send message to current opened user on linkedin and sleep to 20-40sec after.

        :param: user -- User instance
        :returns: True -- if send message successful, False -- if send message unsuccessful
        """
        self.check_pause()
        self.chrome.get(user['candidate']['linkedin_url'])
        time.sleep(2)
        try:
            self.chrome.find_element_by_xpath("//button[contains(@data-control-name, 'overlay.close')]").click()
            time.sleep(1)
        except:
            pass
        try:
            button = self.chrome.find_element_by_css_selector("button[class*='message button-primary-large']")
        except:
            return False
        mouse = ActionChains(self.chrome)
        mouse.move_to_element(button).perform()
        time.sleep(0.5)
        button.click()
        time.sleep(0.5)
        message = self.view.data['forward_message_text']
        textarea = self.chrome.find_element_by_xpath(".//textarea")
        messages = message.split('\n')
        for i in messages:
            textarea.send_keys(i)
            textarea.send_keys(Keys.SHIFT + Keys.ENTER)

        textarea.send_keys(Keys.CONTROL + Keys.ENTER)
        time.sleep(0.5)
        self.chrome.find_element_by_xpath("//button[contains(@data-control-name, 'overlay.close')]").click()
        self.view.process_log("Forward Message sent to - %s" % user['candidate']['full_name'])
        return True

    def update_on_view(self, linkedin_url):
        headers = {'content-type': 'application/json'}
        line = [i for i in self.view.lines_on_table if i.linkedin_url == linkedin_url][0]

        if line.winfo_children()[6].cget('text') == 'F':
            data = {'send_forward': True}
            resp = self.view.base.user.patch(
                self.view.base.api_server + "/api/candidate/" + str(line.candidate_id),
                data=json.dumps(data),
                headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                line.winfo_children()[6].config(bg='green', fg='white')
                # MAYBE NEED BETTER CODE FOR UPDATE DATA IN LIST HERE
                self.view.candidate_list.remove([i for i in self.view.candidate_list if i['id'] == data['id']][0])
                self.view.candidate_list.append(data)
                # Recount status and update text
                self.view.recount_status()
                self.view.active_tab.refresh_status()
