# Author: jnpacker

import requests
import yaml
import os
import os.path

VERSIONS = os.environ.get("LIST_VERSIONS").split(" ")
for version in VERSIONS:
  stableChannelUrl="https://raw.githubusercontent.com/openshift/cincinnati-graph-data/master/channels/stable-" + version + ".yaml"
  print(" Checking for stable version of OpenShift " + version + " from Cincinnati\n  " + stableChannelUrl)
  resp = requests.get(stableChannelUrl)
  if resp.status_code != 200:
    # There was a problem
    raise ValueError('GET ' + stableChannelUrl + ' {}'.format(resp.status_code))

  # Obtain the stable channel YAML file from the Cincinnati repository in github
  stableImages = yaml.load(resp.text, Loader=yaml.SafeLoader)
  foundVersion = False
  for imageTag in stableImages['versions']:
    
    # Check an make sure the tag matches the version we're working on
    if imageTag.startswith(version):
      foundVersion = True
      print("Looking for stable release image: " + imageTag, end='')
      
      # If the clusterImageSet yaml file is in the fast channel folder, promote it to the stable and remove from fast.
      fastFilePath="clusterImageSets/fast/" + version + "/img"+imageTag+"-x86_64.yaml"
      if os.path.isfile(fastFilePath):
        print(" (Found)", end='')
        stableFilePath="clusterImageSets/stable/" + version + "/img"+imageTag+"-x86_64.yaml"
        with open(fastFilePath, 'r') as fastOut:
          fastClusterImageSet = yaml.load(fastOut, Loader=yaml.SafeLoader)
        fastClusterImageSet['metadata']['labels']['channel'] = "stable"
        with open(stableFilePath, 'w') as stableOut:
          yaml.dump(fastClusterImageSet, stableOut, default_flow_style=False)
        print("   (PROMOTED)")
        os.remove(fastFilePath)
      # If the clusterImageSet yaml file is not found, do nothing
      else:
        print(" (SKIPPED)")
  if not foundVersion:
    print(" No release images found matching " + version + " in versions: " + str(stableImages['versions']))
print("Done!")
