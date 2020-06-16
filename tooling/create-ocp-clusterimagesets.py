# Author: jnpacker

import requests
import os
import os.path

# To support new versions, add them to this array
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")
SLACK_FYI =  os.environ.get("SLACK_FYI")
VERSIONS = os.environ.get("LIST_VERSIONS").split(" ")
for version in VERSIONS:
    print(" Checking for release images: " + version + ".x")
    if not os.path.isdir("clusterImageSets/releases/" + version):
        newDir = "clusterImageSets/releases/" + version
        print(" Create directory: " + newDir)
        os.mkdir(newDir)
    
    resp = requests.get('https://quay.io/api/v1/repository/openshift-release-dev/ocp-release/image/')
    if resp.status_code != 200:
        # There was a problem
        raise ValueError('GET quay.io status code: %s\n%s' % (resp.status_code, resp.text))
    
    # Loop through all images found in quay.io
    for image in resp.json()['images']:
        if (image['tags'] != []):
            tag=image['tags'][0]  # There is only one tag for now in each image
            if ("x86_64" in tag and version+"." in tag):
                print('Checking tag: {}'.format(tag), end='')

                # Check if we already have the file in the stable, fast or releases channel
                fileName="img" + tag + ".yaml"
                fileNotFound=True
                #for channel in ["releases","stable","fast"]:
                #    if os.path.isfile("clusterImageSets/" + channel + "/" + version + "/" + fileName):
                #        fileNotFound=False
                #if fileNotFound:
                if not os.path.isfile("clusterImageSets/releases/" + version + "/" + fileName):
                    #imgName=tag.replace("x86_64","fast")
                    imgName=tag.replace("_","-")
                    yaml= open("clusterImageSets/releases/" + version + "/" + fileName,"w+")
                    yaml.write("---\napiVersion: hive.openshift.io/v1\nkind: ClusterImageSet\nmetadata:\n    name: img" + imgName + "\n    labels:\n      channel: candidate\nspec:\n    releaseImage: quay.io/openshift-release-dev/ocp-release:" + tag + "\n")
                    yaml.close()
                    print(" Created clusterImageSet")
                    
                    if SLACK_WEBHOOK:
                        slack_data = {'text': "*NEW* *ClusterImageSet* found\nOpenShift Release `" + imgName + "` has been published <https://github.com/open-cluster-management/acm-hive-openshift-releases/tree/master/clusterImageSets/releases/"+version+"|link>\nFYI: "+SLACK_FYI}
                        response = requests.post(SLACK_WEBHOOK, json=slack_data, headers={'Content-Type': 'application/json'})
                        if response.status_code != 200:
                            raise ValueError('Request to slack returned status code: %s\n%s' % (response.status_code, response.text))
                        print(" (Slack msg sent!)")
                    else:
                        print(" (Slack not configured)")
                else:
                    print(" Skipped, already exists")
