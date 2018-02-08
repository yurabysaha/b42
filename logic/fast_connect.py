import json
import re
from logic.basic import BaseMethod
import time


class FastConnect(BaseMethod):
    def __init__(self, view=None, continue_from_page=None):
        self.view = view
        BaseMethod.__init__(self)
        self.max_connect_today = self.view.data['max_send_connect'] or 1000
        self.max_connect_today = self.max_connect_today - self.view.count_connected_all

        self.login()

        page_number = 0 if not continue_from_page else continue_from_page - 1
        try:
            while True:
                page_number += 1
                self.save_current_page_in_db(page_number)

                candidates_list = self.connects_on_search_page(self.view.data['linkedin_url'], page_number)
                if candidates_list is False:
                    break

                for p in candidates_list:
                    if self.max_connect_today > 0:
                        if self.click_connect_person(p['element']):
                            self.max_connect_today -= 1
                            p['send_connect'] = True
                        self.view.add_new_profile(data=p)
                        self.check_pause()
                    else:
                        self.view.base.root.after_idle(self.view.stopped_work, 'You rich max limit for connect for this task')
                        self.chrome.close()
                        exit()
        except Exception as exc:
            self.view.base.root.after_idle(self.view.stopped_work, 'Work stopped with error. Try again')
            print(exc)
            self.chrome.close()
            exit()

    def connects_on_search_page(self, linkedin_search_url, page_number):
        """Get list with users linkedin_url and name.

        We open search page on page which we get from variable page_number.
        Than we parse all users name and linkedin urls and check if this user didn't added in our task already.

        :param: linkedin_search_url -- search page linkedin url
        :param: page_number -- int page number on search page.
        :return: permalinks_array - List of users with dict full_name, linkedin_url and task_id
        """

        self.check_pause()
        self.chrome.get('{}&page={}'.format(linkedin_search_url, page_number))
        self.view.process_log("Search on page {}".format(page_number))
        time.sleep(5)
        self.chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        user_list = self.chrome.find_elements_by_css_selector('ul[class *= "results-list"] li')

        if not user_list:
            return False

        candidates_array = []
        for i in user_list:
            data = {
                'element': "",
                'full_name': "",
                'task_id': self.view.data['id']
            }
            # Check pause
            self.check_pause()
            self.chrome.execute_script("arguments[0].scrollIntoView()", i)

            # Check LinkedIn limit on request
            try:
                i.find_element_by_css_selector("[class*='search-result__profile-blur']")
                self.view.base.root.after_idle(self.view.stopped_work, 'Linkedin - you’ve reached the commercial use limit')
                self.chrome.close()
                exit()
            except:
                pass

            try:
                # Check button Connect is present on page
                connect = i.find_element_by_css_selector(".button-secondary-medium").text
                if connect == 'Connect':
                    data['element'] = i
                else:
                    continue
            except Exception:
                continue

            try:
                data['full_name'] = i.find_element_by_class_name("actor-name").text
                if data['full_name'] == 'LinkedIn Member':
                    continue
            except Exception:
                continue

            candidates_array.append(data)

        return candidates_array

    def _scroll_to_element(self, element):
        """Element can be webdriver object or css_selector (string)"""
        try:
            if type(element) == str:
                element = self.chrome.find_element_by_css_selector(element)
            self.chrome.execute_script("arguments[0].scrollIntoView(false)", element)
        except:
            pass

    def click_connect_person(self, element):
        """Try send current user connect request.

        :return: True - if connect successful or False - if cant connect
        """
        try:
            self._scroll_to_element(element)

            connect_button = element.find_element_by_css_selector(".button-secondary-medium")
            connect_button.click()

            time.sleep(1)
            if not self.view.data['connect_with_message']:
                connect_user = self.chrome.find_element_by_css_selector("div[class*='send-invite'] button[class*='button-primary-large']")
                if not connect_user.is_enabled():
                    raise Exception
                connect_user.click()
                return True
            add_a_note = self.chrome.find_element_by_css_selector(".send-invite__actions > .button-secondary-large")
            add_a_note.click()
            time.sleep(1)
            text_field = self.chrome.find_element_by_css_selector("textarea[id='custom-message']")
            if not self.view.data['connect_note_text']:
                text_field.send_keys(" ")
            else:
                text_field.send_keys(self.view.data['connect_note_text'][0:299])
            send_button = self.chrome.find_element_by_css_selector(".button-primary-large.ml1")
            if not send_button.is_enabled():
                raise Exception
            send_button.click()
            time.sleep(1)
            return True
        except:
            return False

    def get_percent_for_connect(self, list_with_obj):
        """Get count for max connect people on current page.

        :param: list_with_obj -- List with current users in page
        :return: Count for max connect on this page
        """
        if not self.view.data['add_percent'] and self.view.data != '0':
            current_percent = 100
        else:
            current_percent = self.view.data['add_percent']

        try:
            percent = int(float(current_percent))
        except ValueError:
            digit = re.findall(r'\d+', current_percent)[0]
            percent = int(float(digit))

        max_send_count = len(list_with_obj) * percent / 100
        return max_send_count

    def save_current_page_in_db(self, page_number):
        """Save page on search into db.

        :param: page_number -- int page number which we save
        """

        headers = {'content-type': 'application/json'}

        data = {
            "continue_from_page": page_number
        }
        resp = self.view.base.user.patch(self.view.base.api_server + "/api/tasks/" + str(self.view.data['id']),
                                         data=json.dumps(data), headers=headers)
        if resp.status_code == 200:
            self.view.data = resp.json()
