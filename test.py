##
# Copyright (2021, ) Institute of Software, Chinese Academy of Sciences
##
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
    url = "https://120.46.180.58:6443"
    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IlNXU0pBMkczanNmdjhaOUlJZmUzUXRHUHpnUEx4bjlGREsydWxaTTFiMDQifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJrdWJlcm5ldGVzLWNsaWVudC10b2tlbiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJrdWJlcm5ldGVzLWNsaWVudCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6Ijg5ZGQ1ZjBhLTYyM2EtNGZhMi05MjQ3LTBmOTZiZGNmMGY3MSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlLXN5c3RlbTprdWJlcm5ldGVzLWNsaWVudCJ9.DNNSlT7jMYLR7FBrh58H-E04vwtYhna_br4PgHcS1fjnUGIflqJNco4AIiGXRLk53YvM5t6C5Vg2iy8TPkG4d7eFCYaypgg7baqlkt_ZaNnS0SPY90Mzodx1VzkkZomMeti32Y2eUxk3F_jWPadoLyydYGmAmqvypdilclYbBvEblM_gwHsb6cBpGfuF1MyYsdXNTmYpsOe5husJsL_juQAc4xGF9zBMPz4qmbzPm_Myd1SddcvRjckScP_-ifQl86jJLJd8lpKGvrn0LP3KhhUdrLrUptHejpbAyUY2X4IQDwj0nnz_VVn3C30gJIGGOS75WasczVG_74oKJqFy5w"

    client = KubernetesClient(url=url, token=token)
    test_watcher_base(client, "default", "Pod", handlerFunction=deal_watch(), timeoutSeconds=3)
    test_CRUD(client=client)

    print("current thread count: ", KubernetesClient.getWatchThreadCount())
    time.sleep(7)
    # because of the timeoutSecond=3, watching thread is leave.
    print("current thread count: ", KubernetesClient.getWatchThreadCount())


if __name__ == '__main__':
    main()
