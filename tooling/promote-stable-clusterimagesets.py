# Author: jnpacker

import requests
import yaml
import os
import os.path

VERSIONS = os.environ.get("LIST_VERSIONS").split(" ")
CHANNELS = ["stable", "fast"]
for version in VERSIONS:
  for channel in CHANNELS:
    channelUrl="https://raw.githubusercontent.com/openshift/cincinnati-graph-data/master/channels/" + channel + "-" + version + ".yaml"
    print("---\n Checking for " + channel + " version of OpenShift " + version + " from Cincinnati\n  " + channelUrl)
    resp = requests.get(channelUrl)
    if resp.status_code != 200:
      # There was a problem
      raise ValueError('GET ' + channelUrl + ' {}'.format(resp.status_code))

    # Obtain the stable channel YAML file from the Cincinnati repository in github
    images = yaml.load(resp.text, Loader=yaml.SafeLoader)
    foundVersion = False
    i = 0
    for imageTag in images['versions']:
      i = i + 1
      # Check an make sure the tag matches the version we're working on
      if imageTag.startswith(version):
        foundVersion = True
        print("  Looking for stable release image: " + imageTag, end='')
        
        # Change the channel label is found
        filePath="clusterImageSets/releases/" + version + "/img"+imageTag+"-x86_64.yaml"
        if os.path.isfile(filePath):
          print(" (Found)", end='')
          #stableFilePath="clusterImageSets/stable/" + version + "/img"+imageTag+"-x86_64.yaml"
          # Load the current yaml
          with open(filePath, 'r') as fileIn:
            fastClusterImageSet = yaml.load(fileIn, Loader=yaml.SafeLoader)
          
          # Update the channel
          if fastClusterImageSet['metadata']['labels']['channel'] != channel and fastClusterImageSet['metadata']['labels']['channel'] != "stable" :
            fastClusterImageSet['metadata']['labels']['channel'] = channel
            with open(filePath, 'w') as fileOut:
              yaml.dump(fastClusterImageSet, fileOut, default_flow_style=False)
            print(" (Labelled as " + channel + " channel)", end='')
          
          # Place the YAML into the correct channel
          channelPath = "clusterImageSets/" + channel + "/" + version + "/"
          channelImage = channelPath + "img"+imageTag+"-x86_64.yaml"
          if i >= len(images['versions'])-1 and not os.path.isfile(channelImage):
            # Deal with a scenario that the directory does not exist
            if not os.path.isdir(channelPath):
              os.mkdir(channelPath)
            with open(channelImage, 'w') as fileOut:
              yaml.dump(fastClusterImageSet, fileOut, default_flow_style=False) 
            print(" Published to " + channel + " channel")
          else:
            print(" (SKIPPED)")

        # If the clusterImageSet yaml file is not found, do nothing
        else:
          print(" (SKIPPED)")
    if not foundVersion:
      print(" No release images found matching " + version + " in versions: " + str(images['versions']))
print("Done!")
