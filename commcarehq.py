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
            self.MOD_SKIP=data['MOD_SKIP']
            self.ALL_CASES=data['ALL_CASES']
            self.SEARCH_NAMES=data['SEARCH_NAMES']
            self.FUNC_USER_CHECK_IN_FORM=data['FUNC_USER_CHECK_IN_FORM']
            self.FUNC_USER_CHECK_IN=data['FUNC_USER_CHECK_IN']
            self.FUNC_HOME_SCREEN=data['FUNC_HOME_SCREEN']
            self.FUNC_ALL_CASES_CASE_LIST=data['FUNC_ALL_CASES_CASE_LIST']
            self.FUNC_ALL_OPEN_CASES_CASE_LIST=data['FUNC_ALL_OPEN_CASES_CASE_LIST']
            self.FUNC_ALL_CLOSED_CASES_CASE_LIST=data['FUNC_ALL_CLOSED_CASES_CASE_LIST']
            self.FUNC_CASE_DETAILS=data['FUNC_CASE_DETAILS']
            self.FUNC_CI_FORM=data['FUNC_CI_FORM']
            self.FUNC_PART_OF_CLUSTER=data['FUNC_PART_OF_CLUSTER']
            self.FUNC_HOSPITALIZED=data['FUNC_HOSPITALIZED']
            self.FUNC_HOSPITAL_NAME=data['FUNC_HOSPITAL_NAME']
            self.FUNC_CI_FORM_SUBMIT=data['FUNC_CI_FORM_SUBMIT']
            self.FUNC_ID_FORM=data['FUNC_ID_FORM']
            self.FUNC_ALTERNATE_PHONE_NUMBER=data['FUNC_ALTERNATE_PHONE_NUMBER']
            self.FUNC_ALTERNATE_PHONE_NUMBER_ENTER=data['FUNC_ALTERNATE_PHONE_NUMBER_ENTER']
            self.FUNC_ID_FORM_SUBMIT=data['FUNC_ID_FORM_SUBMIT']
            self.FUNC_RNC_FORM=data['FUNC_RNC_FORM']
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
            self.FUNC_BU_CONTACTS_MATCHING=data['FUNC_BU_CONTACTS_MATCHING']
            self.FUNC_BU_ASSIGN_PRIMARY=data['FUNC_BU_ASSIGN_PRIMARY']
            self.FUNC_BU_SELECT_OWNER=data['FUNC_BU_SELECT_OWNER']
            self.FUNC_BU_NUMBER_OF_UPDATES=data['FUNC_BU_NUMBER_OF_UPDATES']
            self.FUNC_BU_CONTACTS_FORM_SUBMIT=data['FUNC_BU_CONTACTS_FORM_SUBMIT']
            self.FUNC_UPDATE_CONTACTS_FORM_SUBMIT=data['FUNC_UPDATE_CONTACTS_FORM_SUBMIT']
        self._log_in()
        self._get_build_info()
        if not self.MOD_SKIP['get_all_cases_info']:
            self._get_all_cases_info()
        if not self.MOD_SKIP['get_all_cases_info']:
            self._get_all_cases_filter()
        if not self.MOD_SKIP['get_all_cases_info']:
            self._get_all_cases_ids()
        if not self.MOD_SKIP['check_in_form']:
            self._user_check_in_form()
        if not self.MOD_SKIP['check_in_form']:
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
        local_filter=self.ALL_CASES['filter'] if self.ALL_CASES['filter']!='' else str(self.all_cases_module['case_details']['short']['filter'])
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


    @tag('all', 'home_screen')
    @task
    def home_screen(self):
        logging.info("home_screen")
        data = self._formplayer_post("navigate_menu_start", name="Home Screen", checkKey="title", checkValue=self.FUNC_HOME_SCREEN['title'])
        assert(data['title'] == self.FUNC_HOME_SCREEN['title'])
        #assert(len(data['commands']) == 41)


    @tag('all', 'all_cases_case_list')
    @task
    def all_cases_case_list(self):
        logging.info("all_cases_case_list")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_ALL_CASES_CASE_LIST['selections']],
        }, name="All Cases Case List", checkKey="title", checkValue=self.FUNC_ALL_CASES_CASE_LIST['title'])
        #data = self._navigate_menu([5], name="All Cases case list")
        assert(data['title'] == self.FUNC_ALL_CASES_CASE_LIST['title'])
        assert(len(data['entities']))       # should return at least one case


    @tag('all', 'all_open_cases_case_list', 'cal_test')
    @task
    def all_open_cases_case_list(self):
        logging.info("all_open_cases_case_list")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_ALL_OPEN_CASES_CASE_LIST['selections']],
        }, name="All Open Cases Case List", checkKey="title", checkValue=self.FUNC_ALL_OPEN_CASES_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_OPEN_CASES_CASE_LIST['title'])
        assert(len(data['entities']))       # should return at least one case


    @tag('all', 'all_closed_cases_case_list', 'cal_test')
    @task
    def all_closed_cases_case_list(self):
        logging.info("all_closed_cases_case_list")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_ALL_CLOSED_CASES_CASE_LIST['selections']],
        }, name="All Closed Cases Case List", checkKey="title", checkValue=self.FUNC_ALL_CLOSED_CASES_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_CLOSED_CASES_CASE_LIST['title'])
        assert(len(data['entities']))       # should return at least one case


    @tag('all', 'ci-form', 'cal_test')
    @task
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
            assert(len(data['details']) == self.parent.FUNC_CASE_DETAILS['checkLen'])


        @task
        def ci_form(self):
            # Select All Cases, then a case, then Case Investiation form
            logging.info("ci-form==ci_form::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.FUNC_CI_FORM['selections'], self.local_case_id, self.parent.FUNC_CI_FORM['subselections']],
            }, name="CI Form", checkKey="title", checkValue=self.parent.FUNC_CI_FORM['title'])
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


    @tag('all', 'id-form', 'cal_test')
    @task
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
    @task
    # Register New Contacts Form
    class RNCFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Cases, then a case
            ##self.local_case_id=self.parent._get_case_id_patient()


            self.local_case_id="37974432deff4c8c81f6856498e05550"

 
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
            self.session_id=data['session_id']
            logging.info("register-new-contact-form=rnc_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_RNC_FORM['title'])
            assert('instanceXml' in data)


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
                "answer": self.parent.FUNC_RNC_COLLEGE_UNIVERSITY['answer'],
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
    @task
    class NewCaseSearch(SequentialTaskSet):
        @task
        def new_search_all_cases_form(self):
            logging.info("new-case-search==new_search_all_cases_form")
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections" : [self.parent.FUNC_NEW_SEARCH_ALL_CASES_FORM['selections']],
                },
                name="Search All Cases Form", checkKey="title", checkValue=self.parent.FUNC_NEW_SEARCH_ALL_CASES_FORM['title'])
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
            logging.info("new-case-search==stop")
            self.interrupt()


    @tag('new-contact-search', 'test')
    @task
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
            logging.info("new-contact-search==stop")
            self.interrupt()


    @tag('bulk-update-form')
    @task
    # Bulk Update Contacts Form
    class BulkUpdateFormEntry(SequentialTaskSet):
        @task
        def bulk_update_form(self):
            logging.info("bulk-update-form==bulk_update_form")
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.FUNC_BU_CONTACTS_FORM['selections'],self.parent.FUNC_BU_CONTACTS_FORM['subselections']],
            }, name="Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_CONTACTS_FORM['title'])
            self.session_id=data['session_id']
            logging.info("bulk_update_form==bulk_update_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_BU_CONTACTS_FORM['title'])
            assert('instanceXml' in data)


        @task
        def contacts_matching(self):
            logging.info("bulk-update-form==contacts_matching")
            data = self.parent._formplayer_post("answer", extra_json={
                "answer": [self.parent.FUNC_BU_CONTACTS_MATCHING['answer']],
                "ix": self.parent.FUNC_BU_CONTACTS_MATCHING['ix'],
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Contacts Matching for Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_CONTACTS_MATCHING['title'])
            assert(data['title'] == self.parent.FUNC_BU_CONTACTS_MATCHING['title'])


        @task
        def assign_primary(self):
            logging.info("bulk-update-form==assign_primary")
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
    ###wait_time = between(5, 10)
    formplayer_host = "/formplayer" 
    project=str(os.environ.get("project"))

    with open("project-config/"+project+"/config.yaml") as f:
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

