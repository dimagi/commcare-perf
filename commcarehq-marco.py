import logging
import os
import yaml
import random
import csv
import json

from collections import defaultdict
from locust import HttpUser, TaskSet, SequentialTaskSet, between, task, tag
from lxml import etree
from datetime import datetime

class WorkloadModelSteps(TaskSet):
    def on_start(self, x=0):
        ## get domain user credential and app config info
        with open(self.user.app_config) as json_file:
            data = json.load(json_file)
            self.MOD_SKIP=data['MOD_SKIP']
            self.CASES_LIST_FILTER=data['CASES_LIST_FILTER']
            self.SEARCH_NAMES=data['SEARCH_NAMES']
            self.FUNC_USER_CHECK_OUT_FORM=data['FUNC_USER_CHECK_OUT_FORM']
            self.FUNC_USER_CHECK_IN_FORM=data['FUNC_USER_CHECK_IN_FORM']
            self.FUNC_USER_CHECK_IN=data['FUNC_USER_CHECK_IN']
            self.FUNC_HOME_SCREEN=data['FUNC_HOME_SCREEN']
            self.FUNC_ALL_CASES_CASE_LIST=data['FUNC_ALL_CASES_CASE_LIST']
            self.FUNC_ALL_OPEN_CASES_CASE_LIST=data['FUNC_ALL_OPEN_CASES_CASE_LIST']
            self.FUNC_ALL_CLOSED_CASES_CASE_LIST=data['FUNC_ALL_CLOSED_CASES_CASE_LIST']
            if 'FUNC_ALL_CONTACTS_CASE_LIST' in data:
                self.FUNC_ALL_CONTACTS_CASE_LIST=data['FUNC_ALL_CONTACTS_CASE_LIST']
            if 'FUNC_ALL_OPEN_CONTACTS_CASE_LIST' in data: 
                self.FUNC_ALL_OPEN_CONTACTS_CASE_LIST=data['FUNC_ALL_OPEN_CONTACTS_CASE_LIST']
            if 'FUNC_ALL_CLOSED_CONTACTS_CASE_LIST' in data: 
                self.FUNC_ALL_CLOSED_CONTACTS_CASE_LIST=data['FUNC_ALL_CLOSED_CONTACTS_CASE_LIST']
            self.FUNC_CASE_DETAILS=data['FUNC_CASE_DETAILS']
            self.FUNC_CI_FORM=data['FUNC_CI_FORM']
            self.FUNC_PART_OF_CLUSTER=data['FUNC_PART_OF_CLUSTER']
            self.FUNC_HOSPITALIZED=data['FUNC_HOSPITALIZED']
            self.FUNC_HOSPITAL_NAME=data['FUNC_HOSPITAL_NAME']
            self.FUNC_CI_FORM_SUBMIT=data['FUNC_CI_FORM_SUBMIT']
            if 'FUNC_CM_CASE_DETAILS' in data: 
                self.FUNC_CM_CASE_DETAILS=data['FUNC_CM_CASE_DETAILS']
            if 'FUNC_CM_FORM' in data: 
                self.FUNC_CM_FORM=data['FUNC_CM_FORM']
            if 'FUNC_VIEW_UPDATE_CONTACT_INFO' in data: 
                self.FUNC_VIEW_UPDATE_CONTACT_INFO=data['FUNC_VIEW_UPDATE_CONTACT_INFO']
                self.FUNC_VIEW_UPDATE_CONTACT_INF_SKIP=False
            else:
                self.FUNC_VIEW_UPDATE_CONTACT_INF_SKIP=True
            if 'FUNC_INVALID_PHONE_NUMBER' in data: 
                self.FUNC_INVALID_PHONE_NUMBER=data['FUNC_INVALID_PHONE_NUMBER']
            if 'FUNC_PROVIDER_NAME' in data: 
                self.FUNC_PROVIDER_NAME=data['FUNC_PROVIDER_NAME']
            if 'FUNC_CM_FORM_SUBMIT' in data: 
                self.FUNC_CM_FORM_SUBMIT=data['FUNC_CM_FORM_SUBMIT']
            self.FUNC_ID_FORM=data['FUNC_ID_FORM']
            self.FUNC_ALTERNATE_PHONE_NUMBER=data['FUNC_ALTERNATE_PHONE_NUMBER']
            self.FUNC_ALTERNATE_PHONE_NUMBER_ENTER=data['FUNC_ALTERNATE_PHONE_NUMBER_ENTER']
            self.FUNC_ID_FORM_SUBMIT=data['FUNC_ID_FORM_SUBMIT']
            self.FUNC_RNC_FORM=data['FUNC_RNC_FORM']
            if 'FUNC_RNC_TOTAL_NUM_PEOPLE' in data:
                self.FUNC_RNC_TOTAL_NUM_PEOPLE=data['FUNC_RNC_TOTAL_NUM_PEOPLE']
            self.FUNC_RNC_FIRST_NAME=data['FUNC_RNC_FIRST_NAME']
            self.FUNC_RNC_LAST_NAME=data['FUNC_RNC_LAST_NAME']
            self.FUNC_RNC_SCHOOL_SETTING=data['FUNC_RNC_SCHOOL_SETTING']
            self.FUNC_RNC_SCHOOL_PREK=data['FUNC_RNC_SCHOOL_PREK']
            self.FUNC_RNC_COLLEGE_UNIVERSITY=data['FUNC_RNC_COLLEGE_UNIVERSITY']
            self.FUNC_RNC_NAME_OF_SCHOOL=data['FUNC_RNC_NAME_OF_SCHOOL']
            self.FUNC_RNC_NAME_OF_UNIVERSITY=data['FUNC_RNC_NAME_OF_UNIVERSITY']
            self.FUNC_RNC_PREFERRED_LANGUAGE=data['FUNC_RNC_PREFERRED_LANGUAGE']
            self.FUNC_RNC_LAST_DATE_TEST=data['FUNC_RNC_LAST_DATE_TEST']
            self.FUNC_RNC_FORM_SUBMIT=data['FUNC_RNC_FORM_SUBMIT']
            self.FUNC_CASE_CLAIM_SEARCH=data['FUNC_CASE_CLAIM_SEARCH']
            self.FUNC_OMNI_SEARCH=data['FUNC_OMNI_SEARCH']
            self.FUNC_NEW_SEARCH_ALL_CASES_FORM=data['FUNC_NEW_SEARCH_ALL_CASES_FORM']
            self.FUNC_NEW_SEARCH_ALL_CASES=data['FUNC_NEW_SEARCH_ALL_CASES']
            self.FUNC_NEW_SEARCH_ALL_CONTACTS_FORM=data['FUNC_NEW_SEARCH_ALL_CONTACTS_FORM']
            self.FUNC_NEW_SEARCH_ALL_CONTACTS=data['FUNC_NEW_SEARCH_ALL_CONTACTS']
            self.FUNC_BU_CONTACTS_FORM=data['FUNC_BU_CONTACTS_FORM']
            if 'FUNC_BU_CONTACTS_TYPE_OF_BULK' in data:
                self.FUNC_BU_CONTACTS_TYPE_OF_BULK=data['FUNC_BU_CONTACTS_TYPE_OF_BULK']
            if 'FUNC_BU_SELECT_WITHOUT_PRIMARY' in data:
                self.FUNC_BU_SELECT_WITHOUT_PRIMARY=data['FUNC_BU_SELECT_WITHOUT_PRIMARY']
                self.FUNC_BU_SELECT_WITHOUT_PRIMARY_SKIP=False
            else:
                self.FUNC_BU_SELECT_WITHOUT_PRIMARY_SKIP=True
            self.FUNC_BU_CONTACTS_MATCHING=data['FUNC_BU_CONTACTS_MATCHING']
            if 'FUNC_BU_CONTACTS_ASSIGN_ACTION' in data:
                self.FUNC_BU_CONTACTS_ASSIGN_ACTION=data['FUNC_BU_CONTACTS_ASSIGN_ACTION']
            if 'FUNC_BU_CONTACTS_SELECT_OWNER' in data:
                self.FUNC_BU_CONTACTS_SELECT_OWNER=data['FUNC_BU_CONTACTS_SELECT_OWNER']
                self.FUNC_BU_CONTACTS_SELECT_OWNER_SKIP=False
            else:
                self.FUNC_BU_CONTACTS_SELECT_OWNER_SKIP=True
            if 'FUNC_BU_UPDATE_FEWER_CONTACTS' in data:
                self.FUNC_BU_UPDATE_FEWER_CONTACTS=data['FUNC_BU_UPDATE_FEWER_CONTACTS']
            self.FUNC_BU_NUMBER_OF_UPDATES=data['FUNC_BU_NUMBER_OF_UPDATES']
            self.FUNC_BU_CONTACTS_FORM_SUBMIT=data['FUNC_BU_CONTACTS_FORM_SUBMIT']
            self.FUNC_UPDATE_CONTACTS_FORM_SUBMIT=data['FUNC_UPDATE_CONTACTS_FORM_SUBMIT']
            if 'FUNC_BU_CASES_FORM' in data:
                self.FUNC_BU_CASES_FORM=data['FUNC_BU_CASES_FORM']
            if 'FUNC_BU_CASES_TYPE_OF_BULK' in data:
                self.FUNC_BU_CASES_TYPE_OF_BULK=data['FUNC_BU_CASES_TYPE_OF_BULK']
            if 'FUNC_BU_CASES_UNCHECK_OPEN_CASES' in data:
                self.FUNC_BU_CASES_UNCHECK_OPEN_CASES=data['FUNC_BU_CASES_UNCHECK_OPEN_CASES']
            if 'FUNC_BU_CASES_UNCHECK_VALID_PHONE' in data:
                self.FUNC_BU_CASES_UNCHECK_VALID_PHONE=data['FUNC_BU_CASES_UNCHECK_VALID_PHONE']
            if 'FUNC_BU_CASES_UNCHECK_CONFIRMED_CASES' in data:
                self.FUNC_BU_CASES_UNCHECK_CONFIRMED_CASES=data['FUNC_BU_CASES_UNCHECK_CONFIRMED_CASES']
            if 'FUNC_BU_CASES_UNCHECK_INITIAL_INTERVIEW' in data:
                self.FUNC_BU_CASES_UNCHECK_INITIAL_INTERVIEW=data['FUNC_BU_CASES_UNCHECK_INITIAL_INTERVIEW']
            if 'FUNC_BU_CASES_UNCHECK_PRIMARY_OWNER' in data:
                self.FUNC_BU_CASES_UNCHECK_PRIMARY_OWNER=data['FUNC_BU_CASES_UNCHECK_PRIMARY_OWNER']
            if 'FUNC_BU_CASES_MATCHING' in data:
                self.FUNC_BU_CASES_MATCHING=data['FUNC_BU_CASES_MATCHING']
            if 'FUNC_BU_CASES_ASSIGN_PRIMARY' in data:
                self.FUNC_BU_CASES_ASSIGN_PRIMARY=data['FUNC_BU_CASES_ASSIGN_PRIMARY']
            if 'FUNC_BU_CASES_SELECT_OWNER' in data:
                self.FUNC_BU_CASES_SELECT_OWNER=data['FUNC_BU_CASES_SELECT_OWNER']
            if 'FUNC_BU_CASES_UPDATE_FEWER_CASES' in data:
                self.FUNC_BU_CASES_UPDATE_FEWER_CASES=data['FUNC_BU_CASES_UPDATE_FEWER_CASES']
            if 'FUNC_BU_CASES_NUMBER_OF_UPDATES' in data:
                self.FUNC_BU_CASES_NUMBER_OF_UPDATES=data['FUNC_BU_CASES_NUMBER_OF_UPDATES']
            if 'FUNC_BU_CASES_FORM_SUBMIT' in data:
                self.FUNC_BU_CASES_FORM_SUBMIT=data['FUNC_BU_CASES_FORM_SUBMIT']
            if 'FUNC_UPDATE_CASES_FORM_SUBMIT' in data:
                self.FUNC_UPDATE_CASES_FORM_SUBMIT=data['FUNC_UPDATE_CASES_FORM_SUBMIT']
        self._log_in()
        self._get_build_info()
        if not self.MOD_SKIP['get_all_cases_info']:
            self._get_all_cases_info()
        if not self.MOD_SKIP['get_all_cases_info']:
            self._get_all_cases_filter()
        if not self.MOD_SKIP['get_all_cases_info']:
            self._get_all_cases_ids()
        if not self.MOD_SKIP['get_all_contacts_info']:
            self._get_all_contacts_filter()
        if not self.MOD_SKIP['get_all_contacts_info']:
            self._get_all_contacts_ids()
        if not self.MOD_SKIP['check_out_form']:
            self._user_check_out_form()


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
        logging.info("_get_build_info")
        response = self.client.get(f'/a/{self.user.domain}/cloudcare/apps/v2/?option=apps', name='build info')
        assert(response.status_code == 200)
        for app in response.json():
            if app['copy_of']==self.user.app_id:
                # get build_id
                self.build_id = app['_id']
        logging.info("build_id: "+self.build_id)


    def _get_all_cases_info(self):
        logging.info("_get_all_cases_info")
        ##ex: https://staging.commcarehq.org/a/us-covid-performance/apps/source/765b9d4c97d149b3859f86c229872f97/
        #logging.info("url-->/a/"+self.user.domain+"/apps/source/"+self.user.app_id)
        response = self.client.get(f'/a/{self.user.domain}/apps/source/{self.user.app_id}/', name='all cases info')
        assert(response.status_code == 200)
        data=response.json()
        modules=data['modules']
        for module in modules:
            #logging.info("module--->"+str(module))
            # get All_Cases module info
            self.all_cases_module={}
            if module['name']['en']=="All Cases":
                #logging.info("all_cases--->"+str(module))
                self.all_cases_module=module


    def _get_all_cases_filter(self):
        logging.info("_get_all_cases_filter")
        local_filter=self.CASES_LIST_FILTER['all_cases_filter'] if self.CASES_LIST_FILTER['all_cases_filter']!='' else str(self.all_cases_module['case_details']['short']['filter'])
        logging.info("all cases filter: "+local_filter)
        #local_filter=str(self.all_cases_module['case_details']['short']['filter'])
        local_filter=local_filter.replace(" ", "%20")
        local_filter=local_filter.replace("!", "%21")
        local_filter=local_filter.replace("=", "%3D")
        local_filter=local_filter.replace("'", "%22")
        local_filter=local_filter.replace("(", "%28")
        local_filter=local_filter.replace(")", "%29")
        local_filter=local_filter.replace("<", "%3C")
        local_filter=local_filter.replace(">", "%3E")
        local_filter=local_filter.replace("\n","%20")
        local_filter=local_filter.replace("\r","%20")
        self.all_cases_filter=local_filter
        #print("here::::=="+self.all_cases_filter)


    def _get_all_cases_ids(self):
        logging.info("_get_all_cases_ids")
        url = f'/a/{self.user.domain}/phone/search/?case_type={self.user.case_type}&owner_id={self.user.owner_id}&_xpath_query={self.all_cases_filter}'
        #logging.info("url-->"+url)
        response = self.client.get(url, name='get all cases ids')
        assert(response.status_code == 200)

        case_ids=[]
        root = etree.fromstring(response.text)
        for case in root.findall('case'):
            #logging.info("case==>>"+case.attrib.get('case_id'))
            case_ids.append(case.attrib.get('case_id'))
        self.case_ids_patient = iter(case_ids)


    def _get_case_id_patient(self):
        #return random.choice(self.case_ids_patient)
        return next(self.case_ids_patient)


    def _get_all_contacts_filter(self):
        logging.info("_get_all_contacts_filter")
        local_filter=self.CASES_LIST_FILTER['all_contacts_filter']
        logging.info("all contacts filter: "+local_filter)
        local_filter=local_filter.replace(" ", "%20")
        local_filter=local_filter.replace("!", "%21")
        local_filter=local_filter.replace("=", "%3D")
        local_filter=local_filter.replace("'", "%22")
        local_filter=local_filter.replace("(", "%28")
        local_filter=local_filter.replace(")", "%29")
        local_filter=local_filter.replace("<", "%3C")
        local_filter=local_filter.replace(">", "%3E")
        local_filter=local_filter.replace("\n","%20")
        local_filter=local_filter.replace("\r","%20")
        self.all_contacts_filter=local_filter


    def _get_all_contacts_ids(self):
        logging.info("_get_all_contacts_ids")
        url = f'/a/{self.user.domain}/phone/search/?case_type=contact&owner_id={self.user.owner_id}&_xpath_query={self.all_contacts_filter}'
        #logging.info("url-->"+url)
        response = self.client.get(url, name='get all contacts ids')
        assert(response.status_code == 200)

        case_ids=[]
        root = etree.fromstring(response.text)
        for case in root.findall('case'):
            #logging.info("case==>>"+case.attrib.get('case_id'))
            case_ids.append(case.attrib.get('case_id'))
        self.case_ids_contact = iter(case_ids)


    def _get_case_id_contact(self):
        #return random.choice(self.case_ids_contact)
        return next(self.case_ids_contact)


    def _user_check_out_form(self):
        logging.info("_user_check_out_form")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_USER_CHECK_OUT_FORM['selections']],
        }, name="User CheckOut Form")
        ###logging.info("data--->>>>>"+str(data))
        if data['title']!=self.FUNC_USER_CHECK_OUT_FORM['title']:
            self._user_check_in_form()


    def _user_check_in_form(self):
        logging.info("_user_check_in_form")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_USER_CHECK_IN_FORM['selections']],
        }, name="User CheckIn Form")
        self.session_id=data['session_id']
        self._user_check_in()
        """
        try:
            self.session_id=data['session_id']
            logging.info("_user_check_in_form::sessionId::"+self.session_id)
        except (IndexError, KeyError, TypeError):
            self.session_id=''
            logging.info("_user_check_in_form::sessionId empty - skip check in")
        assert(data['title'] == self.FUNC_USER_CHECK_IN_FORM['title'])
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


    @tag('all', 'home_screen')
    @task(6)
    def home_screen(self):
        logging.info("home_screen")
        data = self._formplayer_post("navigate_menu_start", name="Home Screen", checkKey="title", checkValue=self.FUNC_HOME_SCREEN['title'])
        assert(data['title'] == self.FUNC_HOME_SCREEN['title'])
        #assert(len(data['commands']) == 41)


    @tag('all', 'all_cases_case_list')
    @task(6)
    def all_cases_case_list(self):
        logging.info("all_cases_case_list")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_ALL_CASES_CASE_LIST['selections']],
        }, name="All Cases Case List", checkKey="title", checkValue=self.FUNC_ALL_CASES_CASE_LIST['title'])
        #data = self._navigate_menu([5], name="All Cases case list")
        ##logging.info("===>>>>>>>>>"+str(data))
        assert(data['title'] == self.FUNC_ALL_CASES_CASE_LIST['title'])
        assert(len(data['entities']))       # should return at least one case


    @tag('all', 'all_open_cases_case_list', 'cal_test')
    @task(6)
    def all_open_cases_case_list(self):
        logging.info("all_open_cases_case_list")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_ALL_OPEN_CASES_CASE_LIST['selections']],
        }, name="All Open Cases Case List", checkKey="title", checkValue=self.FUNC_ALL_OPEN_CASES_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_OPEN_CASES_CASE_LIST['title'])
        assert(len(data['entities']))       # should return at least one case


    @tag('all', 'all_closed_cases_case_list', 'cal_test')
    @task(6)
    def all_closed_cases_case_list(self):
        logging.info("all_closed_cases_case_list")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_ALL_CLOSED_CASES_CASE_LIST['selections']],
        }, name="All Closed Cases Case List", checkKey="title", checkValue=self.FUNC_ALL_CLOSED_CASES_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_CLOSED_CASES_CASE_LIST['title'])
        assert(len(data['entities']))       # should return at least one case


    @tag('all', 'all_contacts_case_list')
    @task(6)
    def all_contacts_case_list(self):
        logging.info("all_contacts_case_list")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_ALL_CONTACTS_CASE_LIST['selections']],
        }, name="All Contacts Case List", checkKey="title", checkValue=self.FUNC_ALL_CONTACTS_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_CONTACTS_CASE_LIST['title'])
        assert(len(data['entities']))       # should return at least one case


    @tag('all', 'all_open_contacts_case_list')
    @task(6)
    def all_open_contacts_case_list(self):
        logging.info("all_open_contacts_case_list")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_ALL_OPEN_CONTACTS_CASE_LIST['selections']],
        }, name="All Open Contacts Case List", checkKey="title", checkValue=self.FUNC_ALL_OPEN_CONTACTS_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_OPEN_CONTACTS_CASE_LIST['title'])
        assert(len(data['entities']))       # should return at least one case


    @tag('all', 'all_closed_contacts_case_list')
    @task(6)
    def all_closed_contacts_case_list(self):
        logging.info("all_closed_contacts_case_list")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_ALL_CLOSED_CONTACTS_CASE_LIST['selections']],
        }, name="All Closed Contacts Case List", checkKey="title", checkValue=self.FUNC_ALL_CLOSED_CONTACTS_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_CLOSED_CONTACTS_CASE_LIST['title'])
        assert(len(data['entities']))       # should return at least one case


    @tag('all', 'ci-form', 'cal_test')
    @task(2)
    # Case Investigatoin Form
    class CIFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Cases, then a case
            self.local_case_id=self.parent._get_case_id_patient()
            logging.info("ci-form==case_details::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.FUNC_CASE_DETAILS['selections'], self.local_case_id],
            }, name="Case Detail for CI Form", checkKey=self.parent.FUNC_CASE_DETAILS['checkKey'], checkLen=self.parent.FUNC_CASE_DETAILS['checkLen'])
            ###logging.info("data-details==="+str(data))
            assert(len(data['details']) == self.parent.FUNC_CASE_DETAILS['checkLen'])


        @task
        def ci_form(self):
            # Select All Cases, then a case, then Case Investiation form
            logging.info("ci-form==ci_form::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.FUNC_CI_FORM['selections'], self.local_case_id, self.parent.FUNC_CI_FORM['subselections']],
            }, name="CI Form", checkKey="title", checkValue=self.parent.FUNC_CI_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.session_id=data['session_id']
            logging.info("ci_form==ci_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_CI_FORM['title'])
            assert('instanceXml' in data)


        @task
        def part_of_cluster(self):
            # Is this case part of a cluster? --> select No
            logging.info("ci-form==part_of_cluster::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_PART_OF_CLUSTER['answer'], 
                "ix": self.parent.FUNC_PART_OF_CLUSTER['ix'], 
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Part of Cluster for CI Form", checkKey="title", checkValue=self.parent.FUNC_PART_OF_CLUSTER['title'])
            assert(data['title'] == self.parent.FUNC_PART_OF_CLUSTER['title'])


        @task
        def hospitalized(self):
            # Hospitalized --> select Yes
            logging.info("ci-form==hospitalized::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_HOSPITALIZED['answer'],
                "ix": self.parent.FUNC_PART_OF_CLUSTER['ix'], 
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Hospitalizedfor CI Form", checkKey="title", checkValue=self.parent.FUNC_HOSPITALIZED['title'])
            assert(data['title'] == self.parent.FUNC_HOSPITALIZED['title'])


        @task
        def hospital_name(self):
            ## hospitalized --> yes --> hospital name free text response
            logging.info("ci-form==hospital_name::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_HOSPITAL_NAME['answer'],
                "ix": self.parent.FUNC_PART_OF_CLUSTER['ix'], 
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Hospital Name for CI Form", checkKey="title", checkValue=self.parent.FUNC_HOSPITAL_NAME['title'])
            assert(data['title'] == self.parent.FUNC_HOSPITAL_NAME['title'])


        @task
        def ci_form_submit(self):
            logging.info("ci-form==ci_form_submit::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": {
                    self.parent.FUNC_CI_FORM_SUBMIT['answers-key1']: [self.parent.FUNC_CI_FORM_SUBMIT['answers-value1']],
                    self.parent.FUNC_CI_FORM_SUBMIT['answers-key2']: self.parent.FUNC_CI_FORM_SUBMIT['answers-value2'],
                    self.parent.FUNC_CI_FORM_SUBMIT['answers-key3']: [self.parent.FUNC_CI_FORM_SUBMIT['answers-value3']],
                    self.parent.FUNC_CI_FORM_SUBMIT['answers-key4']: self.parent.FUNC_CI_FORM_SUBMIT['answers-value4']
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="CI Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_CI_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_CI_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'cm-form')
    @task(2)
    # Contact Monitoring Form
    class CMFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Contacts, then a contact
            self.local_contact_id=self.parent._get_case_id_contact()
            logging.info("cm-form==case_details::contact_id::"+self.local_contact_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.FUNC_CM_CASE_DETAILS['selections'], self.local_contact_id],
            }, name="Case Detail for CM Form", checkKey=self.parent.FUNC_CM_CASE_DETAILS['checkKey'], checkLen=self.parent.FUNC_CM_CASE_DETAILS['checkLen'])
            ###logging.info("data-details==="+str(data))
            assert(len(data['details']) == self.parent.FUNC_CM_CASE_DETAILS['checkLen'])


        @task
        def cm_form(self):
            # Select All Contacts, then a contact, then Case Monitoring form
            logging.info("cm-form==cm_form::contact_id::"+self.local_contact_id)
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.FUNC_CM_FORM['selections'], self.local_contact_id, self.parent.FUNC_CM_FORM['subselections']],
            }, name="CM Form", checkKey="title", checkValue=self.parent.FUNC_CM_FORM['title'])
            #logging.info("dara--->>"+str(data))
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.session_id=data['session_id']
            logging.info("cm_form==cm_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_CM_FORM['title'])
            assert('instanceXml' in data)


        @task
        def view_update_contact_info(self):
            if self.parent.FUNC_VIEW_UPDATE_CONTACT_INF_SKIP==True: 
                return
            logging.info("cm-form==view_update_contact_info::contact_id::"+self.local_contact_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_VIEW_UPDATE_CONTACT_INFO['answer'],
                "ix": self.parent.FUNC_VIEW_UPDATE_CONTACT_INFO['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="View/Update Contact Info for CM Form", checkKey="title", checkValue=self.parent.FUNC_VIEW_UPDATE_CONTACT_INFO['title'])
            assert(data['title'] == self.parent.FUNC_VIEW_UPDATE_CONTACT_INFO['title'])


        @task
        def invalid_phone_number(self):
            logging.info("cm-form==invalid_phone_number::contact_id::"+self.local_contact_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_INVALID_PHONE_NUMBER['answer'], 
                "ix": self.parent.FUNC_INVALID_PHONE_NUMBER['ix'], 
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Invalid Phone Number for CM Form", checkKey="title", checkValue=self.parent.FUNC_INVALID_PHONE_NUMBER['title'])
            assert(data['title'] == self.parent.FUNC_INVALID_PHONE_NUMBER['title'])


        @task
        def provider_name(self):
            logging.info("cm-form==provider_name::contact_id::"+self.local_contact_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_PROVIDER_NAME['answer'],
                "ix": self.parent.FUNC_PROVIDER_NAME['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Provider Name for CM Form", checkKey="title", checkValue=self.parent.FUNC_PROVIDER_NAME['title'])
            assert(data['title'] == self.parent.FUNC_PROVIDER_NAME['title'])


        @task
        def cm_form_submit(self):
            logging.info("cm-form==cm_form_submit::contact_id::"+self.local_contact_id)
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": {
                    self.parent.FUNC_CM_FORM_SUBMIT['answers-key1']: [self.parent.FUNC_CM_FORM_SUBMIT['answers-value1']],
                    self.parent.FUNC_CM_FORM_SUBMIT['answers-key2']: self.parent.FUNC_CM_FORM_SUBMIT['answers-value2']
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="CM Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_CM_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_CM_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'id-form', 'cal_test')
    @task(2)
    # Identify Duplicate Patient
    class IDPatientEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Cases, then a case
            self.local_case_id=self.parent._get_case_id_patient()
            logging.info("id-form==case_details::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.FUNC_CASE_DETAILS['selections'], self.local_case_id],
            }, name="Case Detail for ID Form", checkKey=self.parent.FUNC_CASE_DETAILS['checkKey'], checkLen=self.parent.FUNC_CASE_DETAILS['checkLen'])
            assert(len(data['details']) == self.parent.FUNC_CASE_DETAILS['checkLen'])


        @task
        def id_form(self):
            # Select All Cases, then a case, then Identify Duplicate Patient form
            logging.info("id-form==id_form::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.FUNC_ID_FORM['selections'], self.local_case_id, self.parent.FUNC_ID_FORM['subselections']],
            }, name="ID Form", checkKey="title", checkValue=self.parent.FUNC_ID_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.session_id=data['session_id']
            logging.info("id_form==id_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_ID_FORM['title'])
            assert('instanceXml' in data)


        @task
        def alternate_phone_number(self):
            logging.info("id-form==alternate_phone_number::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_ALTERNATE_PHONE_NUMBER['answer'], 
                "ix": self.parent.FUNC_ALTERNATE_PHONE_NUMBER['ix'], 
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Alternate Phone Number for ID Form", checkKey="title", checkValue=self.parent.FUNC_ALTERNATE_PHONE_NUMBER['title'])
            assert(data['title'] == self.parent.FUNC_ALTERNATE_PHONE_NUMBER['title'])


        @task
        def alternate_phone_number_enter(self):
            logging.info("id-form==alternate_phone_number_enter::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_ALTERNATE_PHONE_NUMBER_ENTER['answer'],
                "ix": self.parent.FUNC_ALTERNATE_PHONE_NUMBER_ENTER['ix'], 
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Alternate Phone Number Enter for ID Form", checkKey="title", checkValue=self.parent.FUNC_ALTERNATE_PHONE_NUMBER_ENTER['title'])
            assert(data['title'] == self.parent.FUNC_ALTERNATE_PHONE_NUMBER_ENTER['title'])


        @task
        def id_form_submit(self):
            logging.info("id-form==id_form_submit::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": {
                    self.parent.FUNC_ID_FORM_SUBMIT['answers-key']: [self.parent.FUNC_ID_FORM_SUBMIT['answers-value']]
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="ID Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_ID_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_ID_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'register-new-contact-form')
    @task(2)
    # Register New Contacts Form
    class RNCFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Cases, then a case
            self.local_case_id=self.parent._get_case_id_patient()
            logging.info("register-new-contact-form==case_details::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.FUNC_CASE_DETAILS['selections'], self.local_case_id],
            }, name="Case Detail for Register New Contact Form", checkKey=self.parent.FUNC_CASE_DETAILS['checkKey'], checkLen=self.parent.FUNC_CASE_DETAILS['checkLen'])
            assert(len(data['details']) == self.parent.FUNC_CASE_DETAILS['checkLen'])


        @task
        def rnc_form(self):
            # Select All Cases, then a case, then Register New Contacts form
            logging.info("register-new-contact-form==rnc_form::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.FUNC_RNC_FORM['selections'], self.local_case_id, self.parent.FUNC_RNC_FORM['subselections']],
            }, name="Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.session_id=data['session_id']
            logging.info("register-new-contact-form=rnc_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_RNC_FORM['title'])
            assert('instanceXml' in data)


        @task
        def rnc_total_number_people(self):
            logging.info("register-new-contact-form==total_number_people::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_RNC_TOTAL_NUM_PEOPLE['answer'],
                "ix": self.parent.FUNC_RNC_TOTAL_NUM_PEOPLE['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Total Number of People for Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_TOTAL_NUM_PEOPLE['title'])
            assert(data['title'] == self.parent.FUNC_RNC_TOTAL_NUM_PEOPLE['title'])


        @task
        def rnc_first_name(self):
            logging.info("register-new-contact-form==first_name::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_RNC_FIRST_NAME['answer'], 
                "ix": self.parent.FUNC_RNC_FIRST_NAME['ix'], 
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="First Name for Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_FIRST_NAME['title'])
            assert(data['title'] == self.parent.FUNC_RNC_FIRST_NAME['title'])


        @task
        def rnc_last_name(self):
            logging.info("register-new-contact-form==last_name::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_RNC_LAST_NAME['answer'],
                "ix": self.parent.FUNC_RNC_LAST_NAME['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Last Name for Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_LAST_NAME['title'])
            assert(data['title'] == self.parent.FUNC_RNC_LAST_NAME['title'])


        @task
        def rnc_school_setting(self):
            logging.info("register-new-contact-form==school_setting::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_RNC_SCHOOL_SETTING['answer'],
                "ix": self.parent.FUNC_RNC_SCHOOL_SETTING['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="School Setting for Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_SCHOOL_SETTING['title'])
            assert(data['title'] == self.parent.FUNC_RNC_SCHOOL_SETTING['title'])


        @task
        def rnc_school_prek(self):
            logging.info("register-new-contact-form==school_prek::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_RNC_SCHOOL_PREK['answer'],
                "ix": self.parent.FUNC_RNC_SCHOOL_PREK['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="School PreK - 12 for Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_SCHOOL_PREK['title'])
            assert(data['title'] == self.parent.FUNC_RNC_SCHOOL_PREK['title'])


        @task
        def rnc_college_university(self):
            logging.info("register-new-contact-form==college_university::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": [self.parent.FUNC_RNC_COLLEGE_UNIVERSITY['answer']],
                "ix": self.parent.FUNC_RNC_COLLEGE_UNIVERSITY['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="College University for Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_COLLEGE_UNIVERSITY['title'])
            assert(data['title'] == self.parent.FUNC_RNC_COLLEGE_UNIVERSITY['title'])


        @task
        def rnc_name_of_school(self):
            logging.info("register-new-contact-form==name_of_school::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_RNC_NAME_OF_SCHOOL['answer'],
                "ix": self.parent.FUNC_RNC_NAME_OF_SCHOOL['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Name of School for Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_NAME_OF_SCHOOL['title'])
            assert(data['title'] == self.parent.FUNC_RNC_NAME_OF_SCHOOL['title'])


        @task
        def rnc_name_of_university(self):
            logging.info("register-new-contact-form==name_of_university::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_RNC_NAME_OF_UNIVERSITY['answer'],
                "ix": self.parent.FUNC_RNC_NAME_OF_UNIVERSITY['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Name of University for Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_NAME_OF_UNIVERSITY['title'])
            assert(data['title'] == self.parent.FUNC_RNC_NAME_OF_UNIVERSITY['title'])


        @task
        def rnc_preferred_language(self):
            logging.info("register-new-contact-form==preferred_language::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_RNC_PREFERRED_LANGUAGE['answer'],
                "ix": self.parent.FUNC_RNC_PREFERRED_LANGUAGE['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Preferred Language for Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_PREFERRED_LANGUAGE['title'])
            assert(data['title'] == self.parent.FUNC_RNC_PREFERRED_LANGUAGE['title'])


        @task
        def rnc_last_date_test(self):
            logging.info("register-new-contact-form==last_date_test::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_RNC_LAST_DATE_TEST['answer'],
                "ix": self.parent.FUNC_RNC_LAST_DATE_TEST['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Last Date Test for Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_LAST_DATE_TEST['title'])
            assert(data['title'] == self.parent.FUNC_RNC_LAST_DATE_TEST['title'])


        @task
        def rnc_form_submit(self):
            logging.info("register-new-contact-form==rnc_form_submit::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": {
                    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key1']: self.parent.FUNC_RNC_FORM_SUBMIT['answers-value1'],
                    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key2']: self.parent.FUNC_RNC_FORM_SUBMIT['answers-value2'],
                    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key3']: [self.parent.FUNC_RNC_FORM_SUBMIT['answers-value3']],
                    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key4']: [self.parent.FUNC_RNC_FORM_SUBMIT['answers-value4']],
                    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key5']: self.parent.FUNC_RNC_FORM_SUBMIT['answers-value5'],
                    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key6']: self.parent.FUNC_RNC_FORM_SUBMIT['answers-value6'],
                    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key7']: [self.parent.FUNC_RNC_FORM_SUBMIT['answers-value7']],
                    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key8']: self.parent.FUNC_RNC_FORM_SUBMIT['answers-value8']
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Register New Contact Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_RNC_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_RNC_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()

    """
    @tag('case_claim_search', 'search')
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
        logging.info("data-->>"+str(data))
        assert(data["title"] == self.FUNC_CASE_CLAIM_SEARCH['title'])


    @tag('omni_search', 'search')
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
    """


    @tag('new-case-search', 'test')
    @task(6)
    class NewCaseSearch(SequentialTaskSet):
        @task
        def new_search_all_cases_form(self):
            logging.info("new-case-search==new_search_all_cases_form")
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections" : [self.parent.FUNC_NEW_SEARCH_ALL_CASES_FORM['selections']],
                },
                name="New Case Search Form", checkKey="title", checkValue=self.parent.FUNC_NEW_SEARCH_ALL_CASES_FORM['title'])
            assert(data["title"] == self.parent.FUNC_NEW_SEARCH_ALL_CASES_FORM['title'])


        @task
        def new_search_all_cases(self):
            logging.info("new-case-search==new_search_all_cases")
            search_value = random.choice(self.parent.SEARCH_NAMES)
            logging.info("new-case-searach==new_search_all_cases::search_term::"+search_value)
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections" : [self.parent.FUNC_NEW_SEARCH_ALL_CASES['selections']],
                "query_dictionary" : {"first_name" : search_value}},
                name="Search All Cases", checkKey="title", checkValue=self.parent.FUNC_NEW_SEARCH_ALL_CASES['title'])
            assert(data["title"] == self.parent.FUNC_NEW_SEARCH_ALL_CASES['title'])


        @task
        def stop(self):
            self.interrupt()


    @tag('new-contact-search', 'test')
    @task(6)
    class NewContactSearch(SequentialTaskSet):
        @task
        def new_search_all_contacts_form(self):
            logging.info("new-contact-search==new_search_all_contacts_form")
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections" : [self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS_FORM['selections']],
                },
                name="Search All Contacts Form", checkKey="title", checkValue=self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS_FORM['title'])
            assert(data["title"] == self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS_FORM['title'])
    

        @task
        def new_search_all_contacts(self):
            logging.info("new-contact-search==new_search_all_contacts")
            search_value = random.choice(self.parent.SEARCH_NAMES)
            logging.info("new-contact-search==new_search_all_contacts::search_term::"+search_value)

            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections" : [self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS['selections']],
                "query_dictionary" : {"first_name" : search_value}},
                name="Search All Contacts", checkKey="title", checkValue=self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS['title'])
            assert(data["title"] == self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS['title'])


        @task
        def stop(self):
            self.interrupt()


    @tag('bulk-update-contacts')
    @task(2)
    # Bulk Update Contacts Form
    class BulkUpdateContactsFormEntry(SequentialTaskSet):
        @task
        def bulk_update_contacts_form(self):
            logging.info("bulk-update-contacts==bulk_update_contacts_form")
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.FUNC_BU_CONTACTS_FORM['selections']],
            }, name="Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_CONTACTS_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.session_id=data['session_id']
            logging.info("bulk_update_contacts_form==bulk_update_contacts_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_BU_CONTACTS_FORM['title'])
            assert('instanceXml' in data)


        @task
        def type_of_bulk_action(self):
            logging.info("bulk-update-contacs-form==type_of_bulk_action")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_CONTACTS_TYPE_OF_BULK['answer'],
                "ix": self.parent.FUNC_BU_CONTACTS_TYPE_OF_BULK['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Uncheck Open Cases for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CONTACTS_TYPE_OF_BULK['title'])
            assert(data['title'] == self.parent.FUNC_BU_CONTACTS_TYPE_OF_BULK['title'])


        @task
        def select_without_primary(self):
            if self.parent.FUNC_BU_SELECT_WITHOUT_PRIMARY_SKIP==True:
                return
            logging.info("bulk-update-contacts==select_without_primary")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_SELECT_WITHOUT_PRIMARY['answer'],
                "ix": self.parent.FUNC_BU_SELECT_WITHOUT_PRIMARY['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Select Without Primary for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_SELECT_WITHOUT_PRIMARY['title'])
            assert(data['title'] == self.parent.FUNC_BU_SELECT_WITHOUT_PRIMARY['title'])

        @task
        def contacts_matching_cases(self):
            logging.info("bulk-update-contacts-form==contacts_matching_cases")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": [self.parent.FUNC_BU_CONTACTS_MATCHING['answer']],
                "ix": self.parent.FUNC_BU_CONTACTS_MATCHING['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Contacts Matching for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_CONTACTS_MATCHING['title'])
            assert(data['title'] == self.parent.FUNC_BU_CONTACTS_MATCHING['title'])


        @task
        def bu_contacts_assign_action(self):
            logging.info("bulk-update-contacts-form==bu_contacts_assign_action")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_CONTACTS_ASSIGN_ACTION['answer'],
                "ix": self.parent.FUNC_BU_CONTACTS_ASSIGN_ACTION['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Assign Action for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_CONTACTS_ASSIGN_ACTION['title'])
            assert(data['title'] == self.parent.FUNC_BU_CONTACTS_ASSIGN_ACTION['title'])


        @task
        def select_owner_contacts(self):
            if self.parent.FUNC_BU_CONTACTS_SELECT_OWNER_SKIP==True:
                return
            logging.info("bulk-update-contacts-form==select_owner_contacts")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": [self.parent.FUNC_BU_CONTACTS_SELECT_OWNER['answer']],
                "ix": self.parent.FUNC_BU_CONTACTS_SELECT_OWNER['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Select Owner for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_CONTACTS_SELECT_OWNER['title'])
            assert(data['title'] == self.parent.FUNC_BU_CONTACTS_SELECT_OWNER['title'])


        @task
        def update_fewer_contacts(self):
            logging.info("bulk-update-contacts-form==update_fewer_contacts")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_UPDATE_FEWER_CONTACTS['answer'],
                "ix": self.parent.FUNC_BU_UPDATE_FEWER_CONTACTS['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Update Fewer Contacts for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_UPDATE_FEWER_CONTACTS['title'])
            assert(data['title'] == self.parent.FUNC_BU_UPDATE_FEWER_CONTACTS['title'])


        @task
        def number_of_updates_contacts(self):
            logging.info("bulk-update-contacts-form==number_of_updates_contacts")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_NUMBER_OF_UPDATES['answer'],
                "ix": self.parent.FUNC_BU_NUMBER_OF_UPDATES['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Number of Updates for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_NUMBER_OF_UPDATES['title'])
            assert(data['title'] == self.parent.FUNC_BU_NUMBER_OF_UPDATES['title'])


        @task
        def bulk_update_contacts_form_submit(self):
            logging.info("bulk-update-contacts-form==bulk_update_contacts_form_submit")
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": {
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-type-of-bulk']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-type-of-bulk'],
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-select-without-primary']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-select-without-primary'],
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-contacts-matching']: [self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-contacts-matching']],
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-select-owner']: [self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-select-owner']],
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-assign-action']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-assign-action'],
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-update-fewer-contacts']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-update-fewer-contacts'],
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-number-of-updates']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-number-of-updates']
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Bulk Update Contacts Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['submitResponseMessage'])
            ##logging.info("data-->"+str(data))
            self.session_id2=data['nextScreen']['session_id']
            logging.info("bulk_update_contacts_form==bulk_update_contacts_form_submit::sessionId::"+self.session_id2)
            assert(data['submitResponseMessage'] == self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['submitResponseMessage'])


        @task
        def update_contacts_form_submit(self):
            logging.info("bulk-update-contacts-form==update_contacts_form_submit")
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": { },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id2,
            }, name="Update Contacts Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_UPDATE_CONTACTS_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_UPDATE_CONTACTS_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('bulk-update-cases')
    @task(1)
    # Bulk Update Cases Form
    class BulkUpdateCasesFormEntry(SequentialTaskSet):
        @task
        def bulk_update_cases(self):
            logging.info("bulk-update-cases==bulk_update_cases_form")
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.FUNC_BU_CASES_FORM['selections']],
            }, name="Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.session_id=data['session_id']
            logging.info("bulk_update_cases_form==bulk_update_cases_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_BU_CASES_FORM['title'])
            assert('instanceXml' in data)


        @task
        def type_of_bulk_action(self):
            logging.info("bulk-update-cases-form==type_of_bulk_action")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_CASES_TYPE_OF_BULK['answer'],
                "ix": self.parent.FUNC_BU_CASES_TYPE_OF_BULK['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Uncheck Open Cases for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_TYPE_OF_BULK['title'])
            assert(data['title'] == self.parent.FUNC_BU_CASES_TYPE_OF_BULK['title'])


        @task
        def uncheck_open_cases(self):
            logging.info("bulk-update-cases-form==uncheck_open_cases")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_CASES_UNCHECK_OPEN_CASES['answer'],
                "ix": self.parent.FUNC_BU_CASES_UNCHECK_OPEN_CASES['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Uncheck Open Cases for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_UNCHECK_OPEN_CASES['title'])
            assert(data['title'] == self.parent.FUNC_BU_CASES_UNCHECK_OPEN_CASES['title'])


        @task
        def uncheck_valid_phone(self):
            logging.info("bulk-update-cases-form==uncheck_valid_phone")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_CASES_UNCHECK_VALID_PHONE['answer'],
                "ix": self.parent.FUNC_BU_CASES_UNCHECK_VALID_PHONE['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Uncheck Valid Phone for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_UNCHECK_VALID_PHONE['title'])
            assert(data['title'] == self.parent.FUNC_BU_CASES_UNCHECK_VALID_PHONE['title'])


        @task
        def uncheck_confirmed_cases(self):
            logging.info("bulk-update-cases-form==uncheck_confirmed_cases")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_CASES_UNCHECK_CONFIRMED_CASES['answer'],
                "ix": self.parent.FUNC_BU_CASES_UNCHECK_CONFIRMED_CASES['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Uncheck Valid Phone for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_UNCHECK_CONFIRMED_CASES['title'])
            assert(data['title'] == self.parent.FUNC_BU_CASES_UNCHECK_CONFIRMED_CASES['title'])


        @task
        def uncheck_initial_interview(self):
            logging.info("bulk-update-cases-form==uncheck_initial_interview")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_CASES_UNCHECK_INITIAL_INTERVIEW['answer'],
                "ix": self.parent.FUNC_BU_CASES_UNCHECK_INITIAL_INTERVIEW['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Uncheck Initial Interview for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_UNCHECK_INITIAL_INTERVIEW['title'])
            assert(data['title'] == self.parent.FUNC_BU_CASES_UNCHECK_INITIAL_INTERVIEW['title'])


        @task
        def uncheck_primary_owner(self):
            logging.info("bulk-update-cases-form==uncheck_primary_owner")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_CASES_UNCHECK_PRIMARY_OWNER['answer'],
                "ix": self.parent.FUNC_BU_CASES_UNCHECK_PRIMARY_OWNER['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Uncheck Primary Owner for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_UNCHECK_PRIMARY_OWNER['title'])
            assert(data['title'] == self.parent.FUNC_BU_CASES_UNCHECK_PRIMARY_OWNER['title'])


        @task
        def contacts_matching(self):
            logging.info("bulk-update-cases-form==contacts_matching")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": [self.parent.FUNC_BU_CASES_MATCHING['answer']],
                "ix": self.parent.FUNC_BU_CASES_MATCHING['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Contacts Matching for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_MATCHING['title'])
            assert(data['title'] == self.parent.FUNC_BU_CASES_MATCHING['title'])


        @task
        def assign_primary_contacts(self):
            logging.info("bulk-update-cases-form==assign_primary_contacts")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_CASES_ASSIGN_PRIMARY['answer'],
                "ix": self.parent.FUNC_BU_CASES_ASSIGN_PRIMARY['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Assign Primary for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_ASSIGN_PRIMARY['title'])
            assert(data['title'] == self.parent.FUNC_BU_CASES_ASSIGN_PRIMARY['title'])


        @task
        def select_owner_cases(self):
            logging.info("bulk-update-cases-form==select_owner_cases")
            logging.info("sessionId--->>>"+self.session_id)
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": [self.parent.FUNC_BU_CASES_SELECT_OWNER['answer']],
                "ix": self.parent.FUNC_BU_CASES_SELECT_OWNER['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Select Owner for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_SELECT_OWNER['title'])
            ###logging.info("data--->>>>>"+str(data))
            assert(data['title'] == self.parent.FUNC_BU_CASES_SELECT_OWNER['title'])


        @task
        def update_fewer_cases(self):
            logging.info("bulk-update-cases-form==update_fewer_cases")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_CASES_UPDATE_FEWER_CASES['answer'],
                "ix": self.parent.FUNC_BU_CASES_UPDATE_FEWER_CASES['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Update Fewer Cases for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_UPDATE_FEWER_CASES['title'])
            assert(data['title'] == self.parent.FUNC_BU_CASES_UPDATE_FEWER_CASES['title'])


        @task
        def number_of_updates_cases(self):
            logging.info("bulk-update-cases-form==number_of_updates_cases")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_CASES_NUMBER_OF_UPDATES['answer'],
                "ix": self.parent.FUNC_BU_CASES_NUMBER_OF_UPDATES['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Number of Updates for Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_NUMBER_OF_UPDATES['title'])
            assert(data['title'] == self.parent.FUNC_BU_CASES_NUMBER_OF_UPDATES['title'])


        @task
        def bulk_update_cases_form_submit(self):
            logging.info("bulk-update-cases-form==bulk_update_cases_form_submit")
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": {
                    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key0']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value0'],
                    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key1']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value1'],
                    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key2']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value2'],
                    ##self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key3']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value3'],
                    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key4']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value4'],
                    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key5']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value5'],
                    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key6']: [self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value6']],
                    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key7']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value7'],
                    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key8']: [self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value8']],
                    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key9']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value9'],
                    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key10']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value10']
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Bulk Update Contacts Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_BU_CASES_FORM_SUBMIT['submitResponseMessage'])
            self.session_id2=data['nextScreen']['session_id']
            logging.info("bulk_update_contacts_form==bulk_update_contacts_form_submit::sessionId::"+self.session_id2)
            assert(data['submitResponseMessage'] == self.parent.FUNC_BU_CASES_FORM_SUBMIT['submitResponseMessage'])


        @task
        def update_cases_form_submit(self):
            logging.info("bulk-update-cases-form==update_cases_form_submit")
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": { },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id2,
            }, name="Update Contacts Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_UPDATE_CASES_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_UPDATE_CASES_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('bulk-update-form-old')
    @task
    # Bulk Update Contacts Form - old
    class BulkUpdateFormEntryOld(SequentialTaskSet):
        @task
        def bulk_update_form(self):
            logging.info("bulk-update-form==bulk_update_form")
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.FUNC_BU_CONTACTS_FORM['selections'],self.parent.FUNC_BU_CONTACTS_FORM['subselections']],
            }, name="Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_CONTACTS_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.session_id=data['session_id']
            logging.info("bulk_update_form==bulk_update_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_BU_CONTACTS_FORM['title'])
            assert('instanceXml' in data)


        @task
        def contacts_matching_contacts(self):
            logging.info("bulk-update-form==contacts_matching_contacts")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": [self.parent.FUNC_BU_CONTACTS_MATCHING['answer']],
                "ix": self.parent.FUNC_BU_CONTACTS_MATCHING['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Contacts Matching for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_CONTACTS_MATCHING['title'])
            assert(data['title'] == self.parent.FUNC_BU_CONTACTS_MATCHING['title'])


        @task
        def assign_primary_cases(self):
            logging.info("bulk-update-form==assign_primary_cases")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_ASSIGN_PRIMARY['answer'],
                "ix": self.parent.FUNC_BU_ASSIGN_PRIMARY['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Assign Primary for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_ASSIGN_PRIMARY['title'])
            assert(data['title'] == self.parent.FUNC_BU_ASSIGN_PRIMARY['title'])


        @task
        def select_owner(self):
            logging.info("bulk-update-form==select_owner")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": [self.parent.FUNC_BU_SELECT_OWNER['answer']],
                "ix": self.parent.FUNC_BU_SELECT_OWNER['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Select Owner for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_SELECT_OWNER['title'])
            assert(data['title'] == self.parent.FUNC_BU_SELECT_OWNER['title'])


        @task
        def update_fewer_contacts(self):
            logging.info("bulk-update-form==update_fewer_contacts")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_ASSIGN_PRIMARY['answer'],
                "ix": self.parent.FUNC_BU_ASSIGN_PRIMARY['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Update Fewer Contacts for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_ASSIGN_PRIMARY['title'])
            assert(data['title'] == self.parent.FUNC_BU_ASSIGN_PRIMARY['title'])


        @task
        def number_of_updates(self):
            logging.info("bulk-update-form==number_of_updates")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": self.parent.FUNC_BU_NUMBER_OF_UPDATES['answer'],
                "ix": self.parent.FUNC_BU_NUMBER_OF_UPDATES['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Number of Updates for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_NUMBER_OF_UPDATES['title'])
            assert(data['title'] == self.parent.FUNC_BU_NUMBER_OF_UPDATES['title'])


        @task
        def bulk_update_form_submit(self):
            logging.info("bulk-update-form==bulk_update_form_submit")
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": {
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key1']: [self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value1']],
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key2']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value2'],
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key3']: [self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value3']],
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key4']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value4'],
                    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key5']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value5']
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Bulk Update Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['submitResponseMessage'])
            self.session_id2=data['nextScreen']['session_id']
            logging.info("bulk_update_form==bulk_update_form_submit::sessionId::"+self.session_id2)
            assert(data['submitResponseMessage'] == self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['submitResponseMessage'])


        @task
        def update_contacts_form_submit(self):
            logging.info("bulk-update-form==update_contacts_form_submit")
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": { },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id2,
            }, name="Update Contacts Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_UPDATE_CONTACTS_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_UPDATE_CONTACTS_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


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
            ##logging.info("data-->"+str(data))
            if ("exception" in data):
                logging.info("ERROR::exception error--"+data['exception'])
                logging.info("ERROR::user-info::"+self.user.username+"::"+self.user.login_as)
                response.failure("exception error--"+data['exception'])
            elif (checkKey and checkKey not in data):
                logging.info("error::"+checkKey+" not in data")
                response.failure("ERROR::"+checkKey+" not in data")
            elif (checkKey and checkLen):
                if (len(data[checkKey]) != checkLen):
                    logging.info("ERROR::len(data['"+checkKey+"']) != "+checkLen)
                    response.failure("error::len(data['"+checkKey+"']) != "+checkLen)
            elif (checkKey and checkValue):
                if (data[checkKey] != checkValue):
                    logging.info("ERROR::data['"+checkKey+"'] != "+checkValue)
                    response.failure("error::data['"+checkKey+"'] != "+checkValue)
        return response.json()


class LoginCommCareHQWithUniqueUsers(HttpUser):
    tasks= [WorkloadModelSteps]

    formplayer_host = "/formplayer" 
    project=str(os.environ.get("project"))
    domain_user_credential_force=str(os.environ.get("user_credential"))
    app_config_force=str(os.environ.get("app_config"))
    wait_time_force=str(os.environ.get("wait_time"))

    if (wait_time_force=="test"):
        wait_time = between(2, 4)
        ###wait_time = between(5, 10)
    else:
        wait_time = between(45, 90)
        ###wait_time = between(30, 60)
        ###wait_time = between(15, 30)

    with open("project-config/"+project+"/config.yaml") as f:
        config = yaml.safe_load(f)
        host = config['host']
        domain = config['domain']
        app_id = config['app_id']
        if (domain_user_credential_force!="None"):
            domain_user_credential = "project-config/"+project+"/"+domain_user_credential_force 
        else:
            domain_user_credential = config['domain_user_credential']
        if (app_config_force!="None"):
            app_config = "project-config/"+project+"/"+app_config_force
        else:
            app_config = config['app_config']
        owner_id = config['owner_id']
        case_type = config['case_type']

    ## get domain user credential and app config info
    with open(domain_user_credential) as json_file:
        data = json.load(json_file)
        data_user=data['user']


    def on_start(self):
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        dt_object = datetime.fromtimestamp(timestamp)
        user_info=self.data_user.pop()
        self.username=user_info['username']
        self.password=user_info['password']
        self.login_as=user_info['login_as']
        #print("userinfo===>>"+str(user_info))

        logging.info("timestamp-->>>"+str(dt_object))
        logging.info("host-->>>"+self.host)
        logging.info("login_as-->>>"+self.login_as)
        logging.info("username-->>>"+self.username)
        logging.info("domain-->>>"+self.domain)
        logging.info("domain_user_credential-->>>"+self.domain_user_credential)
        logging.info("app_config-->>>"+self.app_config)

