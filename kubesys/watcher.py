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
import inspect
import ctypes
from kubesys.common import formatURL, getParams

__author__ = ('Tian Yu <yutian20@otcaix.iscas.ac.cn>',
              'Heng Wu <wuheng@iscas.ac.cn>')


class KubernetesWatcher():
    def __init__(self, thread_t, kind, namespace, watcher_handler, name, url, **kwargs):
        self.thread_t = thread_t
        self.thread_name = self.thread_t.getName()
        self.kind = kind
        self.namespace = namespace
        self.watcherhandler = watcher_handler
        self.name = name
        self.is_daemon = self.thread_t.isDaemon()
        self.url = formatURL(url, getParams(kwargs))

    def run(self) -> None:
        self.thread_t.start()

    def join(self) -> None:
        self.thread_t.join()

    def is_alive(self) -> bool:
        return self.thread_t.is_alive()

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop(self):
        self._async_raise(self.thread_t.ident, SystemExit)
