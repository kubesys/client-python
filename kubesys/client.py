from typing import Union
import requests
from requests import status_codes
from requests.api import request
from kubesys.http_request import createRequest,createRequestReturOriginal
from kubesys.analyzer import KubernetesAnalyzer
from kubesys.watch_handler import WatchHandler
from kubesys.watcher import KubernetesWatcher
import json

class KubernetesClient():
    def __init__(self, account_info, analyzer=None, verify_SSL=False) -> None:
        if "URL" in account_info.keys():
            self.url = account_info["URL"].rstrip("/")
        else:
            self.url = ""

        if "Token" in account_info.keys():
            self.token = account_info["Token"]
        else:
            self.token = ""

        if analyzer:
            self.analyzer = analyzer
        else:
            self.analyzer = KubernetesAnalyzer()

        self.verify_SSL = verify_SSL
        self.http = None

    def Init(self)->None:
        self.analyzer.learning(url=self.url, token=self.token, verify_SSL=self.verify_SSL)
        print(self.analyzer.FullKindToGroupMapper)

    def getNamespace(self,supportNS,value) ->str:
        if supportNS and len(value)>0:
            return "namespaces/" + value + "/"
        
        return ""

    def getRealKind(self,kind,apiVersion)->str:
        index = apiVersion.find("/")
        if index < 0:
            return kind
        else:
            return apiVersion[:index] + "." + kind

    def createResource(self,jsonStr) ->Union[dict,bool,str]:
        jsonObj = jsonStr
        if jsonObj is str:
            jsonObj = json.loads(jsonObj)

        kind = self.getRealKind(str(jsonObj["kind"]),str(jsonObj["apiVersion"]))

        namespace = ""
        if "namespace" in jsonObj["metadata"].keys():
            namespace = str(jsonObj["metadata"]["namespace"])
        
        url = self.analyzer.FullKindToApiPrefixMapper[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceMapper[kind], namespace)
        url += self.analyzer.FullKindToNameMapper[kind]

        return createRequest(url=url,token=self.token,method="POST",body=jsonStr,keep_json=False)

    def updateResource(self,jsonStr)->Union[dict,bool,str]:
        jsonObj = jsonStr
        if jsonObj is str:
            jsonObj = json.loads(jsonObj)
            
        kind = self.getRealKind(str(jsonObj["kind"]),str(jsonObj["apiVersion"]))

        namespace = ""
        if "namespace" in jsonObj["metadata"].keys():
            namespace = str(jsonObj["metadata"]["namespace"])
        
        url = self.analyzer.FullKindToApiPrefixMapper[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceMapper[kind], namespace)
        url += self.Analyzer.FullKindToNameMapper[kind] + "/" + jsonObj["metadata"]["name"]

        return createRequest(url=url,token=self.token,method="PUT",body=jsonStr,keep_json=False)

    def checkAndReturnRealKind(kind,mapper)->Union[str,str]:
        index = kind.find(".")
        if index<0:
            if len(mapper[kind])==1:
                return mapper[kind][0], None

            elif len(mapper[kind])==0:
                return "", "invalid kind"

            else:
                value = ""
                for s in mapper[kind]:
                    value+= "," + s

                return "", "please use fullKind: "+value[1:]

        return kind, None

    def deleteResource(self,kind,namespace,name)->Union[dict,bool,str]:
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindMapper)
        if error_str:
            return None,error_str
        
        url = self.analyzer.FullKindToApiPrefixMapper[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceMapper[fullKind], namespace)
        url += self.analyzer.FullKindToNameMapper[fullKind] + "/" + name

        return createRequest(url=url, method="DELETE",keep_json=False)

    def getResource(self,kind,namespace,name)->Union[dict,bool,str]:
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindMapper)
        if error_str:
            return None,error_str

        url = self.analyzer.FullKindToApiPrefixMapper[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceMapper[fullKind], namespace)
        url += self.analyzer.FullKindToNameMapper[fullKind] + "/" + name

        return createRequest(url=url, method="GET",keep_json=False)

    def listResources(self,kind,namespace)->Union[dict,bool,str]:
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindMapper)
        if error_str:
            return None,error_str

        url = self.analyzer.FullKindToApiPrefixMapper[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceMapper[fullKind], namespace)
        url += self.analyzer.FullKindToNameMapper[fullKind]

        return createRequest(url=url, method="GET",keep_json=False)

    def bindResource(self,pod,host)->Union[dict,bool,str]:
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

        url = self.analyzer.FullKindToApiPrefixMapper[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceMapper[kind], namespace)
        url += self.analyzer.FullKindToNameMapper[kind] + "/"
        url += pod["metadata"]["name"] + "/binding"

        return createRequest(url=url, method="POST",data=jsonObj, keep_json=False)

    def watchResource(self,kind,namespace,watcher,name=None) ->None:
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindMapper)
        if error_str:
            print(error_str)
            return

        url = self.analyzer.FullKindToApiPrefixMapper[fullKind] + "/watch/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceMapper[fullKind], namespace)
        if name:
            url += self.analyzer.FullKindToNameMapper[fullKind] + "/" + name
        else:
            url += self.analyzer.FullKindToNameMapper[fullKind]

        Watching(url,watcher=watcher)

    def watchResources(self,kind,namespace,watcher) ->None:
        self.watchResource(self,kind,namespace,watcher,name=None)

    def updateResourceStatus(self, jsonStr)->Union[dict,bool,str]:
        jsonObj = jsonStr
        if jsonObj is str:
            jsonObj = json.loads(jsonObj)
        
        kind = self.getRealKind(jsonObj["kind"], jsonObj["apiVersion"])
        namespace = ""
        if "namespace" in jsonObj["metadata"]:
            namespace = jsonObj["metadata"]["namespace"]

        url = self.analyzer.FullKindToApiPrefixMapper[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceMapper[kind], namespace)
        url += self.analyzer.FullKindToNameMapper[kind] + "/" + jsonObj["metadata"]["name"]
        url += "/status"

        return createRequest(url=url, method="PUT", body=jsonObj, keep_json=False)

    def listResourcesWithLabelSelector(self,kind, namespace, labels)->Union[dict,bool,str]:
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindMapper)
        if error_str:
            print(error_str)
            return

        url = self.analyzer.FullKindToApiPrefixMapper[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceMapper[fullKind], namespace)
        url += self.analyzer.FullKindToNameMapper[fullKind]
        url += "?labelSelector="
        for key, value in labels.items():
            url += key + "%3D" + value + ","
        url = url[:len(url)-1]
        return createRequest(url=url, method="GET", keep_json=False)

    def listResourcesWithFieldSelector(self, kind, namespace, fields)->Union[dict,bool,str]:
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindMapper)
        if error_str:
            print(error_str)
            return

        url = self.analyzer.FullKindToApiPrefixMapper[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceMapper[fullKind], namespace)
        url += self.analyzer.FullKindToNameMapper[fullKind]
        url += "?fieldSelector="
        for key, value in fields.items():
            url += key + "%3D" + value + ","

        url = url[:len(url)-1]
        return createRequest(url=url, method="GET", keep_json=False)


