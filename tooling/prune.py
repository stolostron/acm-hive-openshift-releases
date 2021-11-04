import sys
import os
from distutils.version import LooseVersion
import get_support_version
import shutil

BRANCH = os.environ.get("TARGET_BRANCH")
VERSIONS = get_support_version.get_support_version(BRANCH)

if (len(sys.argv) != 3):
    print("Command example: python prune.py <COUNT_TO_KEEP> <PATH_TO_PRUNE>\n  If COUNT_TO_KEEP is 3, at most, three latest versions will remain\n")
    sys.exit(1)

keep = int(sys.argv[1]) + 1 # Now that we keep 1 invisible image, we must account for it in pruning
path = sys.argv[2]

if not os.path.isdir(path):
    print(">>ERROR<< Provide a valid path to prune\n")
    sys.exit(2)

versionMap = {}
for version in VERSIONS:
    prunePath = path + "/" + version
    print("\nSupporting path: " + prunePath)
    versionMap[prunePath] = ""

filesDirs = os.listdir(path)
for fileDir in filesDirs:
    curDir = path + "/" + fileDir
    if curDir in versionMap:
        print("Leaving : " + curDir)
    else:
        print("Removing: " + curDir)
        shutil.rmtree(curDir)






