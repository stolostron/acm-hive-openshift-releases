# OpenShift Release Images
This repository provides a subscription that will populate all the latest OpenShift images into ACM for depoyment

# Changes to the default images in the channel
- This repository will provide the two latest `stable` images and the initial image for OpenShift 4.3.
- Also included will be the two latest release candidates for OpenShift 4.4
- To learn how to curate your own images, see `ONLINE - custom curated` below

## ONLINE - latest stable images
- Populates the 2x latest OpenShift stable release images, the base stable image for 4.3.0 and the two latest 4.4 release candidates for use with Advanced Cluster Management
- Run the following command
```bash
oc apply -k subscription/
```
- After about 60s the Create Cluster user interface will list all available OpenShift 4.4 images

## ONLINE - custom curated
- Fork this repository
- Update the the `./subscription/channel.yaml` file, changing `open-cluster-management` to your `name` or `organization` for the forked repository.
```yaml
spec:
  type: GitHub
  pathname: https://github.com/NAME_or_ORGANIZATION/acm-hive-openshift-versions.git
```
- Place the YAML files for the images you want to appear in the ACM UI under `./clusterImageSets/4.3` or `./clusterImageSets/4.4`
- Commit and push your changes to the forked repository
- Run the following command
```bash
oc apply -k subscription/
```
- After about 60s the Create Cluster user interface will list only the images available in  your forked repository
- Add new OpenShift install images by created additional files in the `4.3` and `4.4` directories

## How to get new versions
- This repository will automatically update with the latest stable versions
- You can monitor this repository and merge changes if you forked it
- As soon as new images are committed to this repository or your fork, they will become available in the ACM console within 60s
- This is the stable stream: https://github.com/openshift/cincinnati-graph-data/blob/master/channels/stable-4.3.yaml


## (ALPHA) Usecase - OFFLINE - limited images
- Copy the `clusterImageSets` directory to a system that has access to the disconnected Advanced Cluster Management Hub
- Delete the YAML files for OpenShift versions you do not want to host OFFLINE
- Modify the `clusterImageSet` YAML files for the remaining OpenShift release images to point to the correct OFFLINE repository
```yaml
apiVersion: hive.openshift.io/v1
kind: ClusterImageSet
metadata:
    name: img4.4.0-rc.6-x86-64
spec:
    releaseImage: IMAGE_REGISTRY_IPADDRESS_or_DNSNAME/REPO_PATH/ocp-release:4.4.0-rc.6-x86_64
```
- Make sure the images are loaded in the OFFLINE image registry referenced in the YAML
- Apply a subset of the YAML files
```bash
oc apply -f clusterImageSets/
```
- The Create Cluster user interface will list only the images available from the `cluseterImageSets` directory

## Secure Github repostiory
- Uncomment the secret reference in `subscription/channel.yaml`
- Create a `subscription/secret.yaml` file with the following contents
```yaml
---
  apiVersion: v1
  kind: Secret
  metadata:
    name: my-github-secret
    namespace: ocp-clusterimagesets
  data:
    user: BASE64_ENCODED_GITHUB_USERNAME
    accessToken: BASE64_ENCODED_GITHUB_TOKEN
```
- The following command is used to encode base64: `echo "VALUE_TO_ENCODE" | base64`  place the output in the yaml file.
- Create the secret
```bash
oc apply -f subscription/secret.yaml
``