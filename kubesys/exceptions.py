from requests.exceptions import HTTPError

class KindException(Exception):
    def __init__(self,*args,**kwargs):
        pass

class WatchException(Exception):
    def __init__(self,*args,**kwargs):
        pass