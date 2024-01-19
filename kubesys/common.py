'''
 * Copyright (2024, ) Institute of Software, Chinese Academy of Sciences
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 '''
import json
import threading

__author__ = ('Tian Yu <yutian20@otcaix.iscas.ac.cn>',
              'Heng Wu <wuheng@iscas.ac.cn>')


def goodPrintDict(dict_obj, show_print=False) -> str:
    s = dictToJsonString(dict_obj)
    if show_print:
        print(s)
    return s


def getLastIndex(s, flag) -> int:
    return len(s) - s[::-1].find(flag) - 1


def dictToJsonString(dict_obj) -> str:
    return json.dumps(dict_obj, indent=4, separators=(',', ': '))


def jsonStringToDict(json_str) -> dict:
    return json.loads(json_str)


def jsonBytesToDict(json_bytes) -> dict:
    return json.loads(json_bytes)


def jsonStringToBytes(json_str, encoding="utf-8") -> bytes:
    return bytes(json_str, encoding=encoding)


def getActiveThreadCount() -> int:
    return threading.active_count()


def getParams(params):
    if params is None:
        return ""

    if len(params.keys()) < 1:
        return ""

    http_params = "?"
    for key, value in params.items():
        http_params += str(key)
        http_params += "="
        http_params += str(value)
        http_params += "&"

    return http_params.rstrip("&")


def formatURL(url, paramsString=""):
    return url.rstrip("/") + str(paramsString)
