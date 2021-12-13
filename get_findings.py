# !/usr/bin/env python3
import json
import requests
import os

try:
    SHIFTLEFT_ORG_ID = os.environ["SHIFTLEFT_ORG_ID"]
    SHIFTLEFT_ACCESS_TOKEN = os.environ["SHIFTLEFT_ACCESS_TOKEN"]
except KeyError:
    raise SystemExit("Oops! Do not forget to set both SHIFTLEFT_ORG_ID and SHIFTLEFT_ACCESS_TOKEN!")

API_V4_BASE_URL = "https://www.shiftleft.io/api/v4/"
API_V4_ORG_PATH = "orgs/{organization_id}/"

class SLAPIError:
    """
    SLAPIError represents API error details returned by SL API v4
    """

    def __init__(self, ok=False, code=0, message="", validation_errors=()):
        self.ok = ok
        self.code = code
        self.message = message
        self.validation_errors = validation_errors

    def as_string(self):
        """
        as_string composes the most descriptive error it can with the available data.
        :return: string containing a descriptive error.
        """
        if len(self.validation_errors) != 0:
            return "found the following validation errors in the request: {}".format(", ".join(self.validation_errors))

        if len(self.message) != 0:
            return "server responded: {}".format(self.message)

        return "server returned {} code without further information".format(self.code)


def handle_success(resp):
    """
    We discovered a few cases where response body can be empty so we handle the case
    """
    response = ""
    try:
        response = resp.json()["response"]
    except (json.JSONDecodeError, json.decoder.JSONDecodeError):
        response = resp.text
    return response


def handle_status_code(resp=None):
    """
    handle_status_code intercepts the response and raises an appropriate error if it's not a 200

    :param resp: an http response as returned from requests library
    :return: None in case of success or raises an exception with details otherwise
    """
    if resp is None:
        return
    if resp.status_code == 200:
        return
    try:
        json_decoded_body = resp.json()
    except (json.JSONDecodeError, json.decoder.JSONDecodeError):
        json_decoded_body = resp.text
    except Exception:
        raise Exception(resp.status_code)
    e = SLAPIError(**json_decoded_body)
    raise Exception(e.as_string())


class SLResponse:
    """
    Is an implementation of the base 200 response provided by all ShiftLeft API v4 endpoints.
    """

    def __init__(self, ok=True, response=None):
        if response is None:
            response = {}
        self.ok = ok
        self.response = response


class SLAPIClient:
    """
    SLAPIClient handles communications with ShiftLeft API v4 for the purposes of this script.
    It is very limited and bound to be obsoleted of Schema changes.
    """

    def __init__(self, access_token="", organization_id=""):
        self.__access_header = {'Authorization': 'Bearer {}'.format(access_token), 'Content-Type': 'application/json'}
        self.__organization_id = organization_id

    def _do_get(self, api_path):
        u = API_V4_BASE_URL + API_V4_ORG_PATH.format(organization_id=self.__organization_id) + api_path
        resp = requests.get(u, headers=self.__access_header)
        handle_status_code(resp)
        return handle_success(resp)

    def _do_post(self, api_path, payload=None):
        u = API_V4_BASE_URL + API_V4_ORG_PATH.format(organization_id=self.__organization_id) + api_path
        resp = requests.post(u, headers=self.__access_header, data=json.dumps(payload))
        handle_status_code(resp)
        return handle_success(resp)

    def _do_put(self, api_path, payload=None):
        u = API_V4_BASE_URL + API_V4_ORG_PATH.format(organization_id=self.__organization_id) + api_path
        resp = requests.put(u, headers=self.__access_header, data=json.dumps(payload))
        handle_status_code(resp)
        return handle_success(resp)

    def list_findings(self, page = "1"):
        #resp = self._do_get("findings?per_page=249&type=package")
        return self._do_get(f"findings?page={page}&per_page=249&type=package")


def main():
    api_v4 = SLAPIClient(SHIFTLEFT_ACCESS_TOKEN, SHIFTLEFT_ORG_ID)
    #m = ["1","2","3","4","5","6","7"]
    page = 1
    #for n in m:
    while True:
        findings = api_v4.list_findings(page)
        if "findings" not in findings:
            break
        #print(findings)
        add_to_findings = []
        myList = []
        search = "log4j"
        for key, value in findings.items():
            #print(key)
            if key == "findings":
                #print("true")
                find = value
                #print(find)
                for x in find:
                    app = x.get("app")
                    #print(x)
                    #print(app)
                    for x,y in x.items():
                        #print(x,y)
                        if search in y:
                            #app == x.get("app")
                            #print(x,y,app)
                            myList.append(app)
                            for word in myList:
                                if word not in add_to_findings:
                                    add_to_findings.append(app)
        print(add_to_findings)
        page += 1



if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()
