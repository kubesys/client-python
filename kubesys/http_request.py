"""
* Copyright (2021, ) Institute of Software, Chinese Academy of Sciences
"""
from kubesys.common import formatURL, getParams,dictToJsonString
import requests
from requests.models import HTTPError
from requests.exceptions import JSONDecodeError
import json

__author__ = ('Tian Yu <yutian20@otcaix.iscas.ac.cn>',
              'Jiexin Liu <liujiexin@otcaix.scas.ac.cn>',
              'Heng Wu <wuheng@iscas.ac.cn>')

from kubesys.tls import tlsPaths


def createRequest(url, token, method="GET", body=None, verify=False,
                  keep_json=False, config=None, **kwargs):
    response = doCreateRequest(
        formatURL(url, getParams(kwargs)), token, method, body, config)
    try:
        result = response.json()
        if keep_json:
            result=dictToJsonString(result)
        return result
    except JSONDecodeError:
        raise HTTPError(response.status_code,response.url+' '+response.reason)

def doCreateRequest(url, token, method="GET", body=None, config=None,stream=False):
    if config is None:
        response = doCreateRequestWithToken(url, token, method,stream, body)
    else:
        response = doCreateRequestWithConfig(url, config, method,stream, body)
    return response


def doCreateRequestWithToken(url, token, method,stream, body=None):
    header, data = getHeaderAndBody(token, body)
    return requests.request(method, url=url,
                            headers=header, data=data, verify=False,stream=stream)


def doCreateRequestWithConfig(url, config, method, stream,body=None):

    header, data = getHeaderAndBody(None, body)
    pem, ca, key = tlsPaths(config)
    return requests.request(method, url=url, headers=header, data=data,
                            verify=pem, cert=(ca, key),stream=stream)


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
