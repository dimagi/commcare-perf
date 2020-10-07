import os
from locust import HttpUser, between, task


# env LOCUST_USERNAME=$LOCUST_USERNAME env LOCUST_PASSWORD=$LOCUST_PASSWORD locust -f poc.py --headless -u 1 -r 1
class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    # TODO: external config files for different environments?
    #host = "https://staging.commcarehq.org"
    host = "http://localhost:8000"

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
    def dashboard(self):
        response = self.client.get("/a/bosco/dashboard/project/")
        assert(response.status_code == 200)
        assert('fcc-reports' in response.text)
