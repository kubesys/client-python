from kubesys.client import KubernetesClient
from kubesys.common import dictToJsonString, getActiveThreadCount
from kubesys.watch_handler import WatchHandler
import time
# import kubesys

def test_CRUD(client):
    pod_json= '''{
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
    response_dict,OK,http_status_code = client.listResources("Pod")
    # print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    # print("is OK: ", OK)
    # print("HTTP status code: ", http_status_code,"\n")

    # test create resources
    print("--test create resources:")
    response_dict,OK,http_status_code = client.createResource(pod_json)
    # print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    # print("is OK: ", OK)
    # print("HTTP status code: ", http_status_code,"\n")

    # test get one single Resources
    print("--test get one single Resources")
    response_dict,OK,http_status_code = client.getResource(kind="Pod", namespace="default", name="busybox")
    # print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    # print("is OK: ", OK)
    # print("HTTP status code: ", http_status_code,"\n")

    # test delete pod
    print("--test delete pod:")
    response_dict,OK,http_status_code = client.deleteResource(kind="Pod", namespace="default", name="busybox")
    # print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    # print("is OK: ", OK)
    # print("HTTP status code: ", http_status_code,"\n")

def test_watcher(client,namespce,kind,name=None):
    print("--start to watch...")
    # client.watchResource(kind="Pod", namespace="default", name="busybox",watcherhandler=WatchHandler(add_func = lambda json_dict: print("ADDED: ", dictToJsonString(json_dict)), modify_func = lambda json_dict: print("MODIFIED: ", dictToJsonString(json_dict)),delete_func = lambda json_dict: print("DELETED: ", dictToJsonString(json_dict))))
    watcher = client.watchResource(kind=kind, namespace=namespce, name=name,watcherhandler=WatchHandler(add_func = lambda json_dict: print(kind,"ADDED ",to_name(json_dict)), modify_func = lambda json_dict: print(kind,"MODIFIED ",to_name(json_dict)),delete_func = lambda json_dict: print(kind,"DELETED ",to_name(json_dict))))
    print(watcher.url)

def to_name(json_dict):
    return json_dict["metadata"]["name"]

def main():
    url = ""
    token = ""

    client = KubernetesClient(url=url,token=token)
    test_watcher(client,"","DaemonSet")
    test_watcher(client,"","Pod")
    test_watcher(client,"","Service")
    test_watcher(client,"","Deployment")
    test_watcher(client,"","Secret")
    test_watcher(client,"","Lease")
    test_watcher(client,"","events.k8s.io.Event")
#     test_CRUD(client=client)
    KubernetesClient.joinWatchers()

if __name__ == '__main__':
    main()