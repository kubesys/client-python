import kubesys
import kubesys.client
from kubesys.client import KubernetesClient
import json
from urllib3.connectionpool import InsecureRequestWarning
from urllib3 import disable_warnings
disable_warnings(InsecureRequestWarning)

load_account_from_json=True

def createPod() -> str:
    config_str = '''{
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

    config_dict=json.loads(config_str)

    return json.dumps(config_dict, indent=4,separators=(',', ': '))

def updatePod(client) ->str:
    jsonObj, OK, status_code = client.getResource("Pod", "default", "busybox")
    labels = {}
    labels["test"] = "test"
    jsonObj["metadata"]["labels"] = labels
    return json.dumps(jsonObj)

def main():
    global load_account_from_json

    account_info={"URL": "", "Token": ""}

    if load_account_from_json:
        with open("account.json",'r', encoding='UTF-8') as f:
            account_info = json.load(f)

    client = KubernetesClient(account_info)
    client.Init()

if __name__ == '__main__':
    main()