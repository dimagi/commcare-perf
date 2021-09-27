import os
from glob import glob
from uuid import uuid4
from xml.etree import ElementTree as ET

from locust import HttpUser, between, task
from locust.exception import LocustError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
    def submit_forms(self):
        for filename in glob(os.sep.join((BASE_DIR, 'xforms', '*'))):
            xform_tree = ET.parse(filename)
            self._submit_xform_tree(xform_tree)

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

    def _submit_xform_tree(self, xform_tree: ET.ElementTree):
        set_instance_id(xform_tree)
        set_new_case_ids(xform_tree)
        url = f'/a/{self.domain}/receiver/{self.app_id}/'
        data = dump_xform_tree(xform_tree, 'utf-8')
        auth = (os.environ['CCHQ_USERNAME'], os.environ['CCHQ_PASSWORD'])
        headers = {'Content-Type': 'text/html; charset=UTF-8'}
        response = self.client.post(
            url, data, auth=auth, headers=headers,
            name='receiver',
        )
        assert 200 <= response.status_code < 300, response.text


def set_instance_id(xform_tree: ET.ElementTree):
    """
    Assign a different instance ID to prevent duplicate IDs.
    """
    ns = {'jrx': 'http://openrosa.org/jr/xforms'}
    instance_id = str(uuid4())
    instance_id_elem = xform_tree.find('./jrx:meta/jrx:instanceID', ns)
    if instance_id_elem is None:
        raise LocustError('XForm meta instanceID missing or bad namespace')
    instance_id_elem.text = instance_id


def set_new_case_ids(xform_tree: ET.ElementTree):
    """
    Assign a different ID to new cases to prevent duplicate IDs.
    """
    ns = {'tx': 'http://commcarehq.org/case/transaction/v2'}
    for case_elem in xform_tree.iterfind('./tx:case[tx:create]', ns):
        case_id = str(uuid4())
        case_elem.set('case_id', case_id)


def dump_xform_tree(xform_tree: ET.ElementTree, encoding=None):
    xform_root = xform_tree.getroot()
    return ET.tostring(xform_root, encoding, xml_declaration=True)
