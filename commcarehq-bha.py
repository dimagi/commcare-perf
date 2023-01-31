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
    def on_start(self):
        ## define global variables
        self.case_ids_patient=None
        self.case_ids_contact=None
        self.menuIndexAllCases=-1
        self.menuIndexAllOpenCases=-1
        self.menuIndexAllClosedCases=-1
        self.menuIndexMyCases=-1
        self.menuIndexViewCaseAssignments=-1
        self.menuIndexAllContacts=-1
        self.menuIndexAllOpenContacts=-1
        self.menuIndexAllClosedContacts=-1
        self.menuIndexMyContacts=-1
        self.menuIndexViewContactAssignments=-1
        self.menuIndexSearchAdmitClientForm=-1
        self.menuIndexNewSearchAllCasesForm=-1
        self.menuIndexNewSearchAllContactsForm=-1
        self.menuIndexBUCases=-1
        self.menuIndexBUContacts=-1
        self.menuIndexMyTeam=-1
        self.menuIndexRNCNoIndex=-1
        self.menuIndexRNCase=-1
        self.subMenuIndexCI=-1
        self.subMenuIndexAssignCase=-1
        self.subMenuIndexClosePatient=-1
        self.subMenuIndexSearchDuplicatePatient=-1
        self.subMenuIndexIdentifyDuplicatePatient=-1
        self.subMenuIndexCM=-1
        self.subMenuIndexAssignContact=-1
        self.subMenuIndexCloseContact=-1
        self.subMenuIndexSearchDuplicateContact=-1
        self.subMenuIndexIdentifyDuplicateContact=-1
        self.subMenuIndexRNC=-1
        self.subMenuIndexBUCases=-1
        self.subMenuIndexBUContacts=-1
        ## get domain user credential and app config info
        with open(self.user.app_config) as json_file:
            data = json.load(json_file)
            self.CASE_LIST_FILTER=data['CASE_LIST_FILTER']
            self.SEARCH_NAMES=data['SEARCH_NAMES']
            self.FUNC_MAIN_SCREEN=data['FUNC_MAIN_SCREEN']
            if 'FUNC_USER_CHECK_IN_FORM' in data:
                self.FUNC_USER_CHECK_IN_FORM=data['FUNC_USER_CHECK_IN_FORM']
            if 'FUNC_USER_CHECK_IN_FORM_SUBMIT' in data:
                self.FUNC_USER_CHECK_IN_FORM_SUBMIT=data['FUNC_USER_CHECK_IN_FORM_SUBMIT']
            if 'FUNC_ALL_CASES_CASE_LIST' in data:
                self.FUNC_ALL_CASES_CASE_LIST=data['FUNC_ALL_CASES_CASE_LIST']
            if 'FUNC_ALL_OPEN_CASES_CASE_LIST' in data:
                self.FUNC_ALL_OPEN_CASES_CASE_LIST=data['FUNC_ALL_OPEN_CASES_CASE_LIST']
            if 'FUNC_ALL_CLOSED_CASES_CASE_LIST' in data:
                self.FUNC_ALL_CLOSED_CASES_CASE_LIST=data['FUNC_ALL_CLOSED_CASES_CASE_LIST']
            if 'FUNC_MY_CASES_CASE_LIST' in data:
                self.FUNC_MY_CASES_CASE_LIST=data['FUNC_MY_CASES_CASE_LIST']
            if 'FUNC_VIEW_CASE_ASSIGNMENTS_CASE_LIST' in data:
                self.FUNC_VIEW_CASE_ASSIGNMENTS_CASE_LIST=data['FUNC_VIEW_CASE_ASSIGNMENTS_CASE_LIST']
            if 'FUNC_ALL_CONTACTS_CASE_LIST' in data:
                self.FUNC_ALL_CONTACTS_CASE_LIST=data['FUNC_ALL_CONTACTS_CASE_LIST']
            if 'FUNC_ALL_OPEN_CONTACTS_CASE_LIST' in data: 
                self.FUNC_ALL_OPEN_CONTACTS_CASE_LIST=data['FUNC_ALL_OPEN_CONTACTS_CASE_LIST']
            if 'FUNC_ALL_CLOSED_CONTACTS_CASE_LIST' in data: 
                self.FUNC_ALL_CLOSED_CONTACTS_CASE_LIST=data['FUNC_ALL_CLOSED_CONTACTS_CASE_LIST']
            if 'FUNC_MY_CONTACTS_CASE_LIST' in data:
                self.FUNC_MY_CONTACTS_CASE_LIST=data['FUNC_MY_CONTACTS_CASE_LIST']
            if 'FUNC_VIEW_CONTACT_ASSIGNMENTS_CASE_LIST' in data:
                self.FUNC_VIEW_CONTACT_ASSIGNMENTS_CASE_LIST=data['FUNC_VIEW_CONTACT_ASSIGNMENTS_CASE_LIST']
            if 'FUNC_NEW_SEARCH_ALL_CASES_FORM' in data: 
                self.FUNC_NEW_SEARCH_ALL_CASES_FORM=data['FUNC_NEW_SEARCH_ALL_CASES_FORM']
            if 'FUNC_NEW_SEARCH_ALL_CASES' in data: 
                self.FUNC_NEW_SEARCH_ALL_CASES=data['FUNC_NEW_SEARCH_ALL_CASES']
            if 'FUNC_NEW_SEARCH_ALL_CONTACTS_FORM' in data: 
                self.FUNC_NEW_SEARCH_ALL_CONTACTS_FORM=data['FUNC_NEW_SEARCH_ALL_CONTACTS_FORM']
            if 'FUNC_NEW_SEARCH_ALL_CONTACTS' in data: 
                self.FUNC_NEW_SEARCH_ALL_CONTACTS=data['FUNC_NEW_SEARCH_ALL_CONTACTS']
            if 'FUNC_ALL_CASES_CASE_DETAILS' in data: 
                self.FUNC_ALL_CASES_CASE_DETAILS=data['FUNC_ALL_CASES_CASE_DETAILS']
            if 'FUNC_ALL_CASES_CASE_DETAILS_SUBMIT' in data: 
                self.FUNC_ALL_CASES_CASE_DETAILS_SUBMIT=data['FUNC_ALL_CASES_CASE_DETAILS_SUBMIT']
            if 'FUNC_CI_FORM' in data: 
                self.FUNC_CI_FORM=data['FUNC_CI_FORM']
            if 'FUNC_CI_FORM_QUESTIONS' in data: 
                self.FUNC_CI_FORM_QUESTIONS=data['FUNC_CI_FORM_QUESTIONS']
            if 'FUNC_CI_FORM_SUBMIT' in data: 
                self.FUNC_CI_FORM_SUBMIT=data['FUNC_CI_FORM_SUBMIT']
            if 'FUNC_ASSIGN_CASE_FORM' in data: 
                self.FUNC_ASSIGN_CASE_FORM=data['FUNC_ASSIGN_CASE_FORM']
            if 'FUNC_ASSIGN_CASE_FORM_QUESTIONS' in data: 
                self.FUNC_ASSIGN_CASE_FORM_QUESTIONS=data['FUNC_ASSIGN_CASE_FORM_QUESTIONS']
            if 'FUNC_ASSIGN_CASE_FORM_SUBMIT' in data: 
                self.FUNC_ASSIGN_CASE_FORM_SUBMIT=data['FUNC_ASSIGN_CASE_FORM_SUBMIT']
            if 'FUNC_CLOSE_PATIENT_RECORD_FORM' in data: 
                self.FUNC_CLOSE_PATIENT_RECORD_FORM=data['FUNC_CLOSE_PATIENT_RECORD_FORM']
            if 'FUNC_CLOSE_PATIENT_RECORD_FORM_QUESTIONS' in data: 
                self.FUNC_CLOSE_PATIENT_RECORD_FORM_QUESTIONS=data['FUNC_CLOSE_PATIENT_RECORD_FORM_QUESTIONS']
            if 'FUNC_CLOSE_PATIENT_RECORD_FORM_SUBMIT' in data: 
                self.FUNC_CLOSE_PATIENT_RECORD_FORM_SUBMIT=data['FUNC_CLOSE_PATIENT_RECORD_FORM_SUBMIT']
            if 'FUNC_ALL_CONTACTS_CASE_DETAILS' in data: 
                self.FUNC_ALL_CONTACTS_CASE_DETAILS=data['FUNC_ALL_CONTACTS_CASE_DETAILS']
            if 'FUNC_ALL_CONTACTS_CASE_DETAILS_SUBMIT' in data:
                self.FUNC_ALL_CONTACTS_CASE_DETAILS_SUBMIT=data['FUNC_ALL_CONTACTS_CASE_DETAILS_SUBMIT']
            if 'FUNC_CM_FORM' in data: 
                self.FUNC_CM_FORM=data['FUNC_CM_FORM']
            if 'FUNC_CM_FORM_QUESTIONS' in data:
                self.FUNC_CM_FORM_QUESTIONS=data['FUNC_CM_FORM_QUESTIONS']
            if 'FUNC_CM_FORM_SUBMIT' in data: 
                self.FUNC_CM_FORM_SUBMIT=data['FUNC_CM_FORM_SUBMIT']


            if 'FUNC_SEARCH_FOR_DUPLICATE_PATIENT_FORM' in data:
                self.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_FORM=data['FUNC_SEARCH_FOR_DUPLICATE_PATIENT_FORM']
            if 'FUNC_SEARCH_FOR_DUPLICATE_PATIENT_SUBMIT' in data:
                self.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_SUBMIT=data['FUNC_SEARCH_FOR_DUPLICATE_PATIENT_SUBMIT']
            if 'FUNC_SEARCH_FOR_DUPLICATE_PATIENT_CASE_DETAILS' in data:
                self.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_CASE_DETAILS=data['FUNC_SEARCH_FOR_DUPLICATE_PATIENT_CASE_DETAILS']
            if 'FUNC_SEARCH_FOR_DUPLICATE_PATIENT_CASE_DETAILS_SUBMIT' in data:
                self.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_CASE_DETAILS_SUBMIT=data['FUNC_SEARCH_FOR_DUPLICATE_PATIENT_CASE_DETAILS_SUBMIT']
            if 'FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM' in data:
                self.FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM=data['FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM']
            if 'FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM_QUESTIONS' in data:
                self.FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM_QUESTIONS=data['FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM_QUESTIONS']
            if 'FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM_SUBMIT' in data:
                self.FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM_SUBMIT=data['FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM_SUBMIT']



            if 'FUNC_ASSIGN_CONTACT_FORM' in data: 
                self.FUNC_ASSIGN_CONTACT_FORM=data['FUNC_ASSIGN_CONTACT_FORM']
            if 'FUNC_ASSIGN_CONTACT_FORM_QUESTIONS' in data: 
                self.FUNC_ASSIGN_CONTACT_FORM_QUESTIONS=data['FUNC_ASSIGN_CONTACT_FORM_QUESTIONS']
            if 'FUNC_ASSIGN_CONTACT_FORM_SUBMIT' in data: 
                self.FUNC_ASSIGN_CONTACT_FORM_SUBMIT=data['FUNC_ASSIGN_CONTACT_FORM_SUBMIT']
            if 'FUNC_CLOSE_CONTACT_RECORD_FORM' in data: 
                self.FUNC_CLOSE_CONTACT_RECORD_FORM=data['FUNC_CLOSE_CONTACT_RECORD_FORM']
            if 'FUNC_CLOSE_CONTACT_RECORD_FORM_QUESTIONS' in data: 
                self.FUNC_CLOSE_CONTACT_RECORD_FORM_QUESTIONS=data['FUNC_CLOSE_CONTACT_RECORD_FORM_QUESTIONS']
            if 'FUNC_CLOSE_CONTACT_RECORD_FORM_SUBMIT' in data: 
                self.FUNC_CLOSE_CONTACT_RECORD_FORM_SUBMIT=data['FUNC_CLOSE_CONTACT_RECORD_FORM_SUBMIT']
            if 'FUNC_RNC_FORM' in data: 
                self.FUNC_RNC_FORM=data['FUNC_RNC_FORM']
            if 'FUNC_RNC_FORM_QUESTIONS' in data:
                self.FUNC_RNC_FORM_QUESTIONS=data['FUNC_RNC_FORM_QUESTIONS']
            if 'FUNC_RNC_FORM_SUBMIT' in data:
                self.FUNC_RNC_FORM_SUBMIT=data['FUNC_RNC_FORM_SUBMIT']
            if 'FUNC_BU_CONTACTS_FORM' in data:
                self.FUNC_BU_CONTACTS_FORM=data['FUNC_BU_CONTACTS_FORM']
            if 'FUNC_BU_CONTACTS_FORM_QUESTIONS' in data:
                self.FUNC_BU_CONTACTS_FORM_QUESTIONS=data['FUNC_BU_CONTACTS_FORM_QUESTIONS']
            if 'FUNC_BU_CONTACTS_FORM_SUBMIT' in data:
                self.FUNC_BU_CONTACTS_FORM_SUBMIT=data['FUNC_BU_CONTACTS_FORM_SUBMIT']
            if 'FUNC_UPDATE_CONTACTS_FORM_SUBMIT' in data:
                self.FUNC_UPDATE_CONTACTS_FORM_SUBMIT=data['FUNC_UPDATE_CONTACTS_FORM_SUBMIT']
            if 'FUNC_BU_CASES_FORM' in data:
                self.FUNC_BU_CASES_FORM=data['FUNC_BU_CASES_FORM']
            if 'FUNC_BU_CASES_FORM_QUESTIONS' in data:
                self.FUNC_BU_CASES_FORM_QUESTIONS=data['FUNC_BU_CASES_FORM_QUESTIONS']
            if 'FUNC_BU_CASES_FORM_SUBMIT' in data:
                self.FUNC_BU_CASES_FORM_SUBMIT=data['FUNC_BU_CASES_FORM_SUBMIT']
            if 'FUNC_UPDATE_CASES_FORM_SUBMIT' in data:
                self.FUNC_UPDATE_CASES_FORM_SUBMIT=data['FUNC_UPDATE_CASES_FORM_SUBMIT']
            if 'FUNC_MY_TEAM_FORM' in data: 
                self.FUNC_MY_TEAM_FORM=data['FUNC_MY_TEAM_FORM']
            if 'FUNC_MY_TEAM_FORM_QUESTIONS' in data:
                self.FUNC_MY_TEAM_FORM_QUESTIONS=data['FUNC_MY_TEAM_FORM_QUESTIONS']
            if 'FUNC_MY_TEAM_FORM_SUBMIT' in data:
                self.FUNC_MY_TEAM_FORM_SUBMIT=data['FUNC_MY_TEAM_FORM_SUBMIT']
            if 'FUNC_RNC_NO_INDEX_FORM' in data: 
                self.FUNC_RNC_NO_INDEX_FORM=data['FUNC_RNC_NO_INDEX_FORM']
            if 'FUNC_RNC_NO_INDEX_FORM_QUESTIONS' in data:
                self.FUNC_RNC_NO_INDEX_FORM_QUESTIONS=data['FUNC_RNC_NO_INDEX_FORM_QUESTIONS']
            if 'FUNC_RNC_NO_INDEX_FORM_SUBMIT' in data:
                self.FUNC_RNC_NO_INDEX_FORM_SUBMIT=data['FUNC_RNC_NO_INDEX_FORM_SUBMIT']
            if 'FUNC_RNCASE_FORM' in data: 
                self.FUNC_RNCASE_FORM=data['FUNC_RNCASE_FORM']
            if 'FUNC_RNCASE_FORM_QUESTIONS' in data:
                self.FUNC_RNCASE_FORM_QUESTIONS=data['FUNC_RNCASE_FORM_QUESTIONS']
            if 'FUNC_RNCASE_FORM_SUBMIT' in data:
                self.FUNC_RNCASE_FORM_SUBMIT=data['FUNC_RNCASE_FORM_SUBMIT']



            if 'FUNC_SEARCH_ADMIT_CLIENT_FORM' in data:
                self.FUNC_SEARCH_ADMIT_CLIENT_FORM=data['FUNC_SEARCH_ADMIT_CLIENT_FORM']
            if 'FUNC_REQUEST_ADMISSION_REVIEW' in data:
                self.FUNC_REQUEST_ADMISSION_REVIEW=data['FUNC_REQUEST_ADMISSION_REVIEW']
            if 'FUNC_REQUEST_ADMISSION_REVIEW_QUESTIONS' in data:
                self.FUNC_REQUEST_ADMISSION_REVIEW_QUESTIONS=data['FUNC_REQUEST_ADMISSION_REVIEW_QUESTIONS']
            if 'FUNC_REQUEST_ADMISSION_REVIEW_SUBMIT' in data:
                self.FUNC_REQUEST_ADMISSION_REVIEW_SUBMIT=data['FUNC_REQUEST_ADMISSION_REVIEW_SUBMIT']
        self._log_in()
        self._get_build_info()
        self._get_navigate_menu_start()
        self._get_app_source_info()


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


    def _get_navigate_menu_start(self):
        logging.info("_get_navigate_menu_start")
        data = self._formplayer_post("navigate_menu_start", name="navigate menu start", checkKey="title", checkValue=self.FUNC_MAIN_SCREEN['title'])
        assert(data['title'] == self.FUNC_MAIN_SCREEN['title'])
        self.menuInfo=data['commands']
        ###menuIndex=self._get_menu_index(self.FUNC_USER_CHECK_IN_FORM['title'])
        ###if (menuIndex==0):
        ###    ## do checkin
        ###    self._user_check_in_form(menuIndex)


    def _get_menu_index(self,title):
        menuIndex=-1 
        for menu in self.menuInfo:
            if menu['displayText']==title:
                menuIndex=menu['index']
        logging.info("_get_menu_index::index::"+str(menuIndex)+"::title::"+title)
        return menuIndex


    def _get_sub_menu_index(self,title,subMenuInfo):
        logging.info("_get_sub_menu_index::title::"+title)
        subMenuIndex=-1
        for menu in subMenuInfo:
            if menu['displayText']==title:
                subMenuIndex=menu['index']
        return subMenuIndex


    """
    def _user_check_out_form(self):
        logging.info("_user_check_out_form")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.FUNC_USER_CHECK_OUT_FORM['selections']],
        }, name="User CheckOut Form")
        ###logging.info("data--->>>>>"+str(data))
        if data['title']!=self.FUNC_USER_CHECK_OUT_FORM['title']:
            self._user_check_in_form()
     """


    def _user_check_in_form(self, menuIndex):
        logging.info("_user_check_in_form")
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [menuIndex],
        }, name="User CheckIn Form")
        assert(data['title'] == self.FUNC_USER_CHECK_IN_FORM['title'])
        self.questionTree=data['tree']
        self.session_id=data['session_id']
        logging.info("sessionId--->>>"+self.session_id)
        self._user_check_in_form_submit()
        """
        try:
            self.session_id=data['session_id']
            logging.info("_user_check_in_form::sessionId::"+self.session_id)
        except (IndexError, KeyError, TypeError):
            self.session_id=''
            logging.info("_user_check_in_form::sessionId empty - skip check in")
        """


    def _user_check_in_form_submit(self):
        logging.info("_user_check_in_form_submit")
        questionString=self._build_question_lists_form_submit(True,"",self.FUNC_USER_CHECK_IN_FORM['title'],self.questionTree,"")
        questionString=self._build_question_str_process(questionString)
        jsonAnswer = json.loads(questionString)
        data = self._formplayer_post("submit-all", extra_json={
            ###"answers": {self.FUNC_USER_CHECK_IN_FORM_SUBMIT['answers-key']: [self.FUNC_USER_CHECK_IN_FORM_SUBMIT['answers-value']]},
            "answers": jsonAnswer,
            "prevalidated": True,
            "debuggerEnabled": True,
            "session_id":self.session_id,
        }, name="User CheckIn Form Submit")
        assert(data['submitResponseMessage'] == self.FUNC_USER_CHECK_IN_FORM_SUBMIT['submitResponseMessage'])
        self._get_navigate_menu_start()


    """
    "required":1 && "type":"question" && !("datatype":"info" || !"datatype":null)
    if answer":[1] (has value), skip
    if "datatype":"multiselect", take the first choice
    """
    def _build_question_lists_form_submit(self,forSubmitAll,questionString,title,questionTree,sessionId):
        #logging.info("_build_question_lists_form_submit::title::"+title)
        for tree in questionTree:
            required=tree['required']
            type=tree['type']
            dataType=tree['datatype']
            answer=tree['answer']
            choices=tree['choices']
            ix=tree['ix']
            caption=tree['caption']
            if ("children" in tree):
                children=tree['children']
                ##logging.info("children--->>"+str(children))
                if (len(children)>0):
                    questionString=self._build_question_lists_form_submit(forSubmitAll,questionString,title,children,sessionId)
                    ##logging.info("qString-->"+str(qString))
            if (required==1 and type=='question' and not(dataType=='info' or dataType==None)):
                if answer==None:
                    if (forSubmitAll):
                        questionString=self._get_answer_string(dataType,ix,choices,questionString)
                    else:
                        self._get_answer_string2(dataType,ix,choices,sessionId,caption)
                else:   ## answer!=None
                    pass
            #logging.info("====")
            ##logging.info("t--->>"+str(tree))
            #logging.info("t1--->>"+str(required))
            #logging.info("t2--->>"+str(type))
            #logging.info("t3--->>"+str(dataType))
            #logging.info("t4--->>"+str(answer))
            #logging.info("t5--->>"+str(choices))
            #logging.info("t6--->>"+str(ix))
            #logging.info("t7--->>"+str(caption)+"<==")
        #logging.info("questionString==>>>>>>"+questionString+"<==")
        return questionString


    def _get_answer_string(self,dataType,ix,choices,questionString):
        if (dataType=='multiselect' and choices!=None):
            questionString+="\""+ix+"\""+":[\"1\"],"
        elif (dataType=='select' and choices!=None):
            questionString+="\""+ix+"\""+":\"1\","
        elif (dataType=='str'):
            questionString+="\""+ix+"\""+":\"test\","
        elif (dataType=='date'):
            questionString+="\""+ix+"\""+":\"2021-05-05\","
        return questionString


    def _get_answer_string2(self,dataType,ix,choices,sessionId,caption):
        logging.info("_get_answer_string2::question::"+str(caption)+"::ix::"+ix)
        if (dataType=='multiselect' and choices!=None):
            self._form_questions(ix,"1",sessionId)
        elif (dataType=='select' and choices!=None):
            self._form_questions(ix,"1",sessionId)
        elif (dataType=='str'):
            self._form_questions(ix,"test",sessionId)
        elif (dataType=='date'):
            self._form_questions(ix,"2021-05-05",sessionId)


    def _form_questions(self,ix,answer,sessionId):
        data = self._formplayer_post("answer", extra_json={
            "answer": answer,
            "ix": ix,
            "debuggerEnabled": True,
            "session_id": sessionId,
        }, name="form submit questions")


    def _build_question_str_process(self, str):
        if (str==""):
            str="{}"
        else:
            str=str.rstrip(str[-1])
            str="{"+str+"}"
        return str


    def _build_question_lists(self,question,questionTree):
        logging.info("_build_question_lists::question::"+question)
        for tree in questionTree:
            required=tree['required']
            type=tree['type']
            dataType=tree['datatype']
            answer=tree['answer']
            choices=tree['choices']
            ix=tree['ix']
            caption=tree['caption']
            if ("children" in tree):
                children=tree['children']
                ##logging.info("children--->>"+str(children))
                if (len(children)>0):
                    d_sub=self._build_question_lists(question,children)
                    ##logging.info("d_sub-->"+str(d_sub))
                    if (d_sub!=None):
                        return d_sub
            #logging.info("====")
            ##logging.info("t--->>"+str(tree))
            #logging.info("t1--->>"+str(required))
            #logging.info("t2--->>"+str(type))
            #logging.info("t3--->>"+str(dataType))
            #logging.info("t4--->>"+str(answer))
            #logging.info("t5--->>"+str(choices))
            #logging.info("t6--->>"+str(ix))
            #logging.info("t7--->>"+str(caption))
            if (caption==question or (choices!=None and question in choices)):
                if answer==None:
                    if (dataType=='multiselect' and choices!=None):
                        answer=1
                    elif (dataType=='select' and choices!=None):
                        answer=1
                    elif (dataType=='str'):
                        answer="test"
                    elif (dataType=='date'):
                        answer="2021-05-05"
                    else:
                        answer=None
                else:
                    pass
                d=dict()
                d['ix']=ix
                d['answer']=answer
                ##logging.info("222--"+str(d))
                return d


    def _get_app_source_info(self):
        logging.info("_get_app_source_info")
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
        local_filter=self.CASE_LIST_FILTER['all_cases_filter'] if self.CASE_LIST_FILTER['all_cases_filter']!='' else str(self.all_cases_module['case_details']['short']['filter'])
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
        if (self.case_ids_patient==None):
            self._get_all_cases_filter()
            self._get_all_cases_ids()
        #return random.choice(self.case_ids_patient)
        return next(self.case_ids_patient)


    def _get_all_contacts_filter(self):
        logging.info("_get_all_contacts_filter")
        local_filter=self.CASE_LIST_FILTER['all_contacts_filter']
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
        if (self.case_ids_contact==None):
            self._get_all_contacts_filter()
            self._get_all_contacts_ids()
        return next(self.case_ids_contact)


    @tag('all', 'main_screen', 'bha')
    @task(1)
    def main_screen(self):
        logging.info("main_screen")
        data = self._formplayer_post("navigate_menu_start", name="Main Screen", checkKey="title", checkValue=self.FUNC_MAIN_SCREEN['title'])
        assert(data['title'] == self.FUNC_MAIN_SCREEN['title'])


    @tag('all', 'search_and_admit_client', 'bha')
    @task(2)
    class SearchAdmitClient(SequentialTaskSet):
        @task
        def search_admit_client_form(self):
            logging.info("search-and-admit-client==search_admit_client_form")
            ## get module index number
            if (self.parent.menuIndexSearchAdmitClientForm==-1):
                self.parent.menuIndexSearchAdmitClientForm=self.parent._get_menu_index(self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['title'])
            if (self.parent.menuIndexSearchAdmitClientForm==-1):
                logging.info("skip -- "+self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['title'])
                self.interrupt()
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections" : [self.parent.menuIndexSearchAdmitClientForm],
                },
                name="Search and Admit New Client Form", checkKey="title", checkValue=self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['title2'])
            self.queryKey=data['queryKey']
            assert(data["title"] == self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['title2'])


        @task
        def search_admit_client(self):
            logging.info("search-and-admit-client==search_admit_client")
            ###search_value = random.choice(self.parent.SEARCH_NAMES)
            ###logging.info("new-case-searach==new_search_all_cases::search_term::"+search_value)
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "query_data": {
                    self.queryKey: { "inputs": {"first_name": self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['first_name'], "last_name": self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['last_name'], "dob": self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['dob'], "consent_collected": self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['consent_collected']}, "execute": True }
                },
                "selections" : [self.parent.menuIndexSearchAdmitClientForm],
                "cases_per_page" : 100,
            }, name="Search and Admit New Client", checkKey="title", checkValue=self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['title'])
            ###logging.info("ddaaa---->>>"+str(data))
            if not ("entities" in data):
                logging.info("entities not found")
                self.interrupt()

            ##self.entitiesIds=data['entities']['id']
            ent_ids=[]
            for entry in data['entities']:
                ###logging.info("ent==>>"+str(entry))
                ent_ids.append(entry['id'])
            self.entitiesIds = ent_ids
            assert('entities' in data)
            assert(data["title"] == self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['title'])


        @task
        def request_admission_review_form(self):
            logging.info("search-and-admit-client==request_admission_review_form::"+"self.entitiesIds--"+str(self.entitiesIds))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "query_data": {
                    self.queryKey: { "inputs": {"first_name": self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['first_name'], "last_name": self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['last_name'], "dob": self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['dob'], "consent_collected": self.parent.FUNC_SEARCH_ADMIT_CLIENT_FORM['consent_collected']}, "execute": True }
                },
                "selected_values": self.entitiesIds,
                "selections": [self.parent.menuIndexSearchAdmitClientForm, "use_selected_values"],
            }, name="Request Admission Form", checkKey="title", checkValue=self.parent.FUNC_REQUEST_ADMISSION_REVIEW['title'])
            ###logging.info("ddaaa---->>>"+str(data))
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("ddaaa---->>>"+str(data['title']))
            logging.info("search-and-admit-client==request_admission_review_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_REQUEST_ADMISSION_REVIEW['title'])
            assert('instanceXml' in data)


        @task
        def request_admission_review_submit_questions(self):
            logging.info("search-and-admit-client==request_admission_review_questions_submit")
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_REQUEST_ADMISSION_REVIEW['title'],self.questionTree,self.session_id)
            #questionString=self.parent._build_question_str_process(questionString)
            #jsonAnswer = json.loads(questionString)


        @task
        def request_admission_form_submit(self):
            logging.info("search-and-admit-client==request_admission_form_submit")
            #questionString=self.parent._build_question_lists_form_submit(True,"",self.parent.FUNC_REQUEST_ADMISSION_REVIEW['title'],self.questionTree,self.session_id)
            #questionString=self.parent._build_question_str_process(questionString)
            #jsonAnswer = json.loads(questionString)
            data = self.parent._formplayer_post("submit-all", extra_json={
                #"answers": jsonAnswer,
                "answers": { },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Request Admission Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_REQUEST_ADMISSION_REVIEW_SUBMIT['submitResponseMessage'])
            #logging.info("ddaaa---->>>"+str(data))
            assert(data['submitResponseMessage'] == self.parent.FUNC_REQUEST_ADMISSION_REVIEW_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()

















    @tag('all', 'all_cases_case_list')
    @task
    def all_cases_case_list(self):
        logging.info("all_cases_case_list")
        ## get module index number
        if (self.menuIndexAllCases==-1):
            self.menuIndexAllCases=self._get_menu_index(self.FUNC_ALL_CASES_CASE_LIST['title'])
        if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.menuIndexAllCases==-1):
            logging.info("skip -- "+self.FUNC_ALL_CASES_CASE_LIST['title']+" for "+self.user.usertype+" user")
            return
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.menuIndexAllCases],
        }, name="All Cases Case List", checkKey="title", checkValue=self.FUNC_ALL_CASES_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_CASES_CASE_LIST['title'])
        ## assert(len(data['entities']))       # should return at least one case


    @tag('all', 'all_open_cases_case_list')
    @task
    def all_open_cases_case_list(self):
        logging.info("all_open_cases_case_list")
        ## get module index number
        if (self.menuIndexAllOpenCases==-1):
            self.menuIndexAllOpenCases=self._get_menu_index(self.FUNC_ALL_OPEN_CASES_CASE_LIST['title'])
        if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.menuIndexAllOpenCases==-1):
            logging.info("skip -- "+self.FUNC_ALL_OPEN_CASES_CASE_LIST['title']+" for "+self.user.usertype+" user")
            return
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.menuIndexAllOpenCases],
        }, name="All Open Cases Case List", checkKey="title", checkValue=self.FUNC_ALL_OPEN_CASES_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_OPEN_CASES_CASE_LIST['title'])
        ## assert(len(data['entities']))       # should return at least one case


    @tag('all', 'all_closed_cases_case_list')
    @task
    def all_closed_cases_case_list(self):
        logging.info("all_closed_cases_case_list")
        ## get module index number
        if (self.menuIndexAllClosedCases==-1):
            self.menuIndexAllClosedCases=self._get_menu_index(self.FUNC_ALL_CLOSED_CASES_CASE_LIST['title'])
        if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.menuIndexAllClosedCases==-1):
            logging.info("skip -- "+self.FUNC_ALL_CLOSED_CASES_CASE_LIST['title']+" for "+self.user.usertype+" user")
            return
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.menuIndexAllClosedCases],
        }, name="All Closed Cases Case List", checkKey="title", checkValue=self.FUNC_ALL_CLOSED_CASES_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_CLOSED_CASES_CASE_LIST['title'])
        ## assert(len(data['entities']))       # should return at least one case


    @tag('all', 'my_cases_case_list')
    @task
    def my_cases_case_list(self):
        logging.info("my_cases_case_list")
        ## get module index number
        if (self.menuIndexMyCases==-1):
            self.menuIndexMyCases=self._get_menu_index(self.FUNC_MY_CASES_CASE_LIST['title'])
        if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.menuIndexMyCases==-1):
            logging.info("skip -- "+self.FUNC_MY_CASES_CASE_LIST['title']+" for "+self.user.usertype+" user")
            return
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.menuIndexMyCases],
        }, name="My Cases Case List", checkKey="title", checkValue=self.FUNC_MY_CASES_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_MY_CASES_CASE_LIST['title'])


    @tag('all', 'view_case_assignments_case_list')
    @task
    def view_case_assignments_case_list(self):
        logging.info("view_case_assignments_case_list")
        ## get module index number
        if (self.menuIndexViewCaseAssignments==-1):
            self.menuIndexViewCaseAssignments=self._get_menu_index(self.FUNC_VIEW_CASE_ASSIGNMENTS_CASE_LIST['title'])
        if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.menuIndexViewCaseAssignments==-1):
            logging.info("skip -- "+self.FUNC_VIEW_CASE_ASSIGNMENTS_CASE_LIST['title']+" for "+self.user.usertype+" user")
            return
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.menuIndexViewCaseAssignments],
        }, name="My Cases Case List", checkKey="title", checkValue=self.FUNC_VIEW_CASE_ASSIGNMENTS_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_VIEW_CASE_ASSIGNMENTS_CASE_LIST['title'])


    @tag('all', 'all_contacts_case_list')
    @task
    def all_contacts_case_list(self):
        logging.info("all_contacts_case_list")
        ## get module index number
        if (self.menuIndexAllContacts==-1):
            self.menuIndexAllContacts=self._get_menu_index(self.FUNC_ALL_CONTACTS_CASE_LIST['title'])
        if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.menuIndexAllContacts==-1):
            logging.info("skip -- "+self.FUNC_ALL_CONTACTS_CASE_LIST['title']+" for "+self.user.usertype+" user")
            return
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.menuIndexAllContacts],
        }, name="All Contacts Case List", checkKey="title", checkValue=self.FUNC_ALL_CONTACTS_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_CONTACTS_CASE_LIST['title'])
        ## assert(len(data['entities']))       # should return at least one case


    @tag('all', 'all_open_contacts_case_list')
    @task
    def all_open_contacts_case_list(self):
        logging.info("all_open_contacts_case_list")
        ## get module index number
        if (self.menuIndexAllOpenContacts==-1):
            self.menuIndexAllOpenContacts=self._get_menu_index(self.FUNC_ALL_OPEN_CONTACTS_CASE_LIST['title'])
        if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.menuIndexAllOpenContacts==-1):
            logging.info("skip -- "+self.FUNC_ALL_OPEN_CONTACTS_CASE_LIST['title']+" for "+self.user.usertype+" user")
            return
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.menuIndexAllOpenContacts],
        }, name="All Open Contacts Case List", checkKey="title", checkValue=self.FUNC_ALL_OPEN_CONTACTS_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_OPEN_CONTACTS_CASE_LIST['title'])
        ## assert(len(data['entities']))       # should return at least one case


    @tag('all', 'all_closed_contacts_case_list')
    @task
    def all_closed_contacts_case_list(self):
        logging.info("all_closed_contacts_case_list")
        ## get module index number
        if (self.menuIndexAllClosedContacts==-1):
            self.menuIndexAllClosedContacts=self._get_menu_index(self.FUNC_ALL_CLOSED_CONTACTS_CASE_LIST['title'])
        if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.menuIndexAllClosedContacts==-1):
            logging.info("skip -- "+self.FUNC_ALL_CLOSED_CONTACTS_CASE_LIST['title']+" for "+self.user.usertype+" user")
            return
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.menuIndexAllClosedContacts],
        }, name="All Closed Contacts Case List", checkKey="title", checkValue=self.FUNC_ALL_CLOSED_CONTACTS_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_ALL_CLOSED_CONTACTS_CASE_LIST['title'])
        ## assert(len(data['entities']))       # should return at least one case


    @tag('all', 'my_contacts_case_list')
    @task
    def my_contacts_case_list(self):
        logging.info("my_contacts_case_list")
        ## get module index number
        if (self.menuIndexMyContacts==-1):
            self.menuIndexMyContacts=self._get_menu_index(self.FUNC_MY_CONTACTS_CASE_LIST['title'])
        if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.menuIndexMyContacts==-1):
            logging.info("skip -- "+self.FUNC_MY_CONTACTS_CASE_LIST['title']+" for "+self.user.usertype+" user")
            return
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.menuIndexMyContacts],
        }, name="My Contacts Case List", checkKey="title", checkValue=self.FUNC_MY_CONTACTS_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_MY_CONTACTS_CASE_LIST['title'])


    @tag('all', 'view_contact_assignments_case_list')
    @task
    def view_contact_assignments_case_list(self):
        logging.info("view_contact_assignments_case_list")
        ## get module index number
        if (self.menuIndexViewCaseAssignments==-1):
            self.menuIndexViewCaseAssignments=self._get_menu_index(self.FUNC_VIEW_CONTACT_ASSIGNMENTS_CASE_LIST['title'])
        if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.menuIndexViewCaseAssignments==-1):
            logging.info("skip -- "+self.FUNC_VIEW_CONTACT_ASSIGNMENTS_CASE_LIST['title']+" for "+self.user.usertype+" user")
            return
        data = self._formplayer_post("navigate_menu",extra_json={
           "selections" : [self.menuIndexViewCaseAssignments],
        }, name="My Cases Case List", checkKey="title", checkValue=self.FUNC_VIEW_CONTACT_ASSIGNMENTS_CASE_LIST['title'])
        assert(data['title'] == self.FUNC_VIEW_CONTACT_ASSIGNMENTS_CASE_LIST['title'])


    @tag('all', 'ci_form')
    @task
    # Case Investigatoin Form
    class CIFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Cases, then a case
            ## get module index number
            if (self.parent.menuIndexAllCases==-1):
                self.parent.menuIndexAllCases=self.parent._get_menu_index(self.parent.FUNC_ALL_CASES_CASE_LIST['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexAllCases==-1):
                logging.info("skip -- "+self.parent.FUNC_CI_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            self.local_case_id=self.parent._get_case_id_patient()
            logging.info("ci_form==case_details::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id],
            }, name="Case Detail for CI Form", checkKey=self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey'], checkLen=1)
            ###logging.info("data-details==="+str(data))
            assert(len(data[self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey']]))


        @task
        def case_details_submit(self):
            logging.info("ci_form==case_details_submit::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id],
            }, name="Case Detail Submit for CI Form", checkKey="title", checkValue=self.parent.FUNC_ALL_CASES_CASE_DETAILS_SUBMIT['title'])
            subMmenuInfo=data['commands']
            ## get sub module index number
            if (self.parent.subMenuIndexCI==-1):
                self.parent.subMenuIndexCI=self.parent._get_sub_menu_index(self.parent.FUNC_CI_FORM['title'],subMmenuInfo)
            assert(data['title'] == self.parent.FUNC_ALL_CASES_CASE_DETAILS_SUBMIT['title'])


        @task
        def ci_form(self):
            # Select All Cases, then a case, then Case Investiation form
            logging.info("ci_form==ci_form::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases)+"::subMenuIndexCI::"+str(self.parent.subMenuIndexCI))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                ##"selections": [self.parent.FUNC_CI_FORM['selections'], self.local_case_id, self.parent.FUNC_CI_FORM['subselections']],
                "selections": [self.parent.menuIndexAllCases, self.local_case_id, self.parent.subMenuIndexCI],
            }, name="CI Form", checkKey="title", checkValue=self.parent.FUNC_CI_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("ci_form==ci_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_CI_FORM['title'])
            assert('instanceXml' in data)


        @task
        def ci_form_questions(self):
            if self.parent.FUNC_CI_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("ci_form==ci_form_questions")
            questions=self.parent.FUNC_CI_FORM_QUESTIONS['questions']
            for q in questions: 
                #logging.info("qq1--->>>"+str(q))
                #logging.info("qq2--->>>"+q["question"])
                #logging.info("qq3--->>>"+q["title"])
                #logging.info("qq4--->>>"+q["answer"])
                #logging.info("qq5--->>>"+q["optional"])
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    return
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("ci_form==ci_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for CI Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def ci_form_submit_questions(self):
            logging.info("ci_form==ci_form_submit_questions::case_id::"+self.local_case_id)
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_CI_FORM['title'],self.questionTree,self.session_id)
            #questionString=self.parent._build_question_str_process(questionString)
            #jsonAnswer = json.loads(questionString)


        @task
        def ci_form_submit(self):
            logging.info("ci_form==ci_form_submit::case_id::"+self.local_case_id)
            #questionString=self.parent._build_question_lists_form_submit(True,"",self.parent.FUNC_CI_FORM['title'],self.questionTree,self.session_id)
            #questionString=self.parent._build_question_str_process(questionString)
            #jsonAnswer = json.loads(questionString)
            data = self.parent._formplayer_post("submit-all", extra_json={
                #"answers": jsonAnswer,
                "answers": {
                #    self.parent.FUNC_CI_FORM_SUBMIT['answers-key1']: [self.parent.FUNC_CI_FORM_SUBMIT['answers-value1']],
                #    self.parent.FUNC_CI_FORM_SUBMIT['answers-key2']: self.parent.FUNC_CI_FORM_SUBMIT['answers-value2'],
                #    self.parent.FUNC_CI_FORM_SUBMIT['answers-key3']: [self.parent.FUNC_CI_FORM_SUBMIT['answers-value3']],
                #    self.parent.FUNC_CI_FORM_SUBMIT['answers-key4']: self.parent.FUNC_CI_FORM_SUBMIT['answers-value4']
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="CI Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_CI_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_CI_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    """
    @tag('all', 'search_duplicate_contact')
    @task
    # Search for Duplicate Contact
    class SearchDeuplcatePatientFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Cases, then a case
            ## get module index number
            if (self.parent.menuIndexAllCases==-1):
                self.parent.menuIndexAllCases=self.parent._get_menu_index(self.parent.FUNC_ALL_CASES_CASE_LIST['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexAllCases==-1):
                logging.info("skip -- "+self.parent.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            self.local_case_id=self.parent._get_case_id_patient()
            logging.info("search_duplicate_patient==case_details::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id],
            }, name="Case Detail for Search for Duplicate Patients", checkKey=self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey'], checkLen=1)
            ###logging.info("data-details==="+str(data))
            assert(len(data[self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey']]))
    """





    @tag('all', 'assign_case_form')
    @task
    # Assign or Reassign the Case
    class AssignCaseFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Cases, then a case
            ## get module index number
            if (self.parent.menuIndexAllCases==-1):
                self.parent.menuIndexAllCases=self.parent._get_menu_index(self.parent.FUNC_ALL_CASES_CASE_LIST['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexAllCases==-1):
                logging.info("skip -- "+self.parent.FUNC_ASSIGN_CASE_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            self.local_case_id=self.parent._get_case_id_patient()
            logging.info("assign_case_form==case_details::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id],
            }, name="Case Detail for Assign or Reassign Case Form", checkKey=self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey'], checkLen=1)
            ###logging.info("data-details==="+str(data))
            assert(len(data[self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey']]))


        @task
        def case_details_submit(self):
            logging.info("assign_case_form==case_details_submit::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id],
            }, name="Case Detail Submit for Assign or Reassign Case Form", checkKey="title", checkValue=self.parent.FUNC_ALL_CASES_CASE_DETAILS_SUBMIT['title'])
            subMmenuInfo=data['commands']
            ## get sub module index number
            if (self.parent.subMenuIndexAssignCase==-1):
                self.parent.subMenuIndexAssignCase=self.parent._get_sub_menu_index(self.parent.FUNC_ASSIGN_CASE_FORM['title'],subMmenuInfo)
            assert(data['title'] == self.parent.FUNC_ALL_CASES_CASE_DETAILS_SUBMIT['title'])


        @task
        def assign_case_form(self):
            # Select All Cases, then a case, then Assign or Reassign Case form
            logging.info("assign_case_form==assign_case_form::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases)+"::subMenuIndexAssignCase::"+str(self.parent.subMenuIndexAssignCase))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id, self.parent.subMenuIndexAssignCase],
            }, name="Assign or Reassign Case Form", checkKey="title", checkValue=self.parent.FUNC_ASSIGN_CASE_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("assign_case_form==ci_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_ASSIGN_CASE_FORM['title'])
            assert('instanceXml' in data)


        @task
        def assign_case_form_questions(self):
            if self.parent.FUNC_ASSIGN_CASE_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("assign_case_form==ci_form_questions")
            questions=self.parent.FUNC_ASSIGN_CASE_FORM_QUESTIONS['questions']
            for q in questions:
                #logging.info("qq1--->>>"+str(q))
                #logging.info("qq2--->>>"+q["question"])
                #logging.info("qq3--->>>"+q["title"])
                #logging.info("qq4--->>>"+q["answer"])
                #logging.info("qq5--->>>"+q["optional"])
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    return
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("assign_case_form==assign_case_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for Assign or Reassign Case Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def assign_case_form_submit_questions(self):
            logging.info("assign_case_form==assign_case_form_submit_questions::case_id::"+self.local_case_id)
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_ASSIGN_CASE_FORM['title'],self.questionTree,self.session_id)
            #questionString=self.parent._build_question_str_process(questionString)
            #jsonAnswer = json.loads(questionString)


        @task
        def assign_case_form_submit(self):
            logging.info("assign_case_form==assign_case_form_submit::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": { },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Assign or Reassign Case Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_ASSIGN_CASE_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_ASSIGN_CASE_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'close_patient_record_form')
    @task
    # Close the Patient Record 
    class ClosePatientRecordFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Cases, then a case
            ## get module index number
            if (self.parent.menuIndexAllCases==-1):
                self.parent.menuIndexAllCases=self.parent._get_menu_index(self.parent.FUNC_ALL_CASES_CASE_LIST['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexAllCases==-1):
                logging.info("skip -- "+self.parent.FUNC_CLOSE_PATIENT_RECORD_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            self.local_case_id=self.parent._get_case_id_patient()
            logging.info("close_patient_record_form==case_details::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id],
            }, name="Case Detail for Close the Patient Record Form", checkKey=self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey'], checkLen=1)
            ###logging.info("data-details==="+str(data))
            assert(len(data[self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey']]))


        @task
        def case_details_submit(self):
            logging.info("close_patient_record_form==case_details_submit::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id],
            }, name="Case Detail Submit for Close the Patient Record Form", checkKey="title", checkValue=self.parent.FUNC_ALL_CASES_CASE_DETAILS_SUBMIT['title'])
            subMmenuInfo=data['commands']
            ## get sub module index number
            if (self.parent.subMenuIndexClosePatient==-1):
                self.parent.subMenuIndexClosePatient=self.parent._get_sub_menu_index(self.parent.FUNC_CLOSE_PATIENT_RECORD_FORM['title'],subMmenuInfo)
            assert(data['title'] == self.parent.FUNC_ALL_CASES_CASE_DETAILS_SUBMIT['title'])


        @task
        def close_patient_record_form(self):
            # Select All Cases, then a case, then Close the Patient Record form
            logging.info("close_patient_record_form==close_patient_record_form::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases)+"::subMenuIndexClosePatient::"+str(self.parent.subMenuIndexClosePatient))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id, self.parent.subMenuIndexClosePatient],
            }, name="Close the Patient Record Form", checkKey="title", checkValue=self.parent.FUNC_CLOSE_PATIENT_RECORD_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("close_patient_record_form==close_patient_record_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_CLOSE_PATIENT_RECORD_FORM['title'])
            assert('instanceXml' in data)


        @task
        def close_patient_record_form_questions(self):
            if self.parent.FUNC_CLOSE_PATIENT_RECORD_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("close_patient_record_form==close_patient_record_form_questions")
            questions=self.parent.FUNC_CLOSE_PATIENT_RECORD_FORM_QUESTIONS['questions']
            for q in questions:
                #logging.info("qq1--->>>"+str(q))
                #logging.info("qq2--->>>"+q["question"])
                #logging.info("qq3--->>>"+q["title"])
                #logging.info("qq4--->>>"+q["answer"])
                #logging.info("qq5--->>>"+q["optional"])
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    return
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("close_patient_record_form==close_patient_record_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for Close the Patient Record Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def close_patient_record_form_submit_questions(self):
            logging.info("close_patient_record_form==close_patient_record_form_submit_questions::case_id::"+self.local_case_id)
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_CLOSE_PATIENT_RECORD_FORM['title'],self.questionTree,self.session_id)
            #questionString=self.parent._build_question_str_process(questionString)
            #jsonAnswer = json.loads(questionString)


        @task
        def close_patient_record_form_submit(self):
            logging.info("close_patient_record_form==close_patient_record_form_submit::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": { },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Close the Patient Record Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_CLOSE_PATIENT_RECORD_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_CLOSE_PATIENT_RECORD_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'cm_form')
    @task
    # Contact Monitoring Form
    class CMFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Contacts, then a contact
            ## get module index number
            if (self.parent.menuIndexAllContacts==-1):
                self.parent.menuIndexAllContacts=self.parent._get_menu_index(self.parent.FUNC_ALL_CONTACTS_CASE_LIST['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexAllContacts==-1):
                logging.info("skip -- "+self.parent.FUNC_CM_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            self.local_contact_id=self.parent._get_case_id_contact()
            logging.info("cm_form==case_details::contact_id::"+self.local_contact_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.menuIndexAllContacts, self.local_contact_id],
            }, name="Case Detail for CM Form", checkKey=self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS['checkKey'], checkLen=1)
            ###logging.info("data-details==="+str(data))
            assert(len(data[self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS['checkKey']]))


        @task
        def case_details_submit(self):
            logging.info("cm_form==case_details_submit::contact_id::"+self.local_contact_id+"::menuIndexAllContacts::"+str(self.parent.menuIndexAllContacts))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllContacts, self.local_contact_id],
            }, name="Case Detail Submit for CM Form", checkKey="title", checkValue=self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS_SUBMIT['title'])
            subMmenuInfo=data['commands']
            ## get sub module index number
            if (self.parent.subMenuIndexCM==-1):
                self.parent.subMenuIndexCM=self.parent._get_sub_menu_index(self.parent.FUNC_CM_FORM['title'],subMmenuInfo)
            assert(data['title'] == self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS_SUBMIT['title'])


        @task
        def cm_form(self):
            # Select All Contacts, then a contact, then Case Monitoring form
            logging.info("cm_form==cm_form::contact_id::"+self.local_contact_id+"::menuIndexAllContacts::"+str(self.parent.menuIndexAllContacts)+"::subMenuIndexCM::"+str(self.parent.subMenuIndexCM))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                ##"selections": [self.parent.FUNC_CM_FORM['selections'], self.local_contact_id, self.parent.FUNC_CM_FORM['subselections']],
                "selections": [self.parent.menuIndexAllContacts, self.local_contact_id, self.parent.subMenuIndexCM],
            }, name="CM Form", checkKey="title", checkValue=self.parent.FUNC_CM_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("cm_form==cm_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_CM_FORM['title'])
            assert('instanceXml' in data)


        @task
        def cm_form_questions(self):
            if self.parent.FUNC_CM_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("cm_form==cm_form_questions")
            questions=self.parent.FUNC_CM_FORM_QUESTIONS['questions']
            for q in questions:
                #logging.info("qq1--->>>"+str(q))
                #logging.info("qq2--->>>"+q["question"])
                #logging.info("qq3--->>>"+q["title"])
                #logging.info("qq4--->>>"+q["answer"])
                #logging.info("qq5--->>>"+q["optional"])
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    continue 
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("cm_form==cm_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for CM Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def cm_form_submit_questions(self):
            logging.info("cm_form==cm_form_submit_questions::contact_id::"+self.local_contact_id)
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_CM_FORM['title'],self.questionTree,self.session_id)


        @task
        def cm_form_submit(self):
            logging.info("cm_form==cm_form_submit::contact_id::"+self.local_contact_id)
            #questionString=self.parent._build_question_lists_form_submit(True,"",self.parent.FUNC_CM_FORM['title'],self.questionTree,self.session_id)
            #questionString=self.parent._build_question_str_process(questionString)
            #jsonAnswer = json.loads(questionString)
            data = self.parent._formplayer_post("submit-all", extra_json={
                #"answers": jsonAnswer,
                "answers": {
                #    self.parent.FUNC_CM_FORM_SUBMIT['answers-key1']: [self.parent.FUNC_CM_FORM_SUBMIT['answers-value1']],
                #    self.parent.FUNC_CM_FORM_SUBMIT['answers-key2']: self.parent.FUNC_CM_FORM_SUBMIT['answers-value2']
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="CM Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_CM_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_CM_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'search_duplicate_patient')
    @task
    # Search for Duplicate Patients
    class SearchDeuplcatePatientFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Cases, then a case
            ## get module index number
            if (self.parent.menuIndexAllCases==-1):
                self.parent.menuIndexAllCases=self.parent._get_menu_index(self.parent.FUNC_ALL_CASES_CASE_LIST['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexAllCases==-1):
                logging.info("skip -- "+self.parent.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            self.local_case_id=self.parent._get_case_id_patient()
            logging.info("search_duplicate_patient==case_details::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id],
            }, name="Case Detail for Search for Duplicate Patients", checkKey=self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey'], checkLen=1)
            ###logging.info("data-details==="+str(data))
            assert(len(data[self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey']]))


        @task
        def case_details_submit(self):
            logging.info("search_duplicate_patient==case_details_submit::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id],
            }, name="Case Detail Submit for Search for Duplicate Patients", checkKey="title", checkValue=self.parent.FUNC_ALL_CASES_CASE_DETAILS_SUBMIT['title'])
            subMmenuInfo=data['commands']
            ## get sub module index number
            if (self.parent.subMenuIndexSearchDuplicatePatient==-1):
                self.parent.subMenuIndexSearchDuplicatePatient=self.parent._get_sub_menu_index(self.parent.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_FORM['title'],subMmenuInfo)
            assert(data['title'] == self.parent.FUNC_ALL_CASES_CASE_DETAILS_SUBMIT['title'])


        @task
        def search_duplicate_patient_form(self):
            # Select All Cases, then a case, then Search for Duplicate Patient
            logging.info("search_duplicate_patient==search_duplicate_patient_form::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases)+"::subMenuIndexSearchDuplicatePatient::"+str(self.parent.subMenuIndexSearchDuplicatePatient))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id, self.parent.subMenuIndexSearchDuplicatePatient],
            }, name="Search for Duplicate Patient Form", checkKey="title", checkValue=self.parent.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_FORM['title2'])
            self.queryKey=data['queryKey']
            assert(data["title"] == self.parent.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_FORM['title2'])


        @task
        def search_duplicate_patient_submit(self):
            logging.info("search_duplicate_patient==search_duplicate_patient_submit::querykey::"+self.queryKey)
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "query_data": {
                    self.queryKey: { "inputs": {}, "execute": True }
                    #"search_command.m10": { "inputs": {"first_name":"test", "last_name":"test"}, "execute": True }
                },
                "selections": [self.parent.menuIndexAllCases, self.local_case_id, self.parent.subMenuIndexSearchDuplicatePatient],
            }, name="Search for Duplicate Patient Submit", checkKey="title", checkValue=self.parent.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_SUBMIT['title'])
            if ('entities' in data):
                entities=data['entities']
                ## get the first case
                if (len(entities)>0):
                    self.duplicatePatientId=entities[0]['id']
                else:
                    logging.info("skip--no entry found")
                    self.interrupt()
            else:
                assert("error in search_duplicate_patient_submit::entities not in data")
            assert(data["title"] == self.parent.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_SUBMIT['title'])


        @task
        def case_details_search_duplicate(self):
            # Select All Cases, then a case, then Search for Duplicate Patient, then choose a case
            logging.info("search_duplicate_patient==case_details_search_duplicate::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases)+"::subMenuIndexSearchDuplicatePatient::"+str(self.parent.subMenuIndexSearchDuplicatePatient)+"::duplicatePatientId::"+str(self.duplicatePatientId))
            data = self.parent._formplayer_post("get_details", extra_json={
                "query_data": {
                    self.queryKey: { "inputs": {}, "execute": True }
                },
                "selections": [self.parent.menuIndexAllCases, self.local_case_id, self.parent.subMenuIndexSearchDuplicatePatient, self.duplicatePatientId],
            }, name="Case Detail Duplicate for Search for Duplicate Patients", checkKey=self.parent.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_CASE_DETAILS['checkKey'], checkLen=1)
            ###logging.info("data-details==="+str(data))
            assert(len(data[self.parent.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_CASE_DETAILS['checkKey']]))


        @task
        def case_details_search_duplicate_submit(self):
            logging.info("search_duplicate_patient==case_details_search_duplicate_submit::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases)+"::subMenuIndexSearchDuplicatePatient::"+str(self.parent.subMenuIndexSearchDuplicatePatient)+"::duplicatePatientId::"+str(self.duplicatePatientId))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "query_data": {
                    self.queryKey: { "inputs": {}, "execute": True }
                },
                "selections": [self.parent.menuIndexAllCases, self.local_case_id, self.parent.subMenuIndexSearchDuplicatePatient, self.duplicatePatientId],
            }, name="Case Detail Duplicate Submit for Search for Duplicate Patients", checkKey="title", checkValue=self.parent.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_CASE_DETAILS_SUBMIT['title'])
            subMmenuInfo=data['commands']
            ## get sub module index number
            if (self.parent.subMenuIndexIdentifyDuplicatePatient==-1):
                self.parent.subMenuIndexIdentifyDuplicatePatient=self.parent._get_sub_menu_index(self.parent.FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM['title'],subMmenuInfo)
            assert(data['title'] == self.parent.FUNC_SEARCH_FOR_DUPLICATE_PATIENT_CASE_DETAILS_SUBMIT['title'])


        @task
        def identify_duplicate_patient_form(self):
            # Select All Cases, then a case, then Search for Duplicate Patient, then choose a case, then Identify Duplicate Patient form
            logging.info("search_duplicate_patient==identify_duplicate_patient_form::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases)+"::subMenuIndexSearchDuplicatePatient::"+str(self.parent.subMenuIndexSearchDuplicatePatient)+"::duplicatePatientId::"+str(self.duplicatePatientId)+"::subMenuIndexIdentifyDuplicatePatient::"+str(self.parent.subMenuIndexIdentifyDuplicatePatient))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "query_data": {
                    self.queryKey: { "inputs": {}, "execute": True }
                },
                "selections": [self.parent.menuIndexAllCases, self.local_case_id, self.parent.subMenuIndexSearchDuplicatePatient, self.duplicatePatientId, self.parent.subMenuIndexIdentifyDuplicatePatient],
            }, name="Identify Deuplicate Patient form for Search for Duplicate Patients", checkKey="title", checkValue=self.parent.FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("identify_duplicate_patient_form==identify_duplicate_patient_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM['title'])
            assert('instanceXml' in data)


        @task
        def identify_duplicate_patient_form_questions(self):
            if self.parent.FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("search_duplicate_patient==identify_duplicate_patient_form_questions")
            questions=self.parent.FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM_QUESTIONS['questions']
            for q in questions:
                #logging.info("qq1--->>>"+str(q))
                #logging.info("qq2--->>>"+q["question"])
                #logging.info("qq3--->>>"+q["title"])
                #logging.info("qq4--->>>"+q["answer"])
                #logging.info("qq5--->>>"+q["optional"])
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    continue
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("search_duplicate_patient==identify_duplicate_patient_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for CM Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def identify_duplicate_patient_form_submit_questions(self):
            logging.info("search_duplicate_patient==identify_duplicate_patient_form_submit_questions::::"+self.local_case_id+"::duplicatePatientId::"+str(self.duplicatePatientId))
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM['title'],self.questionTree,self.session_id)


        @task
        def identify_duplicate_patient_form_submit(self):
            logging.info("search_duplicate_patient==identify_duplicate_patient_form_submit::::"+self.local_case_id+"::duplicatePatientId::"+str(self.duplicatePatientId))
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": { },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="CM Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_IDENTIFY_DUPLICATE_PATIENT_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'assign_contact_form')
    @task
    # Assign or Reassign the Contact
    class AssignContactFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Contacts, then a contact
            ## get module index number
            if (self.parent.menuIndexAllContacts==-1):
                self.parent.menuIndexAllContacts=self.parent._get_menu_index(self.parent.FUNC_ALL_CONTACTS_CASE_LIST['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexAllContacts==-1):
                logging.info("skip -- "+self.parent.FUNC_ASSIGN_CONTACT_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            self.local_contact_id=self.parent._get_case_id_contact()
            logging.info("assign_contact_form==case_details::contact_id::"+self.local_contact_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.menuIndexAllContacts, self.local_contact_id],
            }, name="Contact Detail for Assign or Reassign Contact Form", checkKey=self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS['checkKey'], checkLen=1)
            ###logging.info("data-details==="+str(data))
            assert(len(data[self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS['checkKey']]))


        @task
        def case_details_submit(self):
            logging.info("assign_contact_form==case_details_submit::contact_id::"+self.local_contact_id+"::menuIndexAllContacts::"+str(self.parent.menuIndexAllContacts))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllContacts, self.local_contact_id],
            }, name="Contact Detail Submit for Assign or Reassign Contact Form", checkKey="title", checkValue=self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS_SUBMIT['title'])
            subMmenuInfo=data['commands']
            ## get sub module index number
            if (self.parent.subMenuIndexAssignContact==-1):
                self.parent.subMenuIndexAssignContact=self.parent._get_sub_menu_index(self.parent.FUNC_ASSIGN_CONTACT_FORM['title'],subMmenuInfo)
            assert(data['title'] == self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS_SUBMIT['title'])


        @task
        def assign_contact_form(self):
            # Select All Contacts, then a contact, then Assign or Reassign Contact form
            logging.info("assign_contact_form==assign_contact_form::contact_id::"+self.local_contact_id+"::menuIndexAllContacts::"+str(self.parent.menuIndexAllContacts)+"::subMenuIndexAssignContact::"+str(self.parent.subMenuIndexAssignContact))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllContacts, self.local_contact_id, self.parent.subMenuIndexAssignContact],
            }, name="Assign or Reassign Contact Form", checkKey="title", checkValue=self.parent.FUNC_ASSIGN_CONTACT_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("assign_contact_form==assign_contact_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_ASSIGN_CONTACT_FORM['title'])
            assert('instanceXml' in data)


        @task
        def assign_contact_form_questions(self):
            if self.parent.FUNC_ASSIGN_CONTACT_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("assign_contact_form==assign_contact_form_questions")
            questions=self.parent.FUNC_ASSIGN_CONTACT_FORM_QUESTIONS['questions']
            for q in questions:
                #logging.info("qq1--->>>"+str(q))
                #logging.info("qq2--->>>"+q["question"])
                #logging.info("qq3--->>>"+q["title"])
                #logging.info("qq4--->>>"+q["answer"])
                #logging.info("qq5--->>>"+q["optional"])
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    return
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("assign_contact_form==assign_contact_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for Assign or Reassign Contact Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def assign_contact_form_submit_questions(self):
            logging.info("assign_contact_form==assign_contact_form_submit_questions::contact_id::"+self.local_contact_id)
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_ASSIGN_CONTACT_FORM['title'],self.questionTree,self.session_id)
            #questionString=self.parent._build_question_str_process(questionString)
            #jsonAnswer = json.loads(questionString)


        @task
        def assign_contact_form_submit(self):
            logging.info("assign_contact_form==assign_contact_form_submit::contact_id::"+self.local_contact_id)
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": { },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Assign or Reassign Contact Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_ASSIGN_CONTACT_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_ASSIGN_CONTACT_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'close_contact_record_form')
    @task
    # Close the Contact Record
    class CloseContactRecordFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Contacts, then a contact
            ## get module index number
            if (self.parent.menuIndexAllContacts==-1):
                self.parent.menuIndexAllContacts=self.parent._get_menu_index(self.parent.FUNC_ALL_CONTACTS_CASE_LIST['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexAllContacts==-1):
                logging.info("skip -- "+self.parent.FUNC_CLOSE_CONTACT_RECORD_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            self.local_contact_id=self.parent._get_case_id_contact()
            logging.info("close_contact_record_form==case_details::contact_id::"+self.local_contact_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.menuIndexAllContacts, self.local_contact_id],
            }, name="Case Detail for Close the Contact Record Form", checkKey=self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS['checkKey'], checkLen=1)
            ###logging.info("data-details==="+str(data))
            assert(len(data[self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS['checkKey']]))


        @task
        def case_details_submit(self):
            logging.info("close_contact_record_form==case_details_submit::contact_id::"+self.local_contact_id+"::menuIndexAllContacts::"+str(self.parent.menuIndexAllContacts))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllContacts, self.local_contact_id],
            }, name="Case Detail Submit for Close the Contact Record Form", checkKey="title", checkValue=self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS_SUBMIT['title'])
            subMmenuInfo=data['commands']
            ## get sub module index number
            if (self.parent.subMenuIndexCloseContact==-1):
                self.parent.subMenuIndexCloseContact=self.parent._get_sub_menu_index(self.parent.FUNC_CLOSE_CONTACT_RECORD_FORM['title'],subMmenuInfo)
            assert(data['title'] == self.parent.FUNC_ALL_CONTACTS_CASE_DETAILS_SUBMIT['title'])


        @task
        def close_contact_record_form(self):
            # Select All Contacts, then a contact, then Close the Contact Record form
            logging.info("close_contact_record_form==close_contact_record_form::contact_id::"+self.local_contact_id+"::menuIndexAllContacts::"+str(self.parent.menuIndexAllContacts)+"::subMenuIndexCloseContact::"+str(self.parent.subMenuIndexCloseContact))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllContacts, self.local_contact_id, self.parent.subMenuIndexCloseContact],
            }, name="Close the Contact Record Form", checkKey="title", checkValue=self.parent.FUNC_CLOSE_CONTACT_RECORD_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("close_contact_record_form==close_contact_record_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_CLOSE_CONTACT_RECORD_FORM['title'])
            assert('instanceXml' in data)


        @task
        def close_contact_record_form_questions(self):
            if self.parent.FUNC_CLOSE_CONTACT_RECORD_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("close_contact_record_form==close_contact_record_form_questions")
            questions=self.parent.FUNC_CLOSE_CONTACT_RECORD_FORM_QUESTIONS['questions']
            for q in questions:
                #logging.info("qq1--->>>"+str(q))
                #logging.info("qq2--->>>"+q["question"])
                #logging.info("qq3--->>>"+q["title"])
                #logging.info("qq4--->>>"+q["answer"])
                #logging.info("qq5--->>>"+q["optional"])
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    return
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("close_contact_record_form==close_contact_record_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for Close the Contact Record Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def close_contact_record_form_submit_questions(self):
            logging.info("close_contact_record_form==close_contact_record_form_submit_questions::case_id::"+self.local_contact_id)
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_CLOSE_CONTACT_RECORD_FORM['title'],self.questionTree,self.session_id)
            #questionString=self.parent._build_question_str_process(questionString)
            #jsonAnswer = json.loads(questionString)


        @task
        def close_contact_record_form_submit(self):
            logging.info("close_contact_record_form==close_contact_record_form_submit::case_id::"+self.local_contact_id)
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": { },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Close the Contact Record Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_CLOSE_CONTACT_RECORD_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_CLOSE_CONTACT_RECORD_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    """
    @tag('all', 'id-form')
    @task(1)
    # Identify Duplicate Patient
    class IDPatientEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Cases, then a case
            self.local_case_id=self.parent._get_case_id_patient()
            logging.info("id-form==case_details::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.FUNC_ALL_CASES_CASE_DETAILS['selections'], self.local_case_id],
            }, name="Case Detail for ID Form", checkKey=self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey'], checkLen=self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkLen'])
            assert(len(data['details']) == self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkLen'])


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
    """


    @tag('all', 'register_new_contact_form')
    @task(2)
    # Register New Contacts Form
    class RNCFormEntry(SequentialTaskSet):
        @task
        def case_details(self):
            # select All Cases, then a case
            ## get module index number
            if (self.parent.menuIndexAllCases==-1):
                self.parent.menuIndexAllCases=self.parent._get_menu_index(self.parent.FUNC_ALL_CASES_CASE_LIST['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexAllCases==-1):
                logging.info("skip -- "+self.parent.FUNC_RNC_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            self.local_case_id=self.parent._get_case_id_patient()
            logging.info("register_new_contact_form==case_details::case_id::"+self.local_case_id)
            data = self.parent._formplayer_post("get_details", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id],
            }, name="Case Detail for Register New Contact Form", checkKey=self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey'], checkLen=1)
            assert(len(data[self.parent.FUNC_ALL_CASES_CASE_DETAILS['checkKey']]))


        @task
        def case_details_submit(self):
            logging.info("register_new_contact_form==case_details_submit::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexAllCases, self.local_case_id],
            }, name="Case Detail Submit for Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_ALL_CASES_CASE_DETAILS_SUBMIT['title'])
            subMmenuInfo=data['commands']
            ## get sub module index number
            if (self.parent.subMenuIndexRNC==-1):
                self.parent.subMenuIndexRNC=self.parent._get_sub_menu_index(self.parent.FUNC_RNC_FORM['title'],subMmenuInfo)
            assert(data['title'] == self.parent.FUNC_ALL_CASES_CASE_DETAILS_SUBMIT['title'])


        @task
        def rnc_form(self):
            # Select All Cases, then a case, then Register New Contacts form
            logging.info("register_new_contact_form==register_new_contact_form::case_id::"+self.local_case_id+"::menuIndexAllCases::"+str(self.parent.menuIndexAllCases)+"::subMenuIndexRNC::"+str(self.parent.subMenuIndexRNC))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                ##"selections": [self.parent.FUNC_RNC_FORM['selections'], self.local_case_id, self.parent.FUNC_RNC_FORM['subselections']],
                "selections": [self.parent.menuIndexAllCases, self.local_case_id, self.parent.subMenuIndexRNC],
            }, name="Register New Contact Form", checkKey="title", checkValue=self.parent.FUNC_RNC_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("register_new_contact_form=rnc_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_RNC_FORM['title'])
            assert('instanceXml' in data)


        @task
        def rnc_form_questions(self):
            if self.parent.FUNC_RNC_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("register_new_contact_form==rnc_form_questions")
            questions=self.parent.FUNC_RNC_FORM_QUESTIONS['questions']
            for q in questions:
                #logging.info("qq1--->>>"+str(q))
                #logging.info("qq2--->>>"+q["question"])
                #logging.info("qq3--->>>"+q["title"])
                #logging.info("qq4--->>>"+q["answer"])
                #logging.info("qq5--->>>"+q["optional"])
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    return
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("register_new_contact_form==rnc_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for Register New Contact Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def rnc_form_submit_questions(self):
            logging.info("register_new_contact_form==rnc_form_submit_questions::case_id::"+self.local_case_id)
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_RNC_FORM['title'],self.questionTree,self.session_id)


        @task
        def rnc_form_submit(self):
            logging.info("register_new_contact_form==rnc_form_submit::case_id::"+self.local_case_id)
            #questionString=self.parent._build_question_lists_form_submit(True,"",self.parent.FUNC_RNC_FORM['title'],self.questionTree,self.session_id)
            #questionString=self.parent._build_question_str_process(questionString)
            #jsonAnswer = json.loads(questionString)
            #logging.info("jsonAnswer==========>>>"+str(jsonAnswer))
            data = self.parent._formplayer_post("submit-all", extra_json={
                #"answers": jsonAnswer,
                "answers": {
                #    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key1']: self.parent.FUNC_RNC_FORM_SUBMIT['answers-value1'],
                #    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key2']: self.parent.FUNC_RNC_FORM_SUBMIT['answers-value2'],
                #    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key3']: [self.parent.FUNC_RNC_FORM_SUBMIT['answers-value3']],
                #    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key4']: [self.parent.FUNC_RNC_FORM_SUBMIT['answers-value4']],
                #    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key5']: self.parent.FUNC_RNC_FORM_SUBMIT['answers-value5'],
                #    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key6']: self.parent.FUNC_RNC_FORM_SUBMIT['answers-value6'],
                #    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key7']: [self.parent.FUNC_RNC_FORM_SUBMIT['answers-value7']],
                #    self.parent.FUNC_RNC_FORM_SUBMIT['answers-key8']: self.parent.FUNC_RNC_FORM_SUBMIT['answers-value8']
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Register New Contact Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_RNC_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_RNC_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'new_case_search')
    @task(6)
    class NewCaseSearch(SequentialTaskSet):
        @task
        def new_search_all_cases_form(self):
            logging.info("new-case-search==new_search_all_cases_form")
            ## get module index number
            if (self.parent.menuIndexNewSearchAllCasesForm==-1):
                self.parent.menuIndexNewSearchAllCasesForm=self.parent._get_menu_index(self.parent.FUNC_NEW_SEARCH_ALL_CASES_FORM['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexNewSearchAllCasesForm==-1):
                logging.info("skip -- "+self.parent.FUNC_NEW_SEARCH_ALL_CASES_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections" : [self.parent.menuIndexNewSearchAllCasesForm],
                },
                name="New Case Search Form", checkKey="title", checkValue=self.parent.FUNC_NEW_SEARCH_ALL_CASES_FORM['title2'])
            self.queryKey=data['queryKey']
            assert(data["title"] == self.parent.FUNC_NEW_SEARCH_ALL_CASES_FORM['title2'])


        @task
        def new_search_all_cases(self):
            logging.info("new-case-search==new_search_all_cases")
            search_value = random.choice(self.parent.SEARCH_NAMES)
            logging.info("new-case-searach==new_search_all_cases::search_term::"+search_value)
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "query_data": {
                    self.queryKey: { "inputs": {}, "execute": True }
                },
                "selections" : [self.parent.menuIndexNewSearchAllCasesForm],
            }, name="Search All Cases", checkKey="title", checkValue=self.parent.FUNC_NEW_SEARCH_ALL_CASES['title2'])
            ###logging.info("ddaaa---->>>"+str(data))
            assert('entities' in data)
            assert(data["title"] == self.parent.FUNC_NEW_SEARCH_ALL_CASES['title2'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'new_contact_search')
    @task(6)
    class NewContactSearch(SequentialTaskSet):
        @task
        def new_search_all_contacts_form(self):
            logging.info("new-contact-search==new_search_all_contacts_form")
            ## get module index number
            if (self.parent.menuIndexNewSearchAllContactsForm==-1):
                self.parent.menuIndexNewSearchAllContactsForm=self.parent._get_menu_index(self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS_FORM['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexNewSearchAllContactsForm==-1):
                logging.info("skip -- "+self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections" : [self.parent.menuIndexNewSearchAllContactsForm],
                },
                name="Search All Contacts Form", checkKey="title", checkValue=self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS_FORM['title2'])
            self.queryKey=data['queryKey']
            assert(data["title"] == self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS_FORM['title2'])
    

        @task
        def new_search_all_contacts(self):
            logging.info("new-contact-search==new_search_all_contacts")
            search_value = random.choice(self.parent.SEARCH_NAMES)
            logging.info("new-contact-search==new_search_all_contacts::search_term::"+search_value)

            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "query_data": {
                    self.queryKey: { "inputs": {}, "execute": True }
                },
                "selections" : [self.parent.menuIndexNewSearchAllContactsForm]
            }, name="Search All Contacts", checkKey="title", checkValue=self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS['title2'])
            assert('entities' in data)
            assert(data["title"] == self.parent.FUNC_NEW_SEARCH_ALL_CONTACTS['title2'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'bulk_update_contacts')
    @task(2)
    # Bulk Update Contacts Form
    class BulkUpdateContactsFormEntry(SequentialTaskSet):
        @task
        def bulk_update_contacts_form(self):
            ## get module index number
            if (self.parent.menuIndexBUContacts==-1):
                self.parent.menuIndexBUContacts=self.parent._get_menu_index(self.parent.FUNC_BU_CONTACTS_FORM['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexBUContacts==-1):
                logging.info("skip -- "+self.parent.FUNC_BU_CONTACTS_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            logging.info("bulk_update_contacts==bulk_update_contacts_form::"+"::menuIndexBUContacts::"+str(self.parent.menuIndexBUContacts))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                #"selections": [self.parent.FUNC_BU_CONTACTS_FORM['selections']],
                "selections": [self.parent.menuIndexBUContacts],
            }, name="Bulk Update Contacts Form", checkKey="title", checkValue=self.parent.FUNC_BU_CONTACTS_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("bulk_update_contacts==bulk_update_contacts_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_BU_CONTACTS_FORM['title'])
            assert('instanceXml' in data)


        @task
        def bulk_update_contacts_form_questions(self):
            if self.parent.FUNC_BU_CONTACTS_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("bulk_update_contacts==bulk_update_contacts_form_questions")
            questions=self.parent.FUNC_BU_CONTACTS_FORM_QUESTIONS['questions']
            for q in questions:
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    return
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("bulk_update_contacts==bulk_update_contacts_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for Bulk Update Contacts Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def bulk_update_contacts_form_submit_questions(self):
            logging.info("bulk_update_contacts==bulk_update_contacts_form_submit_questions")
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_BU_CONTACTS_FORM['title'],self.questionTree,self.session_id)


        @task
        def bulk_update_contacts_form_submit(self):
            logging.info("bulk_update_contacts==bulk_update_contacts_form_submit")
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": {
                #    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-type-of-bulk']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-type-of-bulk'],
                #    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-select-without-primary']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-select-without-primary'],
                #    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-contacts-matching']: [self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-contacts-matching']],
                #    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-select-owner']: [self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-select-owner']],
                #    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-assign-action']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-assign-action'],
                #    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-update-fewer-contacts']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-update-fewer-contacts'],
                #    self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-key-number-of-updates']: self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['answers-value-number-of-updates']
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Bulk Update Contacts Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['submitResponseMessage'])
            self.session_id2=data['nextScreen']['session_id']
            logging.info("bulk_update_contacts==bulk_update_contacts_form_submit::sessionId::"+self.session_id2)
            assert(data['submitResponseMessage'] == self.parent.FUNC_BU_CONTACTS_FORM_SUBMIT['submitResponseMessage'])


        @task
        def update_contacts_form_submit(self):
            logging.info("bulk_update_contacts==update_contacts_form_submit")
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


    @tag('all', 'bulk_update_cases')
    @task(1)
    # Bulk Update Cases Form
    class BulkUpdateCasesFormEntry(SequentialTaskSet):
        @task
        def bulk_update_cases(self):
            ## get module index number
            if (self.parent.menuIndexBUCases==-1):
                self.parent.menuIndexBUCases=self.parent._get_menu_index(self.parent.FUNC_BU_CASES_FORM['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexBUCases==-1):
                logging.info("skip -- "+self.parent.FUNC_BU_CASES_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            logging.info("bulk_update_cases==bulk_update_cases_form::"+"::menuIndexBUCases::"+str(self.parent.menuIndexBUCases))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                #"selections": [self.parent.FUNC_BU_CASES_FORM['selections']],
                "selections": [self.parent.menuIndexBUCases],
            }, name="Bulk Update Cases Form", checkKey="title", checkValue=self.parent.FUNC_BU_CASES_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("bulk_update_cases_form==bulk_update_cases_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_BU_CASES_FORM['title'])
            assert('instanceXml' in data)


        @task
        def bulk_update_cases_form_questions(self):
            if self.parent.FUNC_BU_CASES_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("bulk_update_cases==bulk_update_cases_form_questions")
            questions=self.parent.FUNC_BU_CASES_FORM_QUESTIONS['questions']
            for q in questions:
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    return
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("bulk_update_cases==bulk_update_cases_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for Bulk Update Cases Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def bulk_update_cases_form_submit_questions(self):
            logging.info("bulk_update_cases==bulk_update_cases_form_submit_questions")
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_BU_CASES_FORM['title'],self.questionTree,self.session_id)


        @task
        def bulk_update_cases_form_submit(self):
            logging.info("bulk_update_cases_form==bulk_update_cases_form_submit")
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": {
                #    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key0']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value0'],
                #    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key1']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value1'],
                #    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key2']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value2'],
                #    ##self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key3']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value3'],
                #    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key4']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value4'],
                #    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key5']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value5'],
                #    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key6']: [self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value6']],
                #    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key7']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value7'],
                #    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key8']: [self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value8']],
                #    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key9']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value9'],
                #    self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-key10']: self.parent.FUNC_BU_CASES_FORM_SUBMIT['answers-value10']
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
            logging.info("bulk_update_cases_form==update_cases_form_submit")
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


    @tag('all', 'my_team')
    @task(1)
    # My Team Form
    class MyTeamFormEntry(SequentialTaskSet):
        @task
        def my_team_form(self):
            ## get module index number
            if (self.parent.menuIndexMyTeam==-1):
                self.parent.menuIndexMyTeam=self.parent._get_menu_index(self.parent.FUNC_MY_TEAM_FORM['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexMyTeam==-1):
                logging.info("skip -- "+self.parent.FUNC_MY_TEAM_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            logging.info("my_team==my_team_form::"+"::menuIndexMyTeam::"+str(self.parent.menuIndexMyTeam))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                #"selections": [self.parent.FUNC_MY_TEAM_FORM['selections']],
                "selections": [self.parent.menuIndexMyTeam],
            }, name="My Team Form", checkKey="title", checkValue=self.parent.FUNC_MY_TEAM_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("my_team==my_team_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_MY_TEAM_FORM['title'])
            assert('instanceXml' in data)


        @task
        def my_team_form_questions(self):
            if self.parent.FUNC_MY_TEAM_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("my_team==my_team_form_questions")
            questions=self.parent.FUNC_MY_TEAM_FORM_QUESTIONS['questions']
            for q in questions:
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    return
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("my_team==my_team_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for My Team Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def my_team_form_submit_questions(self):
            logging.info("my_team==my_team_form_submit_questions")
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_MY_TEAM_FORM['title'],self.questionTree,self.session_id)


        @task
        def my_team_form_submit(self):
            logging.info("my_team==my_team_form_submit")
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": {
                },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="My Team Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_MY_TEAM_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_MY_TEAM_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'register_new_contact_no_index_form')
    @task(2)
    # Register New Contacts Without Index Case Form
    class RNCNoIndexFormEntry(SequentialTaskSet):
        @task
        def rnc_no_index_form(self):
            ## get module index number
            if (self.parent.menuIndexRNCNoIndex==-1):
                self.parent.menuIndexRNCNoIndex=self.parent._get_menu_index(self.parent.FUNC_RNC_NO_INDEX_FORM['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexRNCNoIndex==-1):
                logging.info("skip -- "+self.parent.FUNC_RNC_NO_INDEX_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            logging.info("register_new_contact_no_index_form==rnc_no_index_form::menuIndexRNCNoIndex::"+str(self.parent.menuIndexRNCNoIndex))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexRNCNoIndex],
            }, name="Register New Contact Without Index Case Form", checkKey="title", checkValue=self.parent.FUNC_RNC_NO_INDEX_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("register_new_contact_no_index_form=rnc_no_index_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_RNC_NO_INDEX_FORM['title'])
            assert('instanceXml' in data)


        @task
        def rnc_no_index_form_questions(self):
            if self.parent.FUNC_RNC_NO_INDEX_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("register_new_contact_no_index_form==rnc_no_index_form_questions")
            questions=self.parent.FUNC_RNC_NO_INDEX_FORM_QUESTIONS['questions']
            for q in questions:
                #logging.info("qq1--->>>"+str(q))
                #logging.info("qq2--->>>"+q["question"])
                #logging.info("qq3--->>>"+q["title"])
                #logging.info("qq4--->>>"+q["answer"])
                #logging.info("qq5--->>>"+q["optional"])
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    return
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("register_new_contact_no_index_form==rnc_no_index_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for Register New Contact Without Index Case Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def rnc_no_index_form_submit_questions(self):
            logging.info("register_new_contact_no_index_form==rnc_no_index_form_submit_questions")
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_RNC_NO_INDEX_FORM['title'],self.questionTree,self.session_id)


        @task
        def rnc_no_index_form_submit(self):
            logging.info("register_new_contact_no_index_form==rnc_no_index_form_submit")
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": { },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Register New Contact Without Index Case Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_RNC_NO_INDEX_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_RNC_NO_INDEX_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    @tag('all', 'register_new_case_form')
    @task(2)
    # Register a New Case
    class RNCaseFormEntry(SequentialTaskSet):
        @task
        def rncase_form(self):
            ## get module index number
            if (self.parent.menuIndexRNCase==-1):
                self.parent.menuIndexRNCase=self.parent._get_menu_index(self.parent.FUNC_RNCASE_FORM['title'])
            if ((self.user.usertype=='ci' or self.user.usertype=='ct') and self.parent.menuIndexRNCase==-1):
                logging.info("skip -- "+self.parent.FUNC_RNCASE_FORM['title']+" for "+self.user.usertype+" user")
                self.interrupt()
            logging.info("register_new_case_form==rncase_form::menuIndexRNCase::"+str(self.parent.menuIndexRNCase))
            data = self.parent._formplayer_post("navigate_menu", extra_json={
                "selections": [self.parent.menuIndexRNCase],
            }, name="Register New Case Form", checkKey="title", checkValue=self.parent.FUNC_RNCASE_FORM['title'])
            if not ("session_id" in data):
                logging.info("case not found -- no session_id")
                self.interrupt()
            self.questionTree=data['tree']
            self.session_id=data['session_id']
            logging.info("register_new_cas3_form=rncas3_form::sessionId::"+self.session_id)
            assert(data['title'] == self.parent.FUNC_RNCASE_FORM['title'])
            assert('instanceXml' in data)


        @task
        def rncase_form_questions(self):
            if self.parent.FUNC_RNCASE_FORM_QUESTIONS['questions']=="None":
                return
            logging.info("register_new_case_form==rncase_form_questions")
            questions=self.parent.FUNC_RNCASE_FORM_QUESTIONS['questions']
            for q in questions:
                #logging.info("qq1--->>>"+str(q))
                #logging.info("qq2--->>>"+q["question"])
                #logging.info("qq3--->>>"+q["title"])
                #logging.info("qq4--->>>"+q["answer"])
                #logging.info("qq5--->>>"+q["optional"])
                dict=self.parent._build_question_lists(q['question'],self.questionTree)
                ## if q["optional"]=="true", the question may not exist, if not, skip it
                if (q["optional"]=="true" and dict==None):
                    return
                if (dict==None):
                    logging.info("question is not found: "+q['question'])
                    ##raise AssertionError()
                    assert False, "question is not found: "+q['question']
                ## if there is q["answer"] defined, don't use the default answer
                if (q["answer"]!=""):
                    finalAns=q["answer"]
                else:
                    finalAns=dict['answer']
                logging.info("register_new_case_form==rncase_form_questions::qq::"+q["question"]+"::"+str(dict['ix'])+"::"+str(finalAns))
                data = self.parent._formplayer_post("answer", extra_json={
                    "answer": finalAns,
                    "ix": dict['ix'],
                    "debuggerEnabled": True,
                    "session_id":self.session_id,
                }, name=q['question']+" for Register New Case Form", checkKey="title", checkValue=q['title'])
                self.questionTree=data['tree']
                assert(data['title'] == q['title'])


        @task
        def rncase_form_submit_questions(self):
            logging.info("register_new_case_form==rncase_form_submit_questions")
            questionString=self.parent._build_question_lists_form_submit(False,"",self.parent.FUNC_RNCASE_FORM['title'],self.questionTree,self.session_id)


        @task
        def rncase_form_submit(self):
            logging.info("register_new_case_form==rncase_form_submit")
            data = self.parent._formplayer_post("submit-all", extra_json={
                "answers": { },
                "prevalidated": True,
                "debuggerEnabled": True,
                "session_id":self.session_id,
            }, name="Register New Case Form Submit", checkKey="submitResponseMessage", checkValue=self.parent.FUNC_RNCASE_FORM_SUBMIT['submitResponseMessage'])
            assert(data['submitResponseMessage'] == self.parent.FUNC_RNCASE_FORM_SUBMIT['submitResponseMessage'])


        @task
        def stop(self):
            self.interrupt()


    def _formplayer_post(self, command, extra_json=None, name=None, checkKey=None, checkValue=None, checkLen=None):
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

        if 'XSRF-TOKEN' not in self.client.cookies:
            response = self.client.get(f"{self.user.formplayer_host}/serverup")
            response.raise_for_status()
        headers = {'X-XSRF-TOKEN': self.client.cookies['XSRF-TOKEN']}
        self.client.headers.update(headers)

        with self.client.post(f"{self.user.formplayer_host}/{command}/", json=json, name=name, catch_response=True) as response:
            data=response.json()
            ##logging.info("data-->"+str(data))
            if ("exception" in data):
                logging.info("ERROR::exception error--"+data['exception'])
                logging.info("ERROR::user-info::"+self.user.username+"::"+self.user.login_as)
                response.failure("exception error--"+data['exception'])
            elif (checkKey and checkKey not in data):
                logging.info("ERROR::"+checkKey+" not in data")
                response.failure("ERROR::"+checkKey+" not in data")
            elif (checkKey and checkLen):
                ##if (len(data[checkKey]) != checkLen):
                ##    logging.info("ERROR::len(data['"+checkKey+"']) != "+checkLen)
                ##    response.failure("ERROR::len(data['"+checkKey+"']) != "+checkLen)
                if (len(data[checkKey]) <= 0):
                    logging.info("ERROR::len(data['"+checkKey+"']) <= 0 ")
                    response.failure("ERROR::len(data['"+checkKey+"']) <= 0 ")
            elif (checkKey and checkValue):
                if (data[checkKey] != checkValue):
                    logging.info("ERROR::data['"+checkKey+"'] != "+checkValue)
                    response.failure("ERROR::data['"+checkKey+"'] != "+checkValue)
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
        ###wait_time = between(45, 90)
        ###wait_time = between(30, 60)
        ###wait_time = between(15, 30)
        wait_time = between(120, 180)

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
        self.usertype=user_info['usertype']
        #print("userinfo===>>"+str(user_info))

        logging.info("timestamp-->>>"+str(dt_object))
        logging.info("host-->>>"+self.host)
        logging.info("login_as-->>>"+self.login_as)
        logging.info("username-->>>"+self.username)
        logging.info("usertype-->>>"+self.usertype)
        logging.info("domain-->>>"+self.domain)
        logging.info("domain_user_credential-->>>"+self.domain_user_credential)
        logging.info("app_config-->>>"+self.app_config)

