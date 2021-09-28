from requests.models import Response

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
