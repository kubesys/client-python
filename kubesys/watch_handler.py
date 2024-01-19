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
from kubesys.common import dictToJsonString

__author__ = ('Tian Yu <yutian20@otcaix.iscas.ac.cn>',
              'Heng Wu <wuheng@iscas.ac.cn>')


class WatchHandler():
    def __init__(self, add_func=lambda json_dict: print("ADDED: ", dictToJsonString(json_dict)),
                 modify_func=lambda json_dict: print("MODIFIED: ", dictToJsonString(json_dict)),
                 delete_func=lambda json_dict: print("DELETED: ", dictToJsonString(json_dict))) -> None:
        self.DoAdded = add_func
        self.DoModified = modify_func
        self.DoDeleted = delete_func
