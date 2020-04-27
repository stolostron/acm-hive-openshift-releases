# Author: jnpacker

import requests
import os
import os.path

# To support new versions, add them to this array
for version in ["4.3", "4.4"]:
    print(" Checking for release images: " + version + ".x")
    if not os.path.isdir("clusterImageSets/fast/" + version):
        print(" Create directory: clusterImageSets/fast/" + version)
        os.mkdir("clusterImageSets/fast/" + version)
    resp = requests.get('https://quay.io/api/v1/repository/openshift-release-dev/ocp-release/image/')
    if resp.status_code != 200:
        # There was a problem
        raise ApiError('GET /api/v1/ {}'.format(resp.status_code))
    # Loop through all images found in quay.io
    for image in resp.json()['images']:
        if (image['tags'] != []):
            tag=image['tags'][0]  # There is only one tag for now in each image
            if ("x86_64" in tag and version in tag):
                print('Checking tag: {}'.format(tag), end='')
                # Check if we already have the file in the primary or archive
                fileName="img" + tag + ".yaml"
                fileNotFound=True
                for channel in ["archive","stable","fast"]:
                    if os.path.isfile("clusterImageSets/" + channel + "/" + version + "/" + fileName):
                        fileNotFound=False
                if fileNotFound:
                    imgName=tag.replace("x86_64","fast")
                    yaml= open("clusterImageSets/fast/" + version + "/" + fileName,"w+")
                    yaml.write("---\napiVersion: hive.openshift.io/v1\nkind: ClusterImageSet\nmetadata:\n    name: img" + imgName + "\n    labels:\n      channel: fast\nspec:\n    releaseImage: quay.io/openshift-release-dev/ocp-release:" + tag + "\n")
                    yaml.close()
                    print(" Created clusterImageSet")
                else:
                    print(" Skipped, already exists")

# Add support to pull from these YAML: https://github.com/openshift/cincinnati-graph-data/blob/master/channels/stable-4.3.yaml