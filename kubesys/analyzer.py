import kubesys.http_request as http_request
from kubesys.common import getLastIndex
class KubernetesAnalyzer:
    def __init__(self) -> None:
        self.KindToFullKindDict = {}
        self.FullKindToApiPrefixDict = {}
        
        self.FullKindToNameDict = {}
        self.FullKindToNamespaceDict = {}

        self.FullKindToVersionDict = {}
        self.FullKindToGroupDict = {}
        self.FullKindToVerbsDict = {}

    def learning(self,url,token,verify_SSL=False) ->None:
        registryValues = http_request.createRequest(url=url,token=token,method="GET",keep_json=False)[0]

        # print(registryValues)
        for path in registryValues["paths"]:
            if path.startswith("/api") and (len(path.split("/"))==4 or path.lower().strip() == "/api/v1"):
                resourceValues = http_request.createRequest(url=url+path,token=token,method="GET",keep_json=False)[0]
                apiVersion = str(resourceValues["groupVersion"])

                for resourceValue in resourceValues["resources"]:
                    shortKind = resourceValue["kind"]
                    fullKind = self.getFullKind(shortKind, apiVersion)

                    if fullKind not in self.FullKindToApiPrefixDict.keys():
                        if shortKind not in self.KindToFullKindDict.keys():
                            self.KindToFullKindDict[shortKind] = []

                        self.KindToFullKindDict[shortKind].append(fullKind)
                        self.FullKindToApiPrefixDict[fullKind] = url+path

                        self.FullKindToNameDict[fullKind] = str(resourceValue["name"])
                        self.FullKindToNamespaceDict[fullKind] = bool(resourceValue["namespaced"])

                        self.FullKindToVersionDict[fullKind] = apiVersion
                        self.FullKindToGroupDict[fullKind] = self.getGroup(apiVersion)
                        self.FullKindToVerbsDict[fullKind] = resourceValue["verbs"]

    def getGroup(self,apiVersion)->str:
        index = getLastIndex(apiVersion,"/")
        if index>0:
            return apiVersion[:index]
        else:
            return ""

    def getFullKind(self,shortKind,apiVersion)->str:
        index = apiVersion.find("/")
        apiGroup=""

        if index>-1:
            apiGroup = apiVersion[:index]

        fullKind = ""
        if len(apiGroup)==0:
            fullKind = shortKind
        else:
            fullKind = apiGroup+"."+shortKind

        return fullKind