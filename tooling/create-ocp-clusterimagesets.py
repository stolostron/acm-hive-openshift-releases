import requests
import os
import os.path
import get_support_version

BRANCH = os.environ.get("TRAVIS_BRANCH")
VERSIONS = get_support_version.get_support_version(BRANCH)

if len(VERSIONS)==0:
    print(">>ERROR<< Make sure the VERSIONS is configured\n")
    sys.exit(2)

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
                    cisr = ("---\n" +
                            "apiVersion: hive.openshift.io/v1\n"
                            "kind: ClusterImageSet\nmetadata:\n"
                            "  name: img" + imgName + "-appsub\n"
                            "  labels:\n"
                            "    channel: candidate\n"
                            "    visible: \"false\"\n"
                            "spec:\n"
                            "  releaseImage: quay.io/openshift-release-dev/ocp-release:" + tag + "\n")
                    yaml.write(cisr)
                    yaml.close()
                    print(" Created clusterImageSet")
                else:
                    print(" Skipped, already exists")
