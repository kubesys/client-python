"""
* Copyright (2021, ) Institute of Software, Chinese Academy of Sciences
"""
from typing import Union
from kubesys.common import formatURL, getParams
import requests
import json

__author__ = ('Tian Yu <yutian20@otcaix.iscas.ac.cn>',
              'Heng Wu <wuheng@iscas.ac.cn>')

from kubesys.tls import tlsPaths


def createRequest(url, token, method="GET", body=None, verify=False,
                  keep_json=False, config=None, **kwargs) -> Union[object, bool, str]:
    response, OK, status_code = doCreateRequest(
        formatURL(url, getParams(kwargs)), token, method, body, config)

    result = response.json()
    if keep_json:
        result = json.dumps(result, indent=4, separators=(',', ': '))

    return result, OK, status_code


def doCreateRequest(url, token, method="GET", body=None, config=None) \
        -> Union[object, bool, str]:
    if config is None:
        response = doCreateRequestWithToken(url, token, method, body)
    else:
        response = doCreateRequestWithConfig(url, config, method, body)

    if 200 <= response.status_code <= 299:
        return response, True, response.status_code

    else:
        return response, False, response.status_code


def doCreateRequestWithToken(url, token, method, body=None):
    header, data = getHeaderAndBody(token, body)
    return requests.request(method, url=url,
                            headers=header, data=data, verify=False)

    # if method_upper == "GET":
    #     return requests.get(url=formatURL(url, getParams(kwargs)), headers=header, verify=False)
    # elif method_upper == "PUT":
    #     return requests.put(url=formatURL(url, getParams(kwargs)), headers=header, data=data, verify=False)
    # elif method_upper == "DELETE":
    #     return requests.delete(url=formatURL(url, getParams(kwargs)), headers=header, verify=False)
    # elif method_upper == "POST":
    #     return requests.post(url=formatURL(url, getParams(kwargs)), headers=header, data=data, verify=False)
    # else:
    #     print("unsupported HTTP request kind! Current method is", method_upper)
    #     exit(-1)


def doCreateRequestWithConfig(url, config, method, body=None):

    header, data = getHeaderAndBody(None, body)
    pem, ca, key = tlsPaths(config)
    return requests.request(method, url=url, headers=header, data=data,
                            verify=pem, cert=(ca, key))


def getHeaderAndBody(token, body):
    if token is None:
        header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
        }
    else:
        header = {
            "Accept": "*/*",
            "Authorization": "Bearer " + token,
            "Accept-Encoding": "gzip, deflate, br",
        }

    if body:
        header["Content-Type"] = "application/json"

        if type(body) is dict:
            data = json.dumps(body, indent=4, separators=(',', ': '))
        else:
            data = str(body)
    else:
        body = None
    return header, body
