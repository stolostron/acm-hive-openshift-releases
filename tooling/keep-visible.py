import yaml
import sys
import os
from distutils.version import LooseVersion

LIST_VERSION = os.environ.get("LIST_VERSIONS")
if not LIST_VERSION:
    print(">>ERROR<< Make sure the LIST_VERSIONS environment variable is configured\n")
    sys.exit(2)

VERSIONS = LIST_VERSION.split(" ")
if (len(sys.argv) != 3):
    print("Command example: python visible.py <COUNT_TO_KEEP> <PATH_TO_HIDE>\n  If COUNT_TO_KEEP is 3, at most, three latest versions will remain\n")
    sys.exit(1)

keep = int(sys.argv[1])
path = sys.argv[2]

print("\nKeep " + str(keep) + " ClusterImageSet resource(s) visible")
if  not os.path.isdir(path):
    print(">>ERROR<< Provide a valid path\n")
    sys.exit(2)

for version in VERSIONS:
    visiblePath = path + "/" + version
    print("Looking in path: " + visiblePath)
    if os.path.isdir(visiblePath):
        filesDirs = os.listdir(visiblePath)
        sortedData = sorted(filesDirs, key=LooseVersion, reverse=True)
        print("Found: " + str(sortedData))

        counter = 1
        for i in sortedData:
            filePath = (visiblePath + "/" + i).replace("//","/")
            if counter > keep and os.path.isfile(filePath):
                print("Visible: false for " + filePath)
                with open(filePath, 'r') as fileIn:
                    clusterImageSet = yaml.load(fileIn, Loader=yaml.SafeLoader)
                clusterImageSet['metadata']['labels']['visible'] = "false"
                with open(filePath, 'w') as fileOut:
                    yaml.dump(clusterImageSet, fileOut, default_flow_style=False)
            else:
                print("Visible: true for " + filePath)
            counter = counter + 1
    else:
        print("\nPath not found\n")







