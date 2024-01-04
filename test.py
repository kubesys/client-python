##
# Copyright (2021, ) Institute of Software, Chinese Academy of Sciences
##
import os.path

import yaml

from kubesys.client import KubernetesClient
from kubesys.common import dictToJsonString, getActiveThreadCount, goodPrintDict
from kubesys.watch_handler import WatchHandler
import time


def test_CRUD(client):
    pod_json = '''{
                        "apiVersion": "v1",
                        "kind": "Pod",
                        "metadata": {
                            "name": "busybox",
                            "namespace": "default"
                        },
                        "spec": {
                            "containers": [
                            {
                                "image": "busybox",
                                "env": [{
                                    "name": "abc",
                                    "value": "abc"
                                    }],
                                "command": [
                                    "sleep",
                                    "3600"
                                    ],
                                "imagePullPolicy": "IfNotPresent",
                                "name": "busybox"
                            }],
                            "restartPolicy": "Always"
                        }
                    }'''

    # test list resources
    print("--test list resources:")
    response_dict, OK, http_status_code = client.listResources("Pod")
    # print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code, "\n")

    # test create resources
    print("--test create resources:")
    response_dict, OK, http_status_code = client.createResource(pod_json)
    # print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    time.sleep(7)
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code, "\n")

    # test get one single Resources
    print("--test get one single Resources")
    response_dict, OK, http_status_code = client.getResource(kind="Pod", namespace="default", name="busybox")
    # print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code, "\n")

    # test delete pod
    print("--test delete pod:")
    response_dict, OK, http_status_code = client.deleteResource(kind="Pod", namespace="default", name="busybox")
    # print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code, "\n")


def test_watcher(client, namespce, kind, name=None):
    print("--start to watch...")
    # client.watchResource(kind="Pod", namespace="default", name="busybox",watcherhandler=WatchHandler(add_func = lambda json_dict: print("ADDED: ", dictToJsonString(json_dict)), modify_func = lambda json_dict: print("MODIFIED: ", dictToJsonString(json_dict)),delete_func = lambda json_dict: print("DELETED: ", dictToJsonString(json_dict))))
    watcher = client.watchResource(kind=kind, namespace=namespce, name=name, watcherhandler=WatchHandler(
        add_func=lambda json_dict: print(kind, "ADDED ", dictToJsonString(json_dict)[:20]),
        modify_func=lambda json_dict: print(kind, "MODIFIED ", dictToJsonString(json_dict)[:20]),
        delete_func=lambda json_dict: print(kind, "DELETED ", dictToJsonString(json_dict)[:20])))
    print(watcher.url)


def deal_watch(*args):
    def tt(jsonObj=None, args=args):
        print(dictToJsonString(jsonObj)[:20])

    return tt


def test_watcher_base(client, namespce, kind, name=None, handlerFunction=None, **kwargs):
    print("--start to watch...")
    # client.watchResource(kind="Pod", namespace="default", name="busybox",watcherhandler=WatchHandler(add_func = lambda json_dict: print("ADDED: ", dictToJsonString(json_dict)), modify_func = lambda json_dict: print("MODIFIED: ", dictToJsonString(json_dict)),delete_func = lambda json_dict: print("DELETED: ", dictToJsonString(json_dict))))
    watcher = client.watchResourceBase(kind=kind, namespace=namespce, name=name, handlerFunction=handlerFunction,
                                       **kwargs)
    print(watcher.url)


def main():

    client = KubernetesClient(config='.token')
    # test_watcher_base(client, "default", "Pod", handlerFunction=deal_watch(), timeoutSeconds=3)
    test_CRUD(client=client)

    print("current thread count: ", KubernetesClient.getWatchThreadCount())
    time.sleep(7)
    # because of the timeoutSecond=3, watching thread is leave.
    print("current thread count: ", KubernetesClient.getWatchThreadCount())


if __name__ == '__main__':
    # main()
    client = KubernetesClient(config='.token')
    print(client.getFullKinds())
    # client.listResourcesWithFieldSelector(kind='Pod', namespace='', fields={'spec.nodeName': '=133.133.135.134'})