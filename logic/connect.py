import json
import re
from logic.basic import BaseMethod
import time


class Connect(BaseMethod):
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

                parsed_list = self.parse_search_page(self.view.data['linkedin_url'], page_number)
                if not parsed_list:
                    break

                for p in parsed_list:
                    parsed_profile = self.parse_user_detail(p)
                    if not parsed_profile:
                        continue
                    if self.max_connect_today > 0:
                        if self.connect_person():
                            self.max_connect_today -= 1
                            parsed_profile['send_connect'] = True
                        self.view.add_new_profile(data=parsed_profile)
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

    def parse_search_page(self, linkedin_search_url, page_number):
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
            return []

        permalinks_array = []
        for i in user_list:
            data = {
                'full_name': "",
                'linkedin_url': "",
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
                data['linkedin_url'] = i.find_element_by_class_name("search-result__result-link").get_attribute("href")
            except Exception:
                continue

            try:
                data['full_name'] = i.find_element_by_class_name("actor-name").text
                if data['full_name'] == 'LinkedIn Member':
                    continue
            except Exception:
                continue

            # Check if this user already not added:  (Not need i this place already)
            # if not any(d['candidate'].get('linkedin_url', None) == data['linkedin_url'] for d in self.view.candidate_list):
            permalinks_array.append(data)

        return permalinks_array

    def _click_see_more_button(self, css_selector=None):
        display_see_more = True
        while display_see_more:
            try:
                see_more = self.chrome.find_element_by_css_selector(css_selector)
                self.chrome.execute_script("arguments[0].scrollIntoView()", see_more)
                time.sleep(1)
                self.chrome.execute_script("arguments[0].click();", see_more)
                time.sleep(1)
            except:
                display_see_more = False

    def _wait_element(self, element):
        counter = 0
        while counter < 20:
           try:
               self.chrome.find_element_by_xpath(element)
               break
           except:
               time.sleep(0.3)
               counter += 1

    def _scroll_to_element(self, element):
        """Element can be webdriver object or css_selector (string)"""
        try:
            if type(element) == str:
                element = self.chrome.find_element_by_css_selector(element)
            self.chrome.execute_script("arguments[0].scrollIntoView()", element)
        except:
            pass

    def connect_person(self):
        """Try send current user connect request.

        :return: True - if connect successful or False - if cant connect
        """
        try:
            self.chrome.execute_script("window.scrollTo(0, 0);")
            try:
                # For second circle connects
                connect_button = self.chrome.find_element_by_css_selector("button[class*='connect']")
                connect_button.click()
            except:
                # For third circle connects
                try:
                    # If connect button in drop-down in right corner with name '...'
                    tree_dot_button = self.chrome.find_element_by_css_selector(
                        "button > span[class='svg-icon-wrap'] > li-icon[type='ellipsis-horizontal-icon']")
                    tree_dot_button.click()
                    # tree_dot_button = self.chrome.find_element_by_css_selector("button[class*='dropdown-trigger ember-view'] li-icon[type='ellipsis-horizontal-icon']")
                    # tree_dot_button.click()
                except:
                    # If connect button in drop-down with name 'More...'
                    more_button = self.chrome.find_element_by_css_selector("div[class*='dropdown pv-top-card-overflow closed ember-view'] button")
                    more_button.click()
                time.sleep(1)

                # Two type how display Connect button in drop-down.
                try:
                    conn_btn = self.chrome.find_element_by_css_selector(
                        "li[class*='action connect overflow ember-view'] span[class='default-text']")
                except:
                    conn_btn = self.chrome.find_element_by_css_selector(
                        "li-icon[type='connect-icon']")
                conn_btn.click()

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
            send_button = self.chrome.find_element_by_css_selector(".button-primary-large.ml3")
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

    def parse_user_detail(self, data):
        """Parse user detail info.

        Returns parsed_data - if parse was correct. False if we already have this user in task list
        """
        self.check_pause()
        self.view.process_log("Parse - %s" % data['full_name'])
        profile_data = {"candidate": {
            "full_name": data['full_name']
        }}

        try:
            self.security_check()
            self.chrome.get(data['linkedin_url'])
            # Check if this user already not added:
            if any(d['candidate'].get('linkedin_url', None) == self.chrome.current_url for d in self.view.candidate_list):
                return False
            profile_data['candidate']['linkedin_url'] = self.chrome.current_url
            self.chrome.refresh()
            time.sleep(2)
            #  Get avatar. We have 3 situation how linkedin display avatar and try find correct.
            try:
                profile_data['candidate']['avatar'] = self.chrome.find_element_by_xpath("//img[contains(@class, 'top-card-section__image')]").get_attribute('src')
            except:
                try:
                    profile_data['candidate']['avatar'] = self.chrome.find_element_by_xpath("//img[contains(@class, 'presence-entity__image')]").get_attribute('src')
                except:
                    profile_data['candidate']['avatar'] = self.chrome.find_element_by_xpath(
                        "//div[contains(@class, 'presence-entity__image')]").value_of_css_property(
                        'background-image').split('"')[1]

            if "base64" in profile_data['candidate']['avatar']:
                    profile_data['candidate']['avatar'] = ""

            try:
                profile_data['candidate']['title'] = self.chrome.find_element_by_xpath("//h2[contains(@class, 'top-card-section__headline')]").text
            except:
                pass
            try:
                profile_data['candidate']['industry'] = self.chrome.find_element_by_xpath("//h3[contains(@class, 'top-card-section__company')]").text
            except:
                pass
            try:
                country_list = ["Albania","Algeria","Andorra","Angola","Antarctica","Antigua and Barbuda","Argentina","Armenia","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria","Burkina Faso","Burma","Burundi","Cambodia","Cameroon","Canada","Cape Verde","Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo, Democratic Republic","Congo, Republic of the","Costa Rica","Cote d'Ivoire","Croatia","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","East Timor","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Ethiopia","Fiji","Finland","France","Gabon","Gambia","Georgia","Germany","Ghana","Greece","Greenland","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Korea North","Korea South","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia","Moldova","Mongolia","Morocco","Monaco","Mozambique","Namibia","Nauru","Nepal","Netherlands","New Zealand","Nicaragua","Niger","Nigeria","Norway","Oman","Pakistan","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia","Russian Federation","Rwanda","Samoa","San Marino","Sao Tome","Saudi Arabia","Senegal","Serbia and Montenegro","Seychelles","Sierra Leone","Singapore","Slovak Republic","Slovenia","Solomon Islands","Somalia","South Africa","Spain","Sri Lanka","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Togo","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan","Vanuatu","Venezuela","Vietnam","Yemen","Zambia","Zimbabwe"]
                location = self.chrome.find_element_by_xpath("//h3[contains(@class, 'top-card-section__location')]").text
                location = location.replace(' Area', '')
                part = location.split(', ')
                if part[-1] in country_list:
                    profile_data['candidate']['country'] = location
            except:
                pass
            self.view.process_log("Parse - %s" % data['full_name'])
            try:
                self._click_see_more_button(css_selector='div[class*="top-card-section__summary"] button[aria-expanded="false"]')
                profile_data['candidate']['summary'] = self.chrome.find_element_by_xpath("//div[contains(@class, 'top-card-section__summary')]/p").text
            except:
                pass

            # Employments
            employments_json = {
                'title': None,
                'company': None,
                'start_date': None,
                'end_date': None,
                'location': None,
                'description': None

            }
            employments_list = []

            self._click_see_more_button(css_selector='section[class*="experience-section"] button[class*="see-more"]')
            # time.sleep(1)
            self._click_see_more_button(css_selector='section[class*="experience-section"] button[aria-expanded="false"]')
            # time.sleep(1)
            employments = self.chrome.find_elements_by_css_selector("section[class*='experience-section'] li")
            for employment in employments:
                self._scroll_to_element(employment)
                try:
                    employments_json['title'] = employment.find_element_by_css_selector("div[class*='entity__summary-info']>*:first-child ").text
                except:
                    continue
                try:
                    employments_json['company'] = employment.find_element_by_css_selector("div[class*='entity__summary-info']>*:nth-child(2)>span:nth-child(2)").text
                except:
                    pass
                try:
                    employments_json['start_date'] = re.split(u"\u2013", employment.find_element_by_css_selector("div[class*='entity__summary-info']>*:nth-child(3)>span:nth-child(2)").text)[0]
                except:
                    pass
                try:
                    employments_json['end_date'] = re.split(u"\u2013", employment.find_element_by_css_selector("div[class*='entity__summary-info']>*:nth-child(3)>span:nth-child(2)").text)[1]
                except:
                    pass
                try:
                    employments_json['location'] = employment.find_element_by_css_selector("div[class*='entity__summary-info']>*:nth-child(5)>span:nth-child(2)").text
                except:
                    pass
                try:
                    employments_json['description'] = employment.find_element_by_css_selector('div[class*="entity__extra-details"]>p').text
                except:
                    pass

                employments_list.append(employments_json.copy())
                employments_json.clear()
            profile_data['candidate']['employments'] = employments_list or None

            # Educations
            educations_json = {
                'name': None,
                'program': None,
                'start_date': None,
                'end_date': None,
                'description': None

            }
            educations_list = []

            self._click_see_more_button(css_selector='section[class*="education-section"] button[class*="see-more"]')
            time.sleep(0.5)
            educations = self.chrome.find_elements_by_css_selector("section[class*='education-section'] li")
            for education in educations:
                self._scroll_to_element(education)
                try:
                    educations_json['name'] = education.find_element_by_css_selector("div[class*='entity__degree-info']>*:first-child").text
                except:
                    pass
                try:
                    title_list = education.find_elements_by_css_selector("div[class*='entity__degree-info']> p")
                    educations_json['program'] = ' - '.join([(p.text).split('\n')[-1] for p in title_list])
                except:
                    pass
                try:
                    date_range = education.find_element_by_css_selector("p[class*='entity__dates']").text
                    date_range = re.findall('\d{4}',date_range)
                    educations_json['start_date'] = date_range[0]
                    educations_json['end_date'] = date_range[1]
                except:
                    pass

                try:
                    description_list = education.find_elements_by_css_selector("div[class*='entity__extra-details']>p")
                    educations_json['description'] = ''.join([str(d.text) for d in description_list])
                except:
                    pass

                educations_list.append(educations_json.copy())
                educations_json.clear()
            profile_data['candidate']['educations'] = educations_list or None

            self.view.process_log("Parse - %s" % data['full_name'])
            # Skills
            skills_list = []

            self._click_see_more_button(css_selector='section[class *="featured-skills-section"] button[aria-expanded = "false"]')

            skills = self.chrome.find_elements_by_css_selector('section[class *="featured-skills-section"] div[class *= "tooltip-container"] span[class *="skill-entity__skill-name"]')
            for skill in skills:
                skills_list.append(skill.text)
            profile_data['candidate']['skills'] = skills_list or None

            try:
                self._scroll_to_element('section[class *="pv-recommendations-section"]')
            except:
                pass

            # Awards
            self.chrome.execute_script("window.scrollTo(0,document.body.scrollHeight);")

            awards_json = {
                'title': None,
                'subtitle': None,
                'description': None
            }
            awards_list = []

            self._click_see_more_button(css_selector='section[class *= "pv-accomplishments-block honors"] button[data-control-name *= "expand"]')

            awards = self.chrome.find_elements_by_css_selector(
                'section[class *= "pv-accomplishments-block honors"] li')
            for award in awards:
                # self._scroll_to_element(language)
                awards_json['title'] = \
                (award.find_element_by_css_selector('[class*="entity__title"]').text).split('\n')[-1]
                try:
                    a = (award.find_element_by_css_selector('p > span[class*="pv-accomplishment-entity__date"]').text).split('\n')[-1]
                    b = (award.find_element_by_css_selector('p > span[class*="pv-accomplishment-entity__issuer"]').text).split('\n')[-1]
                    awards_json['subtitle'] = a + " - " + b
                except:
                    pass
                try:
                    awards_json['description'] = (award.find_element_by_css_selector('[class*="entity__description"]').text).split('\n')[-1]
                except:
                    pass
                awards_list.append(awards_json.copy())
                awards_json.clear()
            profile_data['candidate']['awards'] = awards_list or None

            # Languages
            languages_json = {
                'language': None,
                'level': None
            }
            languages_list = []

            self._click_see_more_button(css_selector='section[class *= "pv-accomplishments-block languages"] button[data-control-name *= "expand"]')
            time.sleep(1)
            self._click_see_more_button(css_selector='section[class *= "pv-accomplishments-block languages"] button[aria-expanded *= "false"]')

            languages = self.chrome.find_elements_by_css_selector('section[class *= "pv-accomplishments-block languages pv-accomplishments-block--expanded"] li')
            for language in languages:
                # self._scroll_to_element(language)
                languages_json['language'] = (language.find_element_by_css_selector('[class*="entity__title"]').text).split('\n')[-1]
                try:
                    languages_json['level'] = language.find_element_by_css_selector('p').text
                except:
                    pass
                languages_list.append(languages_json.copy())
                languages_json.clear()
            profile_data['candidate']['languages'] = languages_list or None

            # Courses
            courses_json = {
                'name': ''
            }
            courses_list = []
            self._click_see_more_button(
                css_selector='section[class *= "pv-accomplishments-block courses"] button[data-control-name *= "expand"]')
            self._click_see_more_button(
                css_selector='section[class *= "pv-accomplishments-block courses"] button[aria-expanded *= "false"]')
            courses = self.chrome.find_elements_by_css_selector(
                'section[class *= "pv-accomplishments-block courses"] li')
            for course in courses:
                self._scroll_to_element(course)
                try:
                    courses_json['name'] = (course.find_element_by_css_selector('[class*="entity__title"]').text).split('\n')[-1]
                    courses_list.append(courses_json.copy())
                    courses_json.clear()
                except:
                    pass
            profile_data['candidate']['courses'] = courses_list or None

            # Certifications
            certifications_json = {
                'name': None,
                'start_date': None,
                'end_date': None,
                'detail': None
            }
            certifications_list = []
            self._click_see_more_button(
                css_selector='section[class *= "pv-accomplishments-block certifications"] button[data-control-name *= "expand"]')
            self._click_see_more_button(
                css_selector='section[class *= "pv-accomplishments-block certifications"] button[aria-expanded *= "false"]')

            certifications = self.chrome.find_elements_by_css_selector(
                'section[class *= "pv-accomplishments-block certifications"] li')
            for certification in certifications:
                try:
                    certifications_json['name'] = ((certification.find_element_by_css_selector('[class*="entity__title"]').text).split('\n')[-1])
                except:
                    pass
                try:
                    certifications_json['start_date'] = (re.split(u"\u2013", (certification.find_element_by_css_selector("[class*='entity__date']").text.split('\n')[-1]))[0])
                    certifications_json['end_date'] = (re.split(u"\u2013", (certification.find_element_by_css_selector("[class*='entity__date']").text.split('\n')[-1]))[-1])
                except:
                    pass
                try:
                    certifications_json['detail'] = ((certification.find_element_by_css_selector("[data-control-name*='certification_detail_company']").text).split('\n')[-1])
                except:
                    pass
                certifications_list.append(certifications_json.copy())
                certifications_json.clear()
            profile_data['candidate']['certificates'] = certifications_list or None

            # Projects
            projects_json = {
                'title': None,
                'start_date': None,
                'end_date': None,
                'description': None
            }
            projects_list = []
            self._click_see_more_button(
                css_selector='section[class *= "pv-accomplishments-block projects"] button[data-control-name *= "expand"]')
            self._click_see_more_button(
                css_selector='section[class *= "pv-accomplishments-block projects"] button[aria-expanded *= "false"]')

            projects = self.chrome.find_elements_by_css_selector(
                'section[class *= "pv-accomplishments-block projects"] li')
            for project in projects:
                try:
                    projects_json['title'] = (
                    (project.find_element_by_css_selector('[class*="entity__title"]').text).split('\n')[-1])
                except:
                    pass
                try:
                    projects_json['start_date'] = (re.split(u"\u2013", (
                    project.find_element_by_css_selector("[class*='entity__date']").text.split('\n')[-1]))[0])
                    projects_json['end_date'] = (re.split(u"\u2013", (
                    project.find_element_by_css_selector("[class*='entity__date']").text.split('\n')[-1]))[-1])
                except:
                    pass
                try:
                    projects_json['description'] = (project.find_element_by_css_selector(
                        "[class*='entity__description']").text)
                except:
                    pass
                projects_list.append(projects_json.copy())
                projects_json.clear()
            profile_data['candidate']['projects'] = projects_list or None

            return profile_data
        except:
            pass

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

    def security_check(self):
        """Sometimes linkedin make auto logout. We check if this happen there."""
        if 'https://www.linkedin.com/m/login' in self.chrome.current_url or 'https://www.linkedin.com/authwall' in self.chrome.current_url or 'captcha-v2' in self.chrome.current_url:
            while 'https://www.linkedin.com/m/login' in self.chrome.current_url or 'https://www.linkedin.com/authwall' in self.chrome.current_url or 'captcha-v2' in self.chrome.current_url:
                self.view.process_log("Security problem. You need login manually")
                time.sleep(2)
            self.view.process_log("Try back to work...")
