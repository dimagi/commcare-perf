from locust import HttpUser, between, task


# env LOCUST_USERNAME=$LOCUST_USERNAME env LOCUST_PASSWORD=$LOCUST_PASSWORD locust -f poc.py --headless -u 1 -r 1
class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    # TODO: external config files for different environments?
    #host = "https://staging.commcarehq.org"
    host = "http://localhost:8000"

    @task
    def style(self):
        response = self.client.get("/styleguide/")
        assert(response.status_code == 200)
