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
    def web_apps(self):
        response = self.client.get(f'/a/{self.domain}/cloudcare/apps/v2/#{{"appId":"{self.build_id}"}}')
        assert(response.status_code == 200)
        assert('Show Full Menu' in response.text)

    @task
    def break_locks(self):
        response = self.client.post(
            self.formplayer_host + "/break_locks/",
            json={
                "domain": self.domain,
                "username": os.environ['LOCUST_USERNAME'],
                "restoreAs": None,    # TODO?
            },
            cookies=response.cookies,
        )
        assert(response.status_code == 200)
        assert(response.json()['type'] == 'success')