def Watching(url,watcher)->None:
    client = KubernetesClient(account_info={"URL":url, "Token": watcher.client.Token},analyzer=watcher.client.analyzer)
    header = {
        "Accept": "*/*",
        "Authorization": "Bearer "+ client.token,
        "Accept-Encoding": "gzip, deflate, br",
    }

    with requests.get(url=url, headers=header, verify=False, stream= True) as response:
        for json_str in response.iter_lines():
            if len(json_str)<1:
                continue

            jsonObj = json.load(json_str)
            if jsonObj["type"] == "ADDED":
                watcher.handler.DoAdded(jsonObj["object"])
            elif jsonObj["type"] == "MODIFIED":
                watcher.handler.DoModified(jsonObj["object"])
            elif jsonObj["type"] == "DELETED":
                watcher.handler.DoDeleted(jsonObj["object"])
            else:
                print("unknow type while watching:",jsonObj["type"])

    # with requests.get(url=url, headers=header, verify=False, stream= True) as response:
    #     while(True):
    #         if response.reason != "OK":
    #             print("HTTP response error when watching, status code:",response.status_code)
    #             exit(-1)

    #         json_strs = response.text.split("\n")
    #         for json_str in json_strs:
    #             if len(json_str)<1:
    #                 continue

    #             jsonObj = json.load(json_str)
    #             if jsonObj["type"] == "ADDED":
    #                 watcher.handler.DoAdded(jsonObj["object"])
    #             elif jsonObj["type"] == "MODIFIED":
    #                 watcher.handler.DoModified(jsonObj["object"])
    #             elif jsonObj["type"] == "DELETED":
    #                 watcher.handler.DoDeleted(jsonObj["object"])
    #             else:
    #                 print("unknow type while watching:",jsonObj["type"])
                    
        