'''
 * Copyright (2024, ) Institute of Software, Chinese Academy of Sciences
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 '''
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
    
