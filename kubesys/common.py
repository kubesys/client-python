import json

def goodPrintDict(dict_obj, show_print=False)->str:
    s= json.dumps(dict_obj, indent=4,separators=(',', ': '))
    if show_print:
        print(s)
    return s