# Author: jnpacker

import requests
import yaml
import os
import os.path

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")
SLACK_FYI =  os.environ.get("SLACK_FYI")
VERSIONS = os.environ.get("LIST_VERSIONS").split(" ")
CHANNELS = ["fast", "stable"]
for version in VERSIONS:
  for channel in CHANNELS:
    channelUrl="https://raw.githubusercontent.com/openshift/cincinnati-graph-data/master/channels/" + channel + "-" + version + ".yaml"
    print("---\n Checking for " + channel + " version of OpenShift " + version + " from Cincinnati\n  " + channelUrl)
    resp = requests.get(channelUrl)
    if resp.status_code != 200:
      # There was a problem
      raise ValueError('GET ' + channelUrl + ' {}'.format(resp.status_code))

    # Obtain the channel YAML file from the Cincinnati repository in github
    images = yaml.load(resp.text, Loader=yaml.SafeLoader)
    foundVersion = False
    for imageTag in images['versions']:
      # Check an make sure the tag matches the version we're working on
      if imageTag.startswith(version):
        foundVersion = True
        print("  Looking for "+ channel + " release image: " + imageTag, end='')
        
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
            print(" (Channel changed)", end='')

            # Place the YAML into the correct channel
            channelPath = "clusterImageSets/" + channel + "/" + version + "/"
            channelImage = channelPath + "img"+imageTag+"-x86_64.yaml"
            if not os.path.isfile(channelImage):
              # Deal with a scenario that the directory does not exist
              if not os.path.isdir(channelPath):
                print(" (Create directory: " + channelPath + ")", end='')
                os.mkdir(channelPath)
              with open(channelImage, 'w') as fileOut:
                yaml.dump(fastClusterImageSet, fileOut, default_flow_style=False) 
              print(" (Published to " + channel + " channel)", end='')
              if os.path.isdir("hive-cluster-testing/AWS-Template") and channel == "fast":
                os.system("export BASEDOMAIN=dev06.red-chesterfield.com && export CLUSTER_TYPE=AWS && export CLUSTER_REGION=us-east-1 && export CLUSTER_IMAGE_SET=img"+imageTag+"-x86-64 && export CLUSTER_NAME=hive"+version.replace(".","")+"-aws-test && export OVERWRITE=no && ./hive-cluster-testing/scripts/build-cluster-subscribe-secrets.sh")
              if os.path.isdir("hive-cluster-testing/GCP-Template") and channel == "fast":
                os.system("export BASEDOMAIN=demo.gcp.red-chesterfield.com && export CLUSTER_TYPE=GCP && export CLUSTER_REGION=us-east1 && export CLUSTER_IMAGE_SET=img"+imageTag+"-x86-64 && export CLUSTER_NAME=hive"+version.replace(".","")+"-gcp-test && export OVERWRITE=no && ./hive-cluster-testing/scripts/build-cluster-subscribe-secrets.sh")
              if os.path.isdir("hive-cluster-testing/Azure-Template") and channel == "fast":
                os.system("export BASEDOMAIN=dev06.az.red-chesterfield.com && export CLUSTER_TYPE=Azure && export CLUSTER_REGION=centralus && export CLUSTER_IMAGE_SET=img"+imageTag+"-x86-64 && export CLUSTER_NAME=hive"+version.replace(".","")+"-azure-test && export OVERWRITE=no && ./hive-cluster-testing/scripts/build-cluster-subscribe-secrets.sh")
              if SLACK_WEBHOOK:
                  slack_data = {'text': "*NEW* *ClusterImageSet* promoted to `"+channel+"` channel\nOpenShift Release `" + imageTag + "` has been published <https://github.com/open-cluster-management/acm-hive-openshift-releases/tree/master/clusterImageSets/"+channel+"/"+version+"|link>\nFYI: "+SLACK_FYI}
                  response = requests.post(SLACK_WEBHOOK, json=slack_data, headers={'Content-Type': 'application/json'})
                  if response.status_code != 200:
                      raise ValueError('Request to slack returned status code: %s\n%s' % (response.status_code, response.text))
                  print(" (Slack msg sent!)")
              else:
                  print(" (Slack not configured)")
          else:
            print(" (SKIPPED)")

        # If the clusterImageSet yaml file is not found, do nothing
        else:
          print(" (SKIPPED)")
    if not foundVersion:
      print(" No release images found matching " + version + " in versions: " + str(images['versions']))
print("Done!")
