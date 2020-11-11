import logging
import os
import yaml
import random
import csv
import json

from collections import defaultdict
from locust import HttpUser, TaskSet, SequentialTaskSet, between, task, tag
from lxml import etree

class WorkloadModelSteps(TaskSet):
    def on_start(self):
        ## get domain user credential and app config info
        with open(self.user.app_config) as json_file:
            data = json.load(json_file)
            self.SEARCH_NAMES=data['SEARCH_NAMES']
            self.FUNC_USER_CHECK_IN_FORM=data['FUNC_USER_CHECK_IN_FORM']
            self.FUNC_USER_CHECK_IN=data['FUNC_USER_CHECK_IN']
            self.FUNC_HOME_SCREEN=data['FUNC_HOME_SCREEN']
            self.FUNC_CASE_LIST=data['FUNC_CASE_LIST']
            self.FUNC_CASE_DETAILS=data['FUNC_CASE_DETAILS']
            self.FUNC_FORM_ENTRY=data['FUNC_FORM_ENTRY']
            self.FUNC_CASE_CLAIM_SEARCH=data['FUNC_CASE_CLAIM_SEARCH']
            self.FUNC_OMNI_SEARCH=data['FUNC_OMNI_SEARCH']
        self._log_in()
        self._get_build_info()
        self._get_caselist_filter()
        self._get_caselist_ids()
        self._user_check_in_form()
        if self.session_id:      # if session_id isn't empty, do user check in
            self._user_check_in()


    def _log_in(self):
        logging.info("_log_in")
        login_url = f'/a/{self.user.domain}/login/'
        response = self.client.get(login_url)
        response = self.client.post(
            login_url,
            {
                "auth-username": self.user.username,
                "auth-password": self.user.password,
                "cloud_care_login_view-current_step": ['auth'],     # fake out two_factor ManagementForm
            },
            headers={
                "X-CSRFToken": self.client.cookies.get('csrftoken'),
                "REFERER": f'{self.user.host}{login_url}',               # csrf requires this for secure requests
            },
        )
        assert(response.status_code == 200)
        assert('Sign In' not in response.text)  # make sure we weren't just redirected back to login


    def _get_build_info(self):
        logging.info("_get_build_id")
        response = self.client.get(f'/a/{self.user.domain}/cloudcare/apps/v2/?option=apps', name='Web Apps apps')
        assert(response.status_code == 200)
        for app in response.json():
            if app['copy_of']==self.user.app_id:
                # get build_id
                self.build_id = app['_id']
                # get All_Cases module info
                for module in app['modules']:
                    if module['name']['en']=="All Cases":
                        self.all_cases_module=module
                        #print("module--->"+str(module))
        #build_id_map = {
        #    app['copy_of']: app['_id']
        #    for app in response.json()
        #}
        #assert(self.user.app_id in build_id_map)
        #self.build_id = build_id_map[self.user.app_id]


    def _get_caselist_filter(self):
        logging.info("_get_filter")
        #print("==>>"+str(self.all_cases_module['case_details']['short']['filter']))
        local_filter=str(self.all_cases_module['case_details']['short']['filter'])
        local_filter=local_filter.replace(" ", "%20")
        local_filter=local_filter.replace("!", "%21")
        local_filter=local_filter.replace("=", "%3D")
        local_filter=local_filter.replace("'", "%22")
        local_filter=local_filter.replace("(", "%28")
        local_filter=local_filter.replace(")", "%29")
        self.all_cases_filter=local_filter
        #print("here::::=="+self.all_cases_filter)


    def _get_caselist_ids(self):
        logging.info("_get_caselist_ids")
        url = f'/a/{self.user.domain}/phone/search/?case_type={self.user.case_type}&owner_id={self.user.owner_id}&_xpath_query={self.all_cases_filter}'
        #print("url-->"+url)
        response = self.client.get(url, name='Get Caselist Ids')
        assert(response.status_code == 200)

        case_ids=[]
        root = etree.fromstring(response.text)
        for case in root.findall('case'):
            #print("case==>>"+case.attrib.get('case_id'))
            case_ids.append(case.attrib.get('case_id'))
        self.case_ids_patient = iter(case_ids)


    def _get_case_id_patient(self):
        #return random.choice(self.case_ids_patient)
        return next(self.case_ids_patient)


    def _user_check_in_form(self):
        logging.info("_user_check_in_form")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_USER_CHECK_IN_FORM['selections']],
        }, name="User CheckIn Form")
        try:
            self.session_id=data['session_id']
            logging.info("_user_check_in_form::sessionId::"+self.session_id)
        except (IndexError, KeyError, TypeError):
            self.session_id=''
            logging.info("_user_check_in_form::sessionId empty - skip check in")
        if self.session_id:
            assert(data['title'] == self.FUNC_USER_CHECK_IN_FORM['title1'])
        else:
            assert(data['title'] == self.FUNC_USER_CHECK_IN_FORM['title2'])
        """
        if self.session_id:
            assert(data['title'] == 'Check In')
        else :
            assert(data['title'] == 'Proceed to Check Out')
        """


    def _user_check_in(self):
        logging.info("_user_check_in")
        """
        data = self._formplayer_post("submit-all", extra_json={
            "answers": {4: [1]},
            "prevalidated": True,
            "debuggerEnabled": True,
            "session_id":self.session_id,
        }, name="User CheckIn")
        logging.info("_user_check_in")
        assert(data['submitResponseMessage'] == 'Form successfully saved!')
        """
        data = self._formplayer_post("submit-all", extra_json={
            "answers": {self.FUNC_USER_CHECK_IN['answers-key']: [self.FUNC_USER_CHECK_IN['answers-value']]},
            "prevalidated": True,
            "debuggerEnabled": True,
            "session_id":self.session_id,
        }, name="User CheckIn")
        assert(data['submitResponseMessage'] == self.FUNC_USER_CHECK_IN['submitResponseMessage'])


    @tag('all')
    @task
    def home_screen(self):
        logging.info("home_screen")
        data = self._formplayer_post("navigate_menu_start", name="Start", checkKey="title", checkValue=self.FUNC_HOME_SCREEN['title'])
        assert(data['title'] == self.FUNC_HOME_SCREEN['title'])
        #assert(len(data['commands']) == 41)


    @tag('all')
    @task
    def case_list(self):
        # All Cases is the sixth command in the main menu
        logging.info("case_list")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_CASE_LIST['selections']],
        }, name="All Cases case list", checkKey="title", checkValue=self.FUNC_CASE_LIST['title'])
        #data = self._navigate_menu([5], name="All Cases case list")
        assert(data['title'] == self.FUNC_CASE_LIST['title'])
        assert(len(data['entities']))       # should return at least one case


    @tag('all', 'form-entry', 'test')
    @task
    class FormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # Select All Cases, then a case
            self.local_case_id=self.parent._get_case_id_patient()
            logging.info("case_details::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.FUNC_CASE_DETAILS['selections'], self.local_case_id],
            }, name="Case Detail", checkKey=self.parent.FUNC_CASE_DETAILS['checkKey'], checkLen=self.parent.FUNC_CASE_DETAILS['checkLen'])
            assert(len(data['details']) == self.parent.FUNC_CASE_DETAILS['checkLen'])


        @task
        def form_entry(self):
            # Select All Cases, then a case, then second command is CI form
            logging.info("form_entry::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.FUNC_FORM_ENTRY['selections'], self.local_case_id, 2],
            }, name="CI Form", checkKey="title", checkValue=self.parent.FUNC_FORM_ENTRY['title'])
            #data = self._navigate_menu([5, local_case_id, 2], name="CI Form")
            assert(data['title'] == self.parent.FUNC_FORM_ENTRY['title'])
            assert('instanceXml' in data)


    @tag('all', 'search')
    @task
    def case_claim_search(self):
        # TEsting Module 3 - exclude active :: Search All Cases
        logging.info("case_claim_search")
        #names = ["Aki", "Graham", "Samic", "Jet", "Petty", "Knack", "Elle", "Leer" ]
        #search_value = random.choice(names)
        search_value = random.choice(self.SEARCH_NAMES)
        logging.info("case_claim_search::search_term::"+search_value)

        data = self._formplayer_post("navigate_menu", extra_json={
            "selections" : [self.FUNC_CASE_CLAIM_SEARCH['selections'], "action 0"],
            "query_dictionary" : {"name" : search_value}},
            name="Case Claim Search", checkKey="title", checkValue=self.FUNC_CASE_CLAIM_SEARCH['title'])
        assert(data["title"] == self.FUNC_CASE_CLAIM_SEARCH['title'])


    @tag('all', 'search')
    @task
    def omni_search(self):
        # All Case :: Omni Search
        logging.info("omni_search")
        #names = ["Aki", "Graham", "Samic", "Jet", "Petty", "Knack", "Elle", "Leer" ]
        #search_value = random.choice(names)
        search_value = random.choice(self.SEARCH_NAMES)
        logging.info("omni_search::search_term::"+search_value)

        data = self._formplayer_post("navigate_menu", extra_json={
            "selections" : [self.FUNC_OMNI_SEARCH['selections']],
            "search_text" : search_value},
            name="OMNI Search", checkKey="title", checkValue=self.FUNC_OMNI_SEARCH['title'])
        assert(data["title"] == self.FUNC_OMNI_SEARCH['title'])


    def _formplayer_post(self, command, extra_json=None, name=None, checkKey=None, checkValue=None, checkLen=None, checkList=None):
        json = {
            "app_id": self.build_id,
            "domain": self.user.domain,
            "locale": "en",
            "restoreAs": self.user.login_as,
            "username": self.user.username,
        }
        if extra_json:
            json.update(extra_json)
        name = name or command

        with self.client.post(f"{self.user.formplayer_host}/{command}/", json=json, name=name, catch_response=True) as response:
            data=response.json()
            #print("data-->"+str(data))
            #for check in checkList:
            #    check()
            if ("\"exception\"" in data):
                logging.info("exception error")
                response.failure("exception error")
            elif (checkKey and checkKey not in data):
                logging.info("error::"+checkKey+" not in data")
                response.failure("error::"+checkKey+" not in data")
            elif (checkKey and checkLen):
                if (len(data[checkKey]) != checkLen):
                    logging.info("error::len(data['"+checkKey+"']) != "+checkLen)
                    response.failure("error::len(data['"+checkKey+"']) != "+checkLen)
            elif (checkKey and checkValue):
                if (data[checkKey] != checkValue):
                    logging.info("error::data['"+checkKey+"'] != "+checkValue)
                    response.failure("error::data['"+checkKey+"'] != "+checkValue)
        return response.json()


class LoginCommCareHQWithUniqueUsers(HttpUser):
    tasks= [WorkloadModelSteps]
    wait_time = between(15, 30)
    formplayer_host = "/formplayer" 

    with open("config.yaml") as f:
        config = yaml.safe_load(f)
        host = config['host']
        domain = config['domain']
        app_id = config['app_id']
        domain_user_credential = config['domain_user_credential']
        app_config = config['app_config']
        owner_id = config['owner_id']
        case_type = config['case_type']

    ## get domain user credential and app config info
    with open(domain_user_credential) as json_file:
        data = json.load(json_file)
        data_user=data['user']


    def on_start(self):
        user_info=self.data_user.pop()
        self.username=user_info['username']
        self.password=user_info['password']
        self.login_as=user_info['login_as']
        #print("userinfo===>>"+str(user_info))

        logging.info("host-->>>"+self.host)
        logging.info("login_as-->>>"+self.login_as)

