from typing import Union
import requests
import json
from requests import status_codes
from requests.models import Response

def createRequest(url,token,method="GET",body=None,verify=False,keep_json=False) -> Union[object,bool,str]:
    response, OK, status_code = createRequestReturOriginal(url,token,method,body,verify)

    result=response.json()
    if not keep_json:
        result = json.dumps(result)

    return result,OK,status_code

def createRequestReturOriginal(url,token,method="GET",body=None,verify=False)-> Union[object,bool,str]:
    method_upper = method.upper()

    data=None
    header = {
        "Accept": "*/*",
        "Authorization": "Bearer "+ token,
        "Accept-Encoding": "gzip, deflate, br",
    }

    if body:
        header["Content-Type"] = "application/json"
        
        if body is dict:
            data = json.dumps(body, indent=4,separators=(',', ': '))
        else:
            data = str(body)

    if method_upper=="GET":
        response = requests.get(url=url, headers=header, verify=verify)
    elif method_upper=="PUT":
        response = requests.put(url=url,headers=header,data=data, verify=verify)
    elif method_upper=="DELETE":
        response = requests.delete(url=url,headers=header, verify=verify)
    elif method_upper=="POST":
        response = requests.post(url=url,headers=header,data=data,verify=verify)
    else:
        print("unsupported HTTP request kind! Current method is",method_upper)
        exit(-1)

    if response.reason=="OK":
        return response,True,response.status_code

    else:
        return response,False,response.status_code

