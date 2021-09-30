from typing import Union
from kubesys.common import getLastIndex,dictToJsonString,jsonStringToBytes
from requests import status_codes
from requests.api import request
from kubesys.http_request import createRequest,createRequestReturOriginal
from kubesys.analyzer import KubernetesAnalyzer
from kubesys.watcher import KubernetesWatcher
import json

class KubernetesClient():
    def __init__(self,url=None,token=None, analyzer=None, verify_SSL=False, account_json={"json_path": "account.json","host_label": "default"}, relearning=True) -> None:
        if not url and not token:
            with open(account_json["json_path"],'r', encoding='UTF-8') as f:
                account_info_dict = json.load(f)
                if account_json["host_label"] not in account_info_dict.keys():
                    print("host label<%s> is not found in %s"%(account_json["host_label"], account_json["json_path"]))
                    exit(-2)
                url = account_info_dict[account_json["host_label"]]["URL"]
                token = account_info_dict[account_json["host_label"]]["Token"]
        
        if url:
            self.url = url.rstrip("/")
        else:
            print("url is not given.")
            exit(-2)

        if token:
            self.token = token
        else:
            print("token is not given.")
            exit(-2)

        self.verify_SSL = verify_SSL

        if analyzer:
            self.analyzer = analyzer
        else:
            self.analyzer = KubernetesAnalyzer()
            self.analyzer.learning(url=self.url, token=self.token, verify_SSL=self.verify_SSL)

        if relearning and self.analyzer:
            self.Init()

    def Init(self)->None:
        self.analyzer.learning(url=self.url, token=self.token, verify_SSL=self.verify_SSL)

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
        if type(jsonObj) is str:
            jsonObj = json.loads(jsonObj)

        kind = self.getRealKind(str(jsonObj["kind"]),str(jsonObj["apiVersion"]))

        namespace = ""
        if "namespace" in jsonObj["metadata"].keys():
            namespace = str(jsonObj["metadata"]["namespace"])
        
        url = self.analyzer.FullKindToApiPrefixDict[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[kind], namespace)
        url += self.analyzer.FullKindToNameDict[kind]

        return createRequest(url=url,token=self.token,method="POST",body=jsonStr,keep_json=False)

    def updateResource(self,jsonStr)->Union[dict,bool,str]:
        jsonObj = jsonStr
        if type(jsonObj) is str:
            jsonObj = json.loads(jsonObj)
            
        kind = self.getRealKind(str(jsonObj["kind"]),str(jsonObj["apiVersion"]))

        namespace = ""
        if "namespace" in jsonObj["metadata"].keys():
            namespace = str(jsonObj["metadata"]["namespace"])
        
        url = self.analyzer.FullKindToApiPrefixDict[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[kind], namespace)
        url += self.analyzer.FullKindToNameDict[kind] + "/" + jsonObj["metadata"]["name"]

        return createRequest(url=url,token=self.token,method="PUT",body=jsonStr,keep_json=False)

    def checkAndReturnRealKind(self,kind,mapper)->Union[str,str]:
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
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindDict)
        if error_str:
            return None,error_str
        
        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        url += self.analyzer.FullKindToNameDict[fullKind] + "/" + name

        return createRequest(url=url,token=self.token, method="DELETE",keep_json=False)

    def getResource(self,kind,name,namespace="")->Union[dict,bool,str]:
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindDict)
        if error_str:
            return None,error_str

        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        url += self.analyzer.FullKindToNameDict[fullKind] + "/" + name

        return createRequest(url=url,token=self.token, method="GET",keep_json=False)

    def listResources(self,kind,namespace="")->Union[dict,bool,str]:
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindDict)
        if error_str:
            return None,error_str

        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        url += self.analyzer.FullKindToNameDict[fullKind]

        return createRequest(url=url,token=self.token, method="GET",keep_json=False)

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

        url = self.analyzer.FullKindToApiPrefixDict[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[kind], namespace)
        url += self.analyzer.FullKindToNameDict[kind] + "/"
        url += pod["metadata"]["name"] + "/binding"

        return createRequest(url=url,token=self.token, method="POST",data=jsonObj, keep_json=False)

    def watchResource(self,kind,namespace,watcher,name=None) ->None:
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindDict)
        if error_str:
            print(error_str)
            return

        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/watch/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        if name:
            url += self.analyzer.FullKindToNameDict[fullKind] + "/" + name
        else:
            url += self.analyzer.FullKindToNameDict[fullKind]

        watcher.watching(url=url,token=self.token)

    def watchResources(self,kind,namespace,watcher) ->None:
        self.watchResource(kind,namespace,watcher,name=None)

    def updateResourceStatus(self, jsonStr)->Union[dict,bool,str]:
        jsonObj = jsonStr
        if type(jsonObj) is str:
            jsonObj = json.loads(jsonObj)
        
        kind = self.getRealKind(jsonObj["kind"], jsonObj["apiVersion"])
        namespace = ""
        if "namespace" in jsonObj["metadata"]:
            namespace = jsonObj["metadata"]["namespace"]

        url = self.analyzer.FullKindToApiPrefixDict[kind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[kind], namespace)
        url += self.analyzer.FullKindToNameDict[kind] + "/" + jsonObj["metadata"]["name"]
        url += "/status"

        return createRequest(url=url,token=self.token, method="PUT", body=jsonObj, keep_json=False)

    def listResourcesWithLabelSelector(self,kind, namespace, labels)->Union[dict,bool,str]:
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindDict)
        if error_str:
            print(error_str)
            return

        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        url += self.analyzer.FullKindToNameDict[fullKind]
        url += "?labelSelector="
        for key, value in labels.items():
            url += key + "%3D" + value + ","
        url = url[:len(url)-1]
        return createRequest(url=url,token=self.token, method="GET", keep_json=False)

    def listResourcesWithFieldSelector(self, kind, namespace, fields)->Union[dict,bool,str]:
        fullKind, error_str = self.checkAndReturnRealKind(kind,self.analyzer.KindToFullKindDict)
        if error_str:
            print(error_str)
            return

        url = self.analyzer.FullKindToApiPrefixDict[fullKind] + "/"
        url += self.getNamespace(self.analyzer.FullKindToNamespaceDict[fullKind], namespace)
        url += self.analyzer.FullKindToNameDict[fullKind]
        url += "?fieldSelector="
        for key, value in fields.items():
            url += key + "%3D" + value + ","

        url = url[:len(url)-1]
        return createRequest(url=url,token=self.token, method="GET", keep_json=False)

    def getKinds(self) ->list:
        return list(self.analyzer.KindToFullKindDict.keys())

    def getFullKinds(self)->list:
        return list(self.analyzer.FullKindToNameDict.keys())

    def kind(self,fullkind)->str:
        index = getLastIndex(fullkind,".")
        if index<1:
            return fullkind
        return fullkind[index+1:]

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