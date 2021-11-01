import sys
import os
from distutils.version import LooseVersion

BRANCH = environ.get("TRAVIS_BRANCH")
LIST_VERSION = os.environ.get("LIST_VERSIONS-"+BRANCH)
if not LIST_VERSION:
    print(">>ERROR<< Make sure the LIST_VERSIONS environment variable is configured\n")
    sys.exit(2)

VERSIONS = LIST_VERSION.split(" ")
if (len(sys.argv) != 3):
    print("Command example: python prune.py <COUNT_TO_KEEP> <PATH_TO_PRUNE>\n  If COUNT_TO_KEEP is 3, at most, three latest versions will remain\n")
    sys.exit(1)

keep = int(sys.argv[1]) + 1 # Now that we keep 1 invisible image, we must account for it in pruning
path = sys.argv[2]

if  not os.path.isdir(path):
    print(">>ERROR<< Provide a valid path to prune\n")
    sys.exit(2)

for version in VERSIONS:
    prunePath = path + "/" + version
    print("\nPruning path: " + prunePath)
    if os.path.isdir(prunePath):
        filesDirs = os.listdir(prunePath)
        sortedData = sorted(filesDirs, key=LooseVersion, reverse=True)
        print("Found: " + str(sortedData))

        counter = 1
        for i in sortedData:
            filePath = (prunePath + "/" + i).replace("//","/")
            if counter > keep and os.path.isfile(filePath):
                print("Pruning: " + filePath)
                os.remove(filePath)
            else:
                print("Leaving: " + filePath)
            counter = counter + 1
    else:
        print("\nPruning path not found\n")







