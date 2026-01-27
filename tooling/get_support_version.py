# Copyright 2025 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# This file was modified with assistance from generative AI.

import json
import sys

def get_support_version(branch):
   if branch is None:
      print("ERROR: TARGET_BRANCH environment variable is not set.")
      print("Set it to a valid branch name from supported-ocp-versions.json")
      print("Example: TARGET_BRANCH=backplane-2.10 make sync-images-job")
      sys.exit(1)

   with open("supported-ocp-versions.json", "r", encoding="UTF-8") as file:
      obj = json.load(file)

   if branch not in obj:
      print(f"ERROR: Branch '{branch}' not found in supported-ocp-versions.json")
      print(f"Available branches: {', '.join(obj.keys())}")
      sys.exit(1)

   return obj[branch]