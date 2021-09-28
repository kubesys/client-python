
def DoAdder(json_dict)->None:
    print("add pod")

def DoModified(json_dict)->None:
    print("update pod")

def DoDeleted(json_dict)->None:
    print("delete pod")

class WatchHandler():
    def __init__(self,func={"DoAdder":DoAdder,"DoModified":DoModified,"DoDeleted":DoDeleted}) -> None:
        self.DoAdder= func["DoAdder"]
        self.DoModified= func["DoModified"]
        self.DoDeleted = func["DoDeleted"]