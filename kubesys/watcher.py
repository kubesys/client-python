import requests
import json

class KubernetesWatcher():
    def __init__(self,client=None,handler=None) -> None:
        self.client = None
        self.watchHandler = None
        self.setValues(client,handler)

    def setValues(self,client=None,handler=None) -> None:
        if client:           
            self.client = client
        if handler:
            self.watchHandler = handler

    def watching(self,url,token)->None:
        header = {
            "Accept": "*/*",
            "Authorization": "Bearer "+ token,
            "Accept-Encoding": "gzip, deflate, br",
        }

        with requests.get(url=url, headers=header, verify=False, stream= True) as response:
            for json_bytes in response.iter_lines():
                if len(json_bytes)<1:
                    continue

                jsonObj = json.loads(json_bytes)
                if jsonObj["type"] == "ADDED":
                    self.watchHandler.DoAdded(jsonObj["object"])
                elif jsonObj["type"] == "MODIFIED":
                    self.watchHandler.DoModified(jsonObj["object"])
                elif jsonObj["type"] == "DELETED":
                    self.watchHandler.DoDeleted(jsonObj["object"])
                else:
                    print("unknow type while watching:",jsonObj["type"])