from kubesys.client import KubernetesClient
from kubesys.common import goodPrintDict
from kubesys.watcher import KubernetesWatcher
from kubesys.watch_handler import WatchHandler

def test_CRUD():
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

    client = KubernetesClient(host_label="default")

    # test list resources
    print("--test list resources:")
    response_dict,OK,http_status_code = client.listResources("Pod")
    print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code,"\n")

    # test create resources
    print("--test create resources:")
    response_dict,OK,http_status_code = client.createResource(pod_json)
    print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code,"\n")

    # test get one single Resources
    print("--test get one single Resources")
    response_dict,OK,http_status_code = client.getResource(kind="Pod", namespace="default", name="busybox")
    print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code,"\n")

    # test delete pod
    print("--test delete pod:")
    response_dict,OK,http_status_code = client.deleteResource(kind="Pod", namespace="default", name="busybox")
    print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code,"\n")

def test_watcher():
    print("--start to watch...")
    client = KubernetesClient(host_label="default")
    watcher = KubernetesWatcher(client,WatchHandler())
    client.watchResource(kind="Pod", namespace="default", name="busybox",watcher=watcher)

def main():
    test_CRUD()
    # test_watcher()

if __name__ == '__main__':
    main()