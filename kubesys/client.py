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
import sys
from typing import Union
from kubesys.common import getLastIndex, dictToJsonString, jsonStringToBytes, getParams, formatURL
from kubesys.http_request import createRequest,doCreateRequest
from kubesys.analyzer import KubernetesAnalyzer
from kubesys.exceptions import WatchException,HTTPError
import requests
import json
from kubesys.common import jsonBytesToDict
import threading

from kubesys.tls import readConfig
from kubesys.watcher import KubernetesWatcher

__author__ = ('Tian Yu <yutian20@otcaix.iscas.ac.cn>',
              'Jiexin Liu <liujiexin@otcaix.iscas.ac.cn>',
              'Heng Wu <wuheng@iscas.ac.cn>')


class KubernetesClient():
    watcher_threads = {}  # static field, record the thread that used to watch

    # def __init__(self, url=None, token=None, analyzer=None, verify_SSL=False,
    #              account_json={"json_path": "account.json", "host_label": "default"}, relearning=True) -> None:
    #     if not url and not token:
    #         with open(account_json["json_path"], 'r', encoding='UTF-8') as f:
    #             account_info_dict = json.load(f)
    #             if account_json["host_label"] not in account_info_dict.keys():
    #                 print("host label<%s> is not found in %s" % (account_json["host_label"], account_json["json_path"]))
    #                 exit(-2)
    #             url = account_info_dict[account_json["host_label"]]["URL"]
    #             token = account_info_dict[account_json["host_label"]]["Token"]

    def __init__(self, url=None, token=None, analyzer=None,
                 config=None, relearning=True) -> None:
        # if not url and not token:
        self.config = config

        if self.config is None:
            if url is None or token is None:
                raise HTTPError('missing url or token')
            self.url = url.rstrip("/")
            self.token = token
        else:
            self.config = readConfig(config)
            self.url = self.config.server
            self.token = None

        if analyzer:
            self.analyzer = analyzer
        else:
            self.analyzer = KubernetesAnalyzer()
            self.analyzer.learning(url=self.url, token=self.token, config=self.config)

        if relearning and self.analyzer:
            self.Init()

    def Init(self) -> None:
        self.analyzer.learning(url=self.url, token=self.token, config=self.config)

    def getNamespace(self, supportNS, value) -> str:
        if supportNS and len(value) > 0:
            return "namespaces/" + value + "/"

        return ""

    def getRealKind(self, kind, apiVersion) -> str:
        index = apiVersion.find("/")
        if index < 0:
            return kind
        else:
            return apiVersion[:index] + "." + kind

    def createResource(self, jsonStr, **kwargs) -> dict:
        jsonObj = jsonStr
        if type(jsonObj) is str:
            jsonObj = json.loads(jsonObj)
        elif type(jsonObj) is dict:
            jsonStr=dictToJsonString(jsonStr)

        kind = self.getRealKind(str(jsonObj["kind"]), str(jsonObj["apiVersion"]))

        namespace = ""
        if "namespace" in jsonObj["metadata"].keys():
            namespace = str(jsonObj["metadata"]["namespace"])

        url = self.analyzer.FullKindToApiPrefixDict[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[kind], namespace)
        url += self.analyzer.FullKindToNameDict[kind]
        return createRequest(url=url, token=self.token, method="POST", body=jsonStr,keep_json=False, config=self.config, **kwargs)

    def updateResource(self, jsonStr:Union[str,dict], **kwargs) -> dict:
        jsonObj = jsonStr
        if type(jsonObj) is str:
            jsonObj = json.loads(jsonObj)
        elif type(jsonObj) is dict:
            jsonStr=dictToJsonString(jsonStr)

        kind = self.getRealKind(str(jsonObj["kind"]), str(jsonObj["apiVersion"]))

        namespace = ""
        if "namespace" in jsonObj["metadata"].keys():
            namespace = str(jsonObj["metadata"]["namespace"])

        url = self.analyzer.FullKindToApiPrefixDict[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[kind], namespace)
        url += self.analyzer.FullKindToNameDict[kind] + "/" + jsonObj["metadata"]["name"]

        return createRequest(url=url, token=self.token, method="PUT", body=jsonStr, keep_json=False,config=self.config, **kwargs)

    # def checkAndReturnRealKind(self, kind, mapper):
    #     index = kind.find(".")
    #     if index < 0:
    #         if not mapper.get(kind) or len(mapper.get(kind)) == 0:
    #             raise KindException(f"Invalid kind {kind}")
    #         if len(mapper[kind]) == 1:
    #             return mapper[kind][0]
    #
    #         # elif len(mapper[kind]) == 0:
    #         #     raise Exception(f"Invalid kind {kind}")
    #
    #         else:
    #             value = ""
    #             for s in mapper[kind]:
    #                 value += "," + s
    #
    #             raise KindException("please use fullKind: " + value[1:])
    #
    #     return kind

    def deleteResource(self, kind, namespace, name, **kwargs) -> dict:
        fullKind = self.analyzer.checkAndReturnRealKind(kind)
        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        url += self.analyzer.FullKindToNameDict[fullKind] + "/" + name

        return createRequest(url=url, token=self.token, method="DELETE", keep_json=False,config=self.config, **kwargs)

    def getResource(self, kind, name, namespace="", **kwargs) -> dict:
        fullKind = self.analyzer.checkAndReturnRealKind(kind)

        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        url += self.analyzer.FullKindToNameDict[fullKind] + "/" + name

        return createRequest(url=url, token=self.token, method="GET", keep_json=False, config=self.config,**kwargs)

    def listResources(self, kind, namespace="", **kwargs) -> dict:
        fullKind = self.analyzer.checkAndReturnRealKind(kind)

        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        url += self.analyzer.FullKindToNameDict[fullKind]

        return createRequest(url=url, token=self.token, method="GET", keep_json=False, config=self.config,**kwargs)

    def bindResource(self, pod, host, **kwargs) -> dict:
        jsonObj = {}
        jsonObj["apiVersion"] = "v1"
        jsonObj["kind"] = "Binding"

        meta = {}
        meta["name"] = pod["metadata"]["name"]
        meta["namespace"] = pod["metadata"]["namespace"]
        jsonObj["metadata"] = meta

        target = {}
        target["apiVersion"] = "v1"
        target["kind"] = "Node"
        target["name"] = host
        jsonObj["target"] = target

        kind = self.getRealKind(pod["kind"], pod["apiVersion"])
        namespace = pod["metadata"]["namespace"]

        url = self.analyzer.FullKindToApiPrefixDict[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[kind], namespace)
        url += self.analyzer.FullKindToNameDict[kind] + "/"
        url += pod["metadata"]["name"] + "/binding"

        return createRequest(url=url, token=self.token, method="POST", data=jsonObj, keep_json=False, config=self.config,**kwargs)

    def watchResource(self, kind, namespace, watcherhandler, name=None, thread_name=None, is_daemon=True,
                      **kwargs) -> KubernetesWatcher:
        '''
        if is_daemon is True, when the main thread leave, this thead will leave automatically.
        '''
        fullKind = self.analyzer.checkAndReturnRealKind(kind)

        url = self.analyzer.FullKindToApiPrefixDict[fullKind]+"/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        if name:
            url += self.analyzer.FullKindToNameDict[fullKind] + "/" + name
        else:
            url += self.analyzer.FullKindToNameDict[fullKind]
        thread_t = threading.Thread(target=KubernetesClient.watching,
                                    args=(url, self.token, self.config, watcherhandler, kwargs,),
                                    name=thread_name, daemon=is_daemon)

        watcher = KubernetesWatcher(thread_t=thread_t, kind=kind, namespace=namespace, watcher_handler=watcherhandler,
                                    name=name, url=url, **kwargs)
        KubernetesClient.watcher_threads[thread_t.getName()] = watcher
        watcher.run()

        return watcher

    def watchResources(self, kind, namespace, watcherhandler, thread_name=None, is_daemon=True,
                       **kwargs) -> KubernetesWatcher:
        '''
        if is_daemon is True, when the main thread leave, this thead will leave automatically.
        '''
        return self.watchResource(kind, namespace, watcherhandler, name=None, thread_name=thread_name,
                                  isDaemon=is_daemon, **kwargs)

    def watchResourceBase(self, kind, namespace, handlerFunction, name=None, thread_name=None, is_daemon=True,
                          **kwargs) -> KubernetesWatcher:
        '''
        if is_daemon is True, when the main thread leave, this thead will leave automatically.
        '''
        fullKind = self.analyzer.checkAndReturnRealKind(kind)

        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/watch/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        if name:
            url += self.analyzer.FullKindToNameDict[fullKind] + "/" + name
        else:
            url += self.analyzer.FullKindToNameDict[fullKind]

        thread_t = threading.Thread(target=KubernetesClient.watchingBase,
                                    args=(url, self.token, handlerFunction, kwargs,), name=thread_name,
                                    daemon=is_daemon)
        watcher = KubernetesWatcher(thread_t=thread_t, kind=kind, namespace=namespace, watcher_handler=handlerFunction,
                                    name=name, url=url, **kwargs)
        KubernetesClient.watcher_threads[thread_t.getName()] = watcher
        watcher.run()
        return watcher

    def watchResourcesBase(self, kind, namespace, handlerFunction, thread_name=None, is_daemon=True,
                           **kwargs) -> KubernetesWatcher:
        '''
        if is_daemon is True, when the main thread leave, this thead will leave automatically.
        '''
        return self.watchResourceBase(kind, namespace, handlerFunction, name=None, thread_name=thread_name,
                                      isDaemon=is_daemon, **kwargs)

    @staticmethod
    def watching(url, token, config, watchHandler, kwargs):
        # TODO
        response=doCreateRequest(url=formatURL(url, getParams(kwargs)) + "&watch=true&timeoutSeconds=315360000", token=token, method="GET", config=config,stream=True)
        for json_bytes in response.iter_lines():
            if len(json_bytes) < 1:
                continue

            jsonObj = jsonBytesToDict(json_bytes)
            if "type" not in jsonObj.keys():
                raise WatchException(f"type is not found in keys while watching, dict is: {jsonObj}" )

            if jsonObj["type"] == "ADDED":
                watchHandler.DoAdded(jsonObj["object"])
            elif jsonObj["type"] == "MODIFIED":
                watchHandler.DoModified(jsonObj["object"])
            elif jsonObj["type"] == "DELETED":
                watchHandler.DoDeleted(jsonObj["object"])
            else:
                raise WatchException(f"unknow type while watching: {jsonObj['type']}")
        KubernetesClient.removeWatcher(thread_name=threading.currentThread().getName())

    @staticmethod
    def watchingBase(url, token, handlerFunction, kwargs):
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

        # TODO
        with requests.get(url=formatURL(url, getParams(kwargs)) + "&watch=true&timeoutSeconds=315360000", headers=header, verify=False, stream=True) as response:
            for json_bytes in response.iter_lines():
                if len(json_bytes) < 1:
                    continue

                jsonObj = jsonBytesToDict(json_bytes)
                handlerFunction(jsonObj=jsonObj)

        del KubernetesClient.watcher_threads[threading.currentThread().getName()]

    def updateResourceStatus(self, jsonStr, **kwargs) -> dict:
        jsonObj = jsonStr
        if type(jsonObj) is str:
            jsonObj = json.loads(jsonObj)
        elif type(jsonObj) is dict:
            jsonStr=dictToJsonString(jsonStr)

        kind = self.getRealKind(jsonObj["kind"], jsonObj["apiVersion"])
        namespace = ""
        if "namespace" in jsonObj["metadata"]:
            namespace = jsonObj["metadata"]["namespace"]

        url = self.analyzer.FullKindToApiPrefixDict[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[kind], namespace)
        url += self.analyzer.FullKindToNameDict[kind] + "/" + jsonObj["metadata"]["name"]
        url += "/status"

        return createRequest(url=url, token=self.token, method="PATCH", body=jsonStr, keep_json=False,config=self.config, **kwargs)

    def getResourceStatus(self,kind, name, namespace="", **kwargs)->dict:
        fullKind = self.analyzer.checkAndReturnRealKind(kind)

        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        url += self.analyzer.FullKindToNameDict[fullKind] + "/" + name
        url+="/status"

        return createRequest(url=url, token=self.token, method="GET", keep_json=False, config=self.config, **kwargs)

    def listResourcesWithSelector(self, kind, namespace, tp,selects) -> dict:
        fullKind = self.analyzer.checkAndReturnRealKind(kind)

        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        url += self.analyzer.FullKindToNameDict[fullKind]
        if tp=='label':
            url += "?labelSelector="
        elif tp=='field':
            url += "?fieldSelector="
        else:
            raise HTTPError(404,f"selector type {tp} should either be label or field")
        for key, value in selects.items():
            url += key + "%3D=" + value + ","
        url = url[:len(url) - 1]
        return createRequest(url=url, token=self.token, method="GET", keep_json=False,config=self.config)


    def getKinds(self) -> list:
        return list(self.analyzer.KindToFullKindDict.keys())

    def getFullKinds(self) -> list:
        return list(self.analyzer.FullKindToNameDict.keys())

    def kind(self, fullkind) -> str:
        index = getLastIndex(fullkind, ".")
        if index < 1:
            return fullkind
        return fullkind[index + 1:]

    def getKindDesc(self) -> dict:
        desc = {}
        for fullKind in self.analyzer.FullKindToNameDict.keys():
            value = {}
            value["apiVersion"] = self.analyzer.FullKindToVersionDict[fullKind]
            value["kind"] = self.kind(fullKind)
            value["plural"] = self.analyzer.FullKindToNameDict[fullKind]
            value["verbs"] = self.analyzer.FullKindToVerbsDict[fullKind]
            desc[fullKind] = value

        return desc

    def getKindDescBytes(self) -> bytes:
        desc = self.getKindDesc()

        return jsonStringToBytes(dictToJsonString(desc))

    '''
    static methods for watch thread
    '''

    @staticmethod
    def getWatchThreadCount() -> int:
        return len(KubernetesClient.watcher_threads.keys())

    @staticmethod
    def getWatcher(thread_name) -> KubernetesWatcher:
        if thread_name in KubernetesClient.watcher_threads.keys():
            return KubernetesClient.watcher_threads[thread_name]
        return None

    @staticmethod
    def removeWatcher(thread_name) -> None:
        if thread_name in KubernetesClient.watcher_threads.keys():
            if KubernetesClient.isWatcherAlive(thread_name):
                KubernetesClient.watcher_threads[thread_name].stop()

            del KubernetesClient.watcher_threads[thread_name]

    @staticmethod
    def isWatcherAlive(thread_name) -> bool:
        if thread_name in KubernetesClient.watcher_threads.keys():
            return KubernetesClient.watcher_threads[thread_name].is_alive()
        return False

    @staticmethod
    def removeWatchers() -> None:
        for thread_name in KubernetesClient.watcher_threads.keys():
            KubernetesClient.watcher_threads[thread_name].stop()
        KubernetesClient.watcher_threads = {}

    @staticmethod
    def removeClosedWatchers() -> None:
        for thread_name in KubernetesClient.watcher_threads.keys():
            if not KubernetesClient.isWatcherAlive(thread_name):
                KubernetesClient.removeWatcher(thread_name)

    @staticmethod
    def joinWatchers() -> None:
        for thread_name in KubernetesClient.watcher_threads.keys():
            KubernetesClient.watcher_threads[thread_name].join()

    @staticmethod
    def getWatcherThreadNames() -> list:
        return KubernetesClient.watcher_threads.keys()
