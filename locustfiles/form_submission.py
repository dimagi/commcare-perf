import os
from uuid import uuid4

from locust import HttpUser, between, task


class MobileUser(HttpUser):
    wait_time = between(5, 15)

    def __init__(self, *args, **kwargs):
        self.username = os.environ['CCHQ_USERNAME']
        self.password = os.environ['CCHQ_PASSWORD']
        self.domain = os.environ['CCHQ_DOMAIN']
        self.app_id = os.environ['CCHQ_APP_ID']
        self.build_id = None
        super().__init__(*args, **kwargs)

    def on_start(self):
        self._log_in()
        self.build_id = self._get_build_id()

    @task
    def restore(self):
        url = (
            f'/a/{self.domain}/phone/restore/{self.build_id}/'
            f'?as={self.username}&skip_fixtures=true'
        )
        auth = (os.environ['CCHQ_USERNAME'], os.environ['CCHQ_PASSWORD'])
        response = self.client.get(url, auth=auth, name='restore')
        assert response.status_code == 200, response.text

    @task
    def submit_form(self):
        url = f'/a/{self.domain}/receiver/{self.app_id}/'
        instance_id = str(uuid4())
        data = xform.format(instance_id=instance_id).encode('utf-8')
        auth = (os.environ['CCHQ_USERNAME'], os.environ['CCHQ_PASSWORD'])
        headers = {'Content-Type': 'text/html; charset=UTF-8'}
        response = self.client.post(
            url, data, auth=auth, headers=headers,
            name='receiver',
        )
        assert 200 <= response.status_code < 300, response.text

    def _log_in(self):
        url = f'/a/{self.domain}/login/'
        self.client.get(url, name='login')
        data = {
            "auth-username": self.username,
            "auth-password": self.password,
            "cloud_care_login_view-current_step": ['auth'],
        }
        headers = {
            "X-CSRFToken": self.client.cookies.get('csrftoken'),
            # CSRF requires this for secure requests:
            "REFERER": f'{self.host}{url}',
        }
        response = self.client.post(url, data, headers=headers, name='login')
        assert response.status_code == 200, response.text
        # Make sure we weren't just redirected back to the login page
        assert 'Sign In' not in response.text

    def _get_build_id(self):
        url = f'/a/{self.domain}/cloudcare/apps/v2/?option=apps'
        response = self.client.get(url, name='apps')
        assert response.status_code == 200, response.text
        return next(
            app['_id'] for app in response.json()
            if app['copy_of'] == self.app_id
        )


xform = """<?xml version='1.0' ?>
<data xmlns:jrm="http://dev.commcarehq.org/jr/xforms"
      xmlns="https://www.commcarehq.org/test/LocustPerfTesting/">
    <foo/>
    <bar/>
    <meta>
        <deviceID>LocustPerfTesting</deviceID>
        <timeStart>2011-10-01T15:25:18.404-04</timeStart>
        <timeEnd>2011-10-01T15:26:29.551-04</timeEnd>
        <username>admin</username>
        <userID>testy.mctestface</userID>
        <instanceID>{instance_id}</instanceID>
    </meta>
</data>
"""
