from kubesys.client import KubernetesClient
from kubesys.common import goodPrintDict,dictToJsonString
from kubesys.watcher import KubernetesWatcher
from kubesys.watch_handler import WatchHandler
# import kubesys

url = "https://39.100.71.73:6443/"
token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjNEd1dGSVRaVVdvRUJCdkRlcHlLckw3WnNCcGhsdVVTek43cGRMLXhxSFUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJrdWJlcm5ldGVzLWNsaWVudC10b2tlbi04bmdzYyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJrdWJlcm5ldGVzLWNsaWVudCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjJhNGEwN2E0LTRiODktNDAxYy04NjlhLTE3ZGQ2OGNlYzc0OSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlLXN5c3RlbTprdWJlcm5ldGVzLWNsaWVudCJ9.M0z9lDSZytKRKPyS3wVZS5AeVu4j8366HTSUJJSm-kVyas7hsYT0BNQraRRy5RCHukHDjb6nIV-9aAjnItO0pdQB6hOvW6JufTA3ukZM5aEYidD-hlt-_iPanYMXaRcUTeBOWpPFTjpWbU4jF9Q5rfTeAgLzBl09kgNTPnTAkFov9jnZx0HZaFCijJZLZkmU_D0djqEUi1jgU7O__W33gPN3mCPYwwAuXzJkEoiVijXVpJT8i3SyYBW9TrK7uoKmMFi5v1e0hm0VfKdQCE4ywFt17Hnc0Zbqga5laeuirT6BHzDe7Tfp4r3j2eCT8QT3PIhohwEDPn4gC3qAwUU6Hg"

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

    client = KubernetesClient(url=url,token=token)

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
    client = KubernetesClient(account_json={"json_path": "account.json", "host_label": "default"})
    watcher = KubernetesWatcher(client,WatchHandler(add_func = lambda json_dict: print("ADDED: ", dictToJsonString(json_dict)), modify_func = lambda json_dict: print("MODIFIED: ", dictToJsonString(json_dict)),delete_func = lambda json_dict: print("DELETED: ", dictToJsonString(json_dict))))
    client.watchResource(kind="Pod", namespace="default", name="busybox",watcher=watcher)

def main():
    test_CRUD()
    # test_watcher()

if __name__ == '__main__':
    main()

# 1. 缺少 watchResources(有了watchResource，缺少加s的)，getKinds、getFullKinds和getKindDesc