class WatchHandler():
    def __init__(self, add_func = lambda json_dict: print("add pod"), modify_func = lambda json_dict: print("modifiy pod"),delete_func = lambda json_dict: print("delete pod")) -> None:
        self.DoAdded= add_func
        self.DoModified= modify_func
        self.DoDeleted = delete_func