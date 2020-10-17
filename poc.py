import os
import yaml

from collections import defaultdict
from locust import HttpUser, between, task
from lxml import etree


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    host = "https://staging.commcarehq.org"
    formplayer_host = "/formplayer"             # settings.FORMPLAYER_URL

    def on_start(self):
        self._read_config()
        self._log_in()
        self._get_build_id()
        self._restore()          # initial restore to populate self.patient_case_ids

    def _read_config(self):
        with open("config.yaml") as f:
            config = yaml.safe_load(f)
            self.domain = config['domain']
            self.login_as = config['login_as']
            self.app_id = config['app_id']
            self.username = os.environ.get('LOCUST_USERNAME')
            self.password = os.environ.get('LOCUST_PASSWORD')

    def _log_in(self):
        login_url = f'/a/{self.domain}/login/'
        response = self.client.get(login_url)
        response = self.client.post(
            login_url,
            {
                "auth-username": self.username,
                "auth-password": self.password,
                "cloud_care_login_view-current_step": ['auth'],     # fake out two_factor ManagementForm
            },
            headers={
                "X-CSRFToken": self.client.cookies.get('csrftoken'),
                "REFERER": f'{self.host}{login_url}',               # csrf requires this for secure requests
            },
        )
        assert(response.status_code == 200)
        assert('Sign In' not in response.text)  # make sure we weren't just redirected back to login

    def _get_build_id(self):
        response = self.client.get(f'/a/{self.domain}/cloudcare/apps/v2/?option=apps', name='Web Apps apps')
        assert(response.status_code == 200)
        build_id_map = {
            app['copy_of']: app['_id']
            for app in response.json()
        }
        assert(self.app_id in build_id_map)
        self.build_id = build_id_map[self.app_id]

    def _restore(self):
        url = f'/a/{self.domain}/phone/restore/{self.build_id}/?skip_fixtures=true'
        if self.login_as:
            url += f'&as={self.login_as}@{self.domain}.commcarehq.org'
        response = self.client.get(url, name='Restore')
        assert(response.status_code == 200)

        namespaces = {None: 'http://commcarehq.org/case/transaction/v2'}
        self.case_ids = defaultdict(set)
        root = etree.fromstring(response.text)
        for case in root.findall('case', namespaces=namespaces):
            case_type = case.findall('create/case_type', namespaces=namespaces)[0].text
            self.case_ids[case_type].add(case.attrib.get('case_id'))

    def _get_case_id(self, case_type):
        return next(iter(self.case_ids[case_type]))

    @task
    def home_screen(self):
        data = self._formplayer_post("navigate_menu_start", name="Start")
        assert(data['title'] == 'NY Communicable Disease Case Management System (NY-CDCMS)')
        assert(len(data['commands']) == 32)

    @task
    def case_list(self):
        # All Cases is the sixth command in the main menu
        data = self._navigate_menu([5], name="All Cases case list")
        assert(data['title'] == 'All Cases')
        assert(len(data['entities']))       # should return at least one case

    @task
    def case_details(self):
        # Select All Cases, then a case
        data = self._formplayer_post("get_details", name="Case Detail", extra_json={
            "selections": [5, self._get_case_id("patient")],
        })
        assert(len(data['details']) == 5)   # 5 tabs in this detail

    @task
    def form_entry(self):
        # Select All Cases, then a case, then second command is CI form
        data = self._navigate_menu([5, self._get_case_id("patient"), 2], name="CI Form")
        assert(data['title'] == 'Case Investigation')
        assert('instanceXml' in data)

    def _navigate_menu(self, selections=None, name=None):
        return self._formplayer_post("navigate_menu", extra_json={
            "selections": selections or [],
        }, name=name)

    def _formplayer_post(self, command, extra_json=None, name=None):
        json = {
            "app_id": self.build_id,
            "domain": self.domain,
            "locale": "en",
            "restoreAs": self.login_as,
            "username": self.username,
        }
        if extra_json:
            json.update(extra_json)
        name = name or command

        response = self.client.post(f"{self.formplayer_host}/{command}/", json=json, name=name)

        assert(response.status_code == 200)
        return response.json()
