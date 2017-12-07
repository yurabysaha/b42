import json
from logic.basic import BaseMethod
import time


class Accept(BaseMethod):
    def __init__(self, view=None):
        self.view = view
        BaseMethod.__init__(self)
        self.count_for_stop = 0
        self.blocks_count = 0

        self.login()
        self.verify_accept()

    def verify_accept(self):
        self.view.process_log("Review accepted. Wait Finish...")
        self.chrome.get(url='https://www.linkedin.com/mynetwork/invite-connect/connections')
        while True:
            blocks = self.chrome.find_elements_by_xpath("//div[@class='core-rail']//li")
            for u in blocks[self.blocks_count:]:
                name = u.find_element_by_xpath('./div/a/span[2]').text
                linkedin_url = u.find_element_by_xpath('./div/a').get_attribute('href')
                accept = any([i for i in self.view.candidate_list if i['candidate']['linkedin_url'] == linkedin_url and i['send_connect'] and not i['accept_connect']])
                if accept:
                    self.update_on_view(linkedin_url)
                    self.count_for_stop = 0
                else:
                    self.count_for_stop += 1

            if self.count_for_stop >= 40:
                break

            self.blocks_count = len(blocks)
            self.chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

        self.view.stopped_work("We think that nobody accepted you more")
        self.chrome.close()

    def update_on_view(self, linkedin_url):
        headers = {'content-type': 'application/json'}
        line = [i for i in self.view.lines_on_table if i.linkedin_url == linkedin_url][0]

        if line.winfo_children()[4].cget('text') == 'A':
            data = {'accept_connect': True}
            resp = self.view.base.user.patch(
                self.view.base.api_server + "/api/candidate/" + str(line.candidate_id),
                data=json.dumps(data),
                headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                line.winfo_children()[4].config(bg='green', fg='white')
                # MAYBE NEED BETTER CODE FOR UPDATE DATA IN LIST HERE
                self.view.candidate_list.remove([i for i in self.view.candidate_list if i['id'] == data['id']][0])
                self.view.candidate_list.append(data)
                # Recount status and update text
                self.view.recount_status()
                self.view.active_tab.refresh_status()
