# client-Python

We expect to provide a python client:
- **Flexibility**. It can support all Kubernetes-based systems with minimized extra development, such as [Openshift](https://www.redhat.com/en/technologies/cloud-computing/openshift), [istio](https://istio.io/), etc.
- **Usability**. Developers just need to learn to write json/yaml(kubernetes native style) from [Kubernetes documentation](https://kubernetes.io/docs/home/).
- **Integration**. It can work with the other Kubernetes clients, such as [fabric8](https://github.com/fabric8io/kubernetes-client), [official](https://github.com/kubernetes-client/java/).

## Comparison

|                           | [official](https://github.com/kubernetes-client/go) | [cdk8s](https://cdk8s.io/) | [client-Python](https://github.com/kubesys/kubernetes-client-python) |
|---------------------------|------------------|------------------|-------------------|
|        Compatibility                      | for kubernetes-native kinds    | for crd kinds                 |  for both |
|  Support customized Kubernetes resources  |  a lot of development          | a lot of development          |  zero-deployment     |
|    Works with the other SDKs              |  complex                       | complex                       |  simple              |

## Architecture

![avatar](/docs/arch.png)

## Installation

```shell
git clone --recursive https://github.com/kubesys/client-python.git
```

just import the module by:

```python
from kubesys.client import KubernetesClient
```

## Usage

- [Usage](#usage)
    - [中文文档](https://www.yuque.com/kubesys/kubernetes-client/overview)
    - [Creating a client](#creating-a-client)
    - [Simple example](#simple-example)
    - [full-example](#full-example)

#### create token with the following commands:

1. create token

```yaml
kubectl create -f https://raw.githubusercontent.com/kubesys/client-python/master/account.yaml
```
2. get token

```kubectl
kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep kubernetes-client | awk '{print $1}') | grep "token:" | awk -F":" '{print$2}' | sed 's/ //g'

```
### Creating a client

we assume the following information: 

```yaml
host name: aliyun
URL: "https://192.168.1.1:6443"
Token: "THISISTHETOKEN"					# Just as an assumption, in reality this is a long-string
```

* you can simply define the dictionary as follows and then initialize the client  

```python
url = "https://192.168.1.1:6443",
token = "THISISTHETOKEN"

client = KubernetesClient(url=url,token=token)
```

* Also, you can make use of  the host informations in your json-configure file. We edit `account.json` with the following ahead of time:

```json
{
    "aliyun":{
        "URL": "https://192.168.1.1:6443",
        "Token":"THISISTHETOKEN"
    }
}
```

then, we can  initialize the client:

```python
client = KubernetesClient(account_json={"json_path": "account.json", "host_label": "aliyun"}) 
```

**If you have set the value of `url` or `token`, `account_json` will not take effect! **



### simple-example

Assume you have a json:

```json
{
  "apiVersion": "v1",
  "kind": "Pod",
  "metadata": {
    "name": "busybox",
    "namespace": "default",
    "labels": {
      "test": "test"
    }
  }
}
```

List resources:

```python
response_dict,OK,http_status_code = client.ListResources("Pod")
print("response dict: ", response_dict)
print("is OK: ", OK)
print("HTTP status code: ", http_status_code)
```

Create a resource:

```go
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

client.createResource(pod_json);
print("response_dict: ", response_dict)
print("is OK: ", OK)
print("HTTP status code: ", http_status_code)
```

Get a resource:

```python
response_dict,OK,http_status_code = client.getResource(kind="Pod",namespace="default", name="busybox")
print("response_dict: ", response_dict)
print("is OK: ", OK)
print("HTTP status code: ", http_status_code)
```

Delete a resource:

```python
response_dict,OK,http_status_code = client.deleteResource(kind="Pod", namespace="default",name="busybox")
print("response_dict: ", response_dict)
print("is OK: ", OK)
print("HTTP status code: ", http_status_code)
```

Watch a resource:

```python
from kubesys.watcher import KubernetesWatcher
from kubesys.watch_handler import WatchHandler

def DoAdder(json_dict)->None:
    print("add pod")

def DoModified(json_dict)->None:
    print("modifiy pod")

def DoDeleted(json_dict)->None:
    print("delete pod")

client = KubernetesClient(url=url,token=token)                                                           # init a client normally
watcher = client.watchResource(kind=kind, namespace=namespace, name=name,watcherhandler=WatchHandler(add_func = lambda json_dict: print(kind,"-ADDED: "), modify_func = lambda json_dict: print(kind,"-MODIFIED: "),delete_func = lambda json_dict: print(kind,"-DELETED: "))

# you can view the KubernetesWatcher-class to learn more about this.
print(watcher.url)
print(watcher.thread_name)              
```

more flexible watcher:

when use this kind of function, you can deal with the original json-object. And you can give some extra params.

```python
def deal_watch(*args):
    # "jsonObj" must be one of the params in function "deal"
    def deal(jsonObj=None,args=args):
        # define your deal process
        print(dictToJsonString(jsonObj)[:20])

    return deal

watcher = client.watchResourceBase(kind="Pod", namespace="default", handlerFunction=deal_watch())
print(watcher.url)
```

Advanced usage:

If you want to add more request restrictions, such as "limit","continue","fieldSelector" and so on, you can simply give them to the python-function-params. For example:

```python
def deal_watch(*args):
    # "jsonObj" must be one of the params in function "deal"
    def deal(jsonObj=None,args=args):
        # define your deal process
        print(dictToJsonString(jsonObj)[:20])

    return deal

# set http_params as timeoutSeconds=3 & limit=1
watcher = client.watchResourceBase(kind="Pod", namespace="default", handlerFunction=deal_watch(),timeoutSeconds="3",limit="1")
print(watcher.url)
```

**the watcher will be close automatically when the main thead exit. If this is not your aim, you can set the param by `is_daemon=False`**

get how much watcher is running:

```python
KubernetesClient.getWatchThreadCount()	# int
```

get watcher by thread-name:

```python
watcher = KubernetesClient.getWatcher(thread_name)
```

close a watcher by thread-name:

```python
KubernetesClient.removeWatcher(thread_name)
```

close all watchers:

```python
KubernetesClient.removeWatchers()
```

know if a watcher is running:

```python
KubernetesClient.isWatcherAlive(thread_name)		# bool
```

get the thread-names of all running watcher:

```python
KubernetesClient.getWatcherThreadNames()			# list[str]
```

if you want to wait watchers without the main-thread exit:

```python
KubernetesClient.joinWatchers()						# It will cause the program fail to exit.
```

Show better print for python-dict as json:

```python
from kubesys.common import goodPrintDict

print(goodPrintDict(response_dict))
```
## full-example

see the result in [run-outputs](/out.txt)

```python
from kubesys.client import KubernetesClient
from kubesys.common import dictToJsonString, getActiveThreadCount,goodPrintDict
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
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code,"\n")

    # test create resources
    print("--test create resources:")
    response_dict,OK,http_status_code = client.createResource(pod_json)
    # print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code,"\n")

    # test get one single Resources
    print("--test get one single Resources")
    response_dict,OK,http_status_code = client.getResource(kind="Pod", namespace="default", name="busybox")
    # print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code,"\n")

    # test delete pod
    print("--test delete pod:")
    response_dict,OK,http_status_code = client.deleteResource(kind="Pod", namespace="default", name="busybox")
    # print("response_dict: %s"%(goodPrintDict(response_dict,show_print=False)))
    print("is OK: ", OK)
    print("HTTP status code: ", http_status_code,"\n")

def test_watcher(client,namespce,kind,name=None):
    print("--start to watch...")
    # client.watchResource(kind="Pod", namespace="default", name="busybox",watcherhandler=WatchHandler(add_func = lambda json_dict: print("ADDED: ", dictToJsonString(json_dict)), modify_func = lambda json_dict: print("MODIFIED: ", dictToJsonString(json_dict)),delete_func = lambda json_dict: print("DELETED: ", dictToJsonString(json_dict))))
    watcher = client.watchResource(kind=kind, namespace=namespce, name=name,watcherhandler=WatchHandler(add_func = lambda json_dict: print(kind,"ADDED ",dictToJsonString(json_dict)[:20]), modify_func = lambda json_dict: print(kind,"MODIFIED ",dictToJsonString(json_dict)[:20]),delete_func = lambda json_dict: print(kind,"DELETED ",dictToJsonString(json_dict)[:20])))
    print(watcher.url)

def deal_watch(*args):
    def tt(jsonObj=None,args=args):
        print(dictToJsonString(jsonObj)[:20])

    return tt

def test_watcher_base(client,namespace,kind,name=None,handlerFunction=None,**kwargs):
    print("--start to watch...")
    # client.watchResource(kind="Pod", namespace="default", name="busybox",watcherhandler=WatchHandler(add_func = lambda json_dict: print("ADDED: ", dictToJsonString(json_dict)), modify_func = lambda json_dict: print("MODIFIED: ", dictToJsonString(json_dict)),delete_func = lambda json_dict: print("DELETED: ", dictToJsonString(json_dict))))
    watcher = client.watchResourceBase(kind=kind, namespace=namespace, name=name,handlerFunction=handlerFunction,**kwargs)
    print(watcher.url)

def main():
    url = ""
    token = ""

    client = KubernetesClient(url=url,token=token)
    test_watcher_base(client,"default","Pod",handlerFunction=deal_watch(),timeoutSeconds=3)
    test_CRUD(client=client)

    print("current thread count: ",KubernetesClient.getWatchThreadCount())
    time.sleep(7)
    # because of the timeoutSecond=3, watching thread is leave.
    print("current thread count: ",KubernetesClient.getWatchThreadCount())

if __name__ == '__main__':
    main()
```

## Security
[![Security Status](https://v3-hkylzjk.murphysec.com/platform3/v3/badge/1611080278760534016.svg)](https://www.murphysec.com/accept?code=d4fc93265c005aada8b96fde2d64bb9d&type=1&from=2&t=2)
