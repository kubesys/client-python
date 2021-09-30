from kubesys.common import dictToJsonString
class WatchHandler():
    def __init__(self, add_func = lambda json_dict: print("ADDED: ", dictToJsonString(json_dict)), modify_func = lambda json_dict: print("MODIFIED: ", dictToJsonString(json_dict)),delete_func = lambda json_dict: print("DELETED: ", dictToJsonString(json_dict))) -> None:
        self.DoAdded= add_func
        self.DoModified= modify_func
        self.DoDeleted = delete_func