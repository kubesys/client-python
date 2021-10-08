from typing import Union
from kubesys.common import formatURL,getParams
import requests
import json

def createRequest(url,token,method="GET",body=None,verify=False,keep_json=False,**kwargs) -> Union[object,bool,str]:
    response, OK, status_code = createRequestReturOriginal(formatURL(url,getParams(kwargs)),token,method,body,verify)

    result=response.json()
    if keep_json:
        result = json.dumps(result, indent=4,separators=(',', ': '))

    return result,OK,status_code

def createRequestReturOriginal(url,token,method="GET",body=None,verify=False,**kwargs)-> Union[object,bool,str]:
    method_upper = method.upper()

    data=None
    header = {
        "Accept": "*/*",
        "Authorization": "Bearer "+ token,
        "Accept-Encoding": "gzip, deflate, br",
    }

    if body:
        header["Content-Type"] = "application/json"
        
        if type(body) is dict:
            data = json.dumps(body, indent=4,separators=(',', ': '))
        else:
            data = str(body)

    if method_upper=="GET":
        response = requests.get(url=formatURL(url,getParams(kwargs)), headers=header, verify=verify)
    elif method_upper=="PUT":
        response = requests.put(url=formatURL(url,getParams(kwargs)),headers=header,data=data, verify=verify)
    elif method_upper=="DELETE":
        response = requests.delete(url=formatURL(url,getParams(kwargs)),headers=header, verify=verify)
    elif method_upper=="POST":
        response = requests.post(url=formatURL(url,getParams(kwargs)),headers=header,data=data,verify=verify)
    else:
        print("unsupported HTTP request kind! Current method is",method_upper)
        exit(-1)

    if response.status_code >=200 and response.status_code <= 299:
        return response,True,response.status_code

    else:
        return response,False,response.status_code

