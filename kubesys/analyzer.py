import kubesys.http_request as http_request

class KubernetesAnalyzer:
    def __init__(self) -> None:
        self.KindToFullKindMapper = {}
        self.FullKindToApiPrefixMapper = {}
        
        self.FullKindToNameMapper = {}
        self.FullKindToNamespaceMapper = {}

        self.FullKindToVersionMapper = {}
        self.FullKindToGroupMapper = {}
        self.FullKindToVerbsMapper = {}

    def learning(self,url,token,verify_SSL=False) ->None:
        registryValues = http_request.createRequest(url=url,token=token,method="GET",keep_json=True)[0]

        print(registryValues)
        for path in registryValues["paths"]:
            if path.startswith("/api") and (len(path.split("/"))==4 or path.lower().strip() == "/api/v1"):
                resourceValues = http_request.createRequest(url=url+path,token=token,method="GET",keep_json=True)[0]
                apiVersion = str(resourceValues["groupVersion"])

                for resourceValue in resourceValues["resources"]:
                    shortKind = resourceValue["kind"]
                    fullKind = self.getFullKind(shortKind, apiVersion)

                    if fullKind not in self.FullKindToApiPrefixMapper.keys():
                        if shortKind not in self.KindToFullKindMapper.keys():
                            self.KindToFullKindMapper[shortKind] = []

                        self.KindToFullKindMapper[shortKind].append(fullKind)
                        self.FullKindToApiPrefixMapper[fullKind] = url+path

                        self.FullKindToNameMapper = str(resourceValue["name"])
                        self.FullKindToNamespaceMapper[fullKind] = bool(resourceValue["namespaced"])

                        self.FullKindToVersionMapper[fullKind] = apiVersion
                        self.FullKindToGroupMapper[fullKind] = self.getGroup(apiVersion)
                        self.FullKindToVerbsMapper[fullKind] = resourceValue["verbs"]

    def getGroup(self,apiVersion)->str:
        index = self.getLastIndex(apiVersion,"/")
        if index>0:
            return apiVersion[:index]
        else:
            return ""

    def getLastIndex(self,s,flag)->int:
        return len(s)-s[::-1].index(flag)-1

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
