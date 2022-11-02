"""
* Copyright (2021, ) Institute of Software, Chinese Academy of Sciences
"""
from kubesys.common import dictToJsonString

__author__ = ('Tian Yu <yutian20@otcaix.iscas.ac.cn>',
              'Heng Wu <wuheng@iscas.ac.cn>')


class WatchHandler():
    def __init__(self, add_func=lambda json_dict: print("ADDED: ", dictToJsonString(json_dict)),
                 modify_func=lambda json_dict: print("MODIFIED: ", dictToJsonString(json_dict)),
                 delete_func=lambda json_dict: print("DELETED: ", dictToJsonString(json_dict))) -> None:
        self.DoAdded = add_func
        self.DoModified = modify_func
        self.DoDeleted = delete_func
