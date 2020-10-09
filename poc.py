import os
from locust import HttpUser, between, task


# env LOCUST_USERNAME=$LOCUST_USERNAME env LOCUST_PASSWORD=$LOCUST_PASSWORD locust -f poc.py --headless -u 1 -r 1
class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    # TODO: external config files for different environments?
    #host = "https://staging.commcarehq.org"
    #formplayer_host = "/formplayer"
    #build_id = "33786ebd596943688cfee14b486cc85f"

    host = "http://localhost:8000"
    formplayer_host = "http://localhost:8080"
    build_id = "8eedfbd8a2ec4ab6babfcbfc44366019"

    domain = "bosco"

    # TODO: Make API call for cases with owner_id
    case_ids = {'f890e903-d114-4017-8e46-16321ab81f46', '80a2e92c-9e90-4fbd-832f-d73fda2240c8'}

    def on_start(self):
        response = self.client.get(f'/a/{self.domain}/login/')   # get cookies
        response = self.client.post(
            f'/a/{self.domain}/login/',
            {
                "auth-username": os.environ['LOCUST_USERNAME'],
                "auth-password": os.environ['LOCUST_PASSWORD'],
                "cloud_care_login_view-current_step": ['auth'],     # fake out two_factor ManagementForm
            },
            headers={"X-CSRFToken": response.cookies.get('csrftoken')}
        )
        assert(response.status_code == 200)
        assert('Sign In' not in response.text)  # make sure we weren't just redirected back to login

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
            "username": os.environ['LOCUST_USERNAME'],
        }
        if extra_json:
            json.update(extra_json)
        name = name or command

        response = self.client.post(f"{self.formplayer_host}/{command}/", json=json, name=name)

        assert(response.status_code == 200)
        return response.json()
