import requests
import yaml
import os
import os.path
import logging
import get_support_version
def MoveToChannel( filePath, channel ):
    print (" Move " + filePath + " to channel " + channel)
    if os.path.isfile(filePath):
      print(" (Found)", end='')
      # Load the current yaml
      with open(filePath, 'r') as fileIn:
        fastClusterImageSet = yaml.load(fileIn, Loader=yaml.SafeLoader)
      
      # Update the channel
      if fastClusterImageSet['metadata']['labels']['channel'] != channel and fastClusterImageSet['metadata']['labels']['channel'] != "stable" :
        fastClusterImageSet['metadata']['labels']['channel'] = channel
        fastClusterImageSet['metadata']['labels']['visible'] = "false"
        with open(filePath, 'w') as fileOut:
          yaml.dump(fastClusterImageSet, fileOut, default_flow_style=False)
        print(" (Channel changed)", end='')

        # Place the YAML into the correct channel
        channelPath = "clusterImageSets/" + channel + "/" + version + "/"
        channelImage = filePath.replace("releases", channel, 1)
        if not os.path.isfile(channelImage):
          # Deal with a scenario that the directory does not exist
          if not os.path.isdir(channelPath):
            logging.info(" (Create directory: " + channelPath + ")")
            os.mkdir(channelPath)
          with open(channelImage, 'w') as fileOut:
            yaml.dump(fastClusterImageSet, fileOut, default_flow_style=False) 
          print(" (Published to " + channel + " channel)", end='')
      else:
        print(" (SKIPPED)")
    # If the clusterImageSet yaml file is not found, do nothing
    else:
      print(" (SKIPPED)")
            # Change the channel label is found
    
# Configure the logs
logLevel = logging.INFO
if os.environ.get("DEBUG") == "true":
  logLevel = logging.DEBUG
logging.basicConfig(format='%(asctime)s-%(levelname)s - %(message)s',level=logLevel)

BRANCH = os.environ.get("TARGET_BRANCH")
VERSIONS = get_support_version.get_support_version(BRANCH)

if len(VERSIONS)==0:
    print(">>ERROR<< Make sure the VERSIONS is configured\n")
    sys.exit(2) 

CHANNELS = ["fast", "stable"]
for version in VERSIONS:
  for channel in CHANNELS:
    channelUrl="https://raw.githubusercontent.com/openshift/cincinnati-graph-data/master/channels/" + channel + "-" + version + ".yaml"
    logging.info("Checking for " + channel + " version of OpenShift " + version + " from Cincinnati\n  " + channelUrl)
    resp = requests.get(channelUrl)
    if resp.status_code != 200:
      # There was a problem
      if resp.status_code == 404:
        logging.warning('FileNotFound: GET ' + channelUrl + ' {}'.format(resp.status_code))
        continue
      else:
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
        MoveToChannel(filePath, channel)
        # Handle the multi arch image
        filePath="clusterImageSets/releases/" + version + "/img"+imageTag+"-multi.yaml"
        MoveToChannel(filePath, channel)

    if not foundVersion:
      logging.info(" No release images found matching " + version + " in versions: " + str(images['versions']))
logging.info("Done!")
