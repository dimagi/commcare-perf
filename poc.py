import os
import yaml
from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    host = "https://staging.commcarehq.org"
    formplayer_host = "/formplayer"             # settings.FORMPLAYER_URL

    # TODO: Make API call for cases with owner_id
    case_ids = {'f890e903-d114-4017-8e46-16321ab81f46', '80a2e92c-9e90-4fbd-832f-d73fda2240c8'}

    def on_start(self):
        self._read_config()
        self._log_in()
        self._get_build_id()

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

    @task
    def home_screen(self):
        data = self._formplayer_post("navigate_menu_start")
        assert(data['title'] == 'Music')
        assert(len(data['commands']) == 7)

    @task
    def menu_list(self):
        data = self._navigate_menu(name="menu")
        assert(data['title'] == 'Music')
        assert(len(data['commands']) == 7)

    @task
    def case_list(self):
        data = self._navigate_menu([1], name="case list")    # click on second menu in main menu list
        assert(data['title'] == 'Update Song Ratings & Year')
        all(e['id'] in self.case_ids for e in data['entities'])

    @task
    def case_details(self):
        data = self._formplayer_post("get_details", extra_json={
            "selections": [2, next(iter(self.case_ids))],
        })
        assert(len(data['details']) == 4)   # 4 tabs in this detail

    @task
    def form_entry(self):
        data = self._navigate_menu([2, next(iter(self.case_ids))], name="form entry")
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
