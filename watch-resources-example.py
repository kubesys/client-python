##
# Copyright (2021, ) Institute of Software, Chinese Academy of Sciences
##
import os.path

import yaml

from kubesys.client import KubernetesClient
from kubesys.common import dictToJsonString, getActiveThreadCount, goodPrintDict
from kubesys.watch_handler import WatchHandler
import time


def test_watcher(client, namespce, kind):
    print("--start to watch...")
    client.watchResources(kind=kind, namespace=namespce, watcherhandler=WatchHandler(
        add_func=lambda json_dict: print(kind, "ADDED ", dictToJsonString(json_dict)[:20]),
        modify_func=lambda json_dict: print(kind, "MODIFIED ", dictToJsonString(json_dict)[:20]),
        delete_func=lambda json_dict: print(kind, "DELETED ", dictToJsonString(json_dict)[:20])))
    time.sleep(10000)


if __name__ == '__main__':
    client = KubernetesClient(config=".token")
    test_watcher(client=client, namespce="", kind="Pod")
    
