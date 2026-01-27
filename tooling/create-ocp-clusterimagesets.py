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

import requests
import os
import os.path
import get_support_version

BRANCH = os.environ.get("TARGET_BRANCH")
VERSIONS = get_support_version.get_support_version(BRANCH)

#compare if version1 is bigger than version2
#return false if they are same
def compare_version(version1, version2):
    version1List = version1.split(".")
    version2List = version2.split(".")
    if int(version1List[0]) > int(version2List[0]):
       return True
    if int(version1List[0]) < int(version2List[0]):
       return False
    if int(version1List[1]) > int(version2List[1]):
       return True
    return False

#check if branch should use combined TAG@SHA format
#returns true for backplane-2.11 and higher
def use_combined_tag_sha(branch):
    if branch is None:
        return False
    if not branch.startswith("backplane-"):
        return False
    try:
        version = branch.replace("backplane-", "")
        version_parts = version.split(".")
        major = int(version_parts[0])
        minor = int(version_parts[1])
        return (major > 2) or (major == 2 and minor >= 11)
    except (ValueError, IndexError):
        return False

USE_COMBINED_TAG_SHA = use_combined_tag_sha(BRANCH)
     
if len(VERSIONS)==0:
    print(">>ERROR<< Make sure the VERSIONS is configured\n")
    sys.exit(2)

for version in VERSIONS:
    print(" Checking for release images: " + version + ".x")
    if not os.path.isdir("clusterImageSets/releases/" + version):
        newDir = "clusterImageSets/releases/" + version
        print(" Create directory: " + newDir)
        os.mkdir(newDir)
    
    i = 1
    while True:
        resp = requests.get('https://quay.io/api/v1/repository/openshift-release-dev/ocp-release/tag', "page="+str(i))
        if resp.status_code != 200:
            # There was a problem
            raise ValueError('GET quay.io status code: %s\n%s' % (resp.status_code, resp.text))

        # Loop through all images found in quay.io
        for tagInfo in resp.json()['tags']:
            tag = tagInfo["name"]
            #Should ignore img4.12.0-multi-x86_64
            #Should include img4.12.0-multi
            #Should include and img4.12.2-x86_64
            if ((version+"." in tag) and (str(tag).endswith("multi") or (str(tag).endswith("x86_64") and "multi" not in tag))):
                print('Checking tag: {}'.format(tag), end='')
                if (not compare_version(version, "4.11")) and (str(tag).endswith("multi")):
                    # support multi-arch after 4.12
                    continue
                # Check if we already have the file in the stable, fast or releases channel
                fileName="img" + tag + ".yaml"
                fileNotFound=True
                if not os.path.isfile("clusterImageSets/releases/" + version + "/" + fileName):
                    imgName=tag.replace("_","-")
                    yaml= open("clusterImageSets/releases/" + version + "/" + fileName,"w+")
                    if USE_COMBINED_TAG_SHA:
                        releaseImage = "quay.io/openshift-release-dev/ocp-release:" + tag + "@" + tagInfo["manifest_digest"]
                    else:
                        releaseImage = "quay.io/openshift-release-dev/ocp-release:" + tag
                    cisr = ("---\n" +
                            "apiVersion: hive.openshift.io/v1\n"
                            "kind: ClusterImageSet\nmetadata:\n"
                            "  name: img" + imgName + "-appsub\n"
                            "  labels:\n"
                            "    channel: candidate\n"
                            "    visible: \"false\"\n"
                            "spec:\n"
                            "  releaseImage: " + releaseImage + "\n")
                    yaml.write(cisr)
                    yaml.close()
                    print(" Created clusterImageSet")
                else:
                    print(" Skipped, already exists")
        if resp.json()['has_additional'] != True:
            break
        i = i+1
