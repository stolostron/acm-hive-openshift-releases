import requests
import os
import os.path
import get_support_version

BRANCH = os.environ.get("TARGET_BRANCH")
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
    
    i = 1
    while True:
        resp = requests.get('https://quay.io/api/v1/repository/openshift-release-dev/ocp-release/tag', "page="+str(i))
        if resp.status_code != 200:
            # There was a problem
            raise ValueError('GET quay.io status code: %s\n%s' % (resp.status_code, resp.text))

        # Loop through all images found in quay.io
        for tagInfo in resp.json()['tags']:
            tag = tagInfo["name"]
            #Should ignore img4.11.0-multi-x86_64
            #Should ignore img4.11.0-multi 
            #Should include and img4.11.2-x86_64
#            if ((version+"." in tag) and (str(tag).endswith("multi") or (str(tag).endswith("x86_64") and "multi" not in tag))):
            if ((version+"." in tag) and ((str(tag).endswith("x86_64") and "multi" not in tag))):
                print('Checking tag: {}'.format(tag), end='')
                # Check if we already have the file in the stable, fast or releases channel
                fileName="img" + tag + ".yaml"
                fileNotFound=True
                if not os.path.isfile("clusterImageSets/releases/" + version + "/" + fileName):
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
        if resp.json()['has_additional'] != True:
            break
        i = i+1
