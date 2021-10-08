import json
import threading

def goodPrintDict(dict_obj, show_print=False)->str:
    s= dictToJsonString(dict_obj)
    if show_print:
        print(s)
    return s

def getLastIndex(s,flag)->int:
    return len(s)-s[::-1].find(flag)-1

def dictToJsonString(dict_obj) -> str:
    return json.dumps(dict_obj, indent=4,separators=(',', ': '))

def jsonStringToDict(json_str) -> dict:
    return json.loads(json_str)

def jsonBytesToDict(json_bytes) -> dict:
    return json.loads(json_bytes)

def jsonStringToBytes(json_str,encoding = "utf-8")->bytes:
    return bytes(json_str,encoding=encoding)

def getActiveThreadCount() -> int:
    return threading.active_count()

def getParams(params):
    if params is None:
        return ""

    if len(params.keys())<1:
        return ""

    http_params = "?"
    for key,value in params.items():
        http_params += str(key)
        http_params += "="
        http_params += str(value)
        http_params += "&"

    return http_params.rstrip("&")

def formatURL(url,paramsString=""):
    return url.rstrip("/") + str(paramsString)