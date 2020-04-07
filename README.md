# OpenShift Release Images
This repository provides a subscription that will populate all the latest OpenShift images into ACM for depoyment

## Usecase - ONLINE - all available images
- The subscription present here, populates the latest hive images of OpenShift for use with Advanced Cluster Management.
- Run the following command
```bash
oc apply -k subscription/
```
- After about 60s the Create Cluster user interface will list all available OpenShift 4.4 images

## Usecase - ONLINE - limited images
- Fork this repository
- Update the the `./subscription/channel.yaml` file, changing `open-cluster-management` to your `name` or `organization` you forked the repository to
```yaml
spec:
  type: GitHub
  pathname: https://github.com/NAME_or_ORGANIZATION/acm-hive-openshift-versions.git
```
- Delete the YAML files for Openshift versions you do not want to display in Advanced Cluster Management
- Commit and push your changes to the forked repository
- Run the following command
```bash
oc apply -k subscription/
```
- After about 60s the Create Cluster user interface will list only the images available in  your forked repository


## (ALPHA) Usecase - OFFLINE - limited images
- Copy the `clusterImageSets` directory to a system that has access to the disconnected Advanced Cluster Management Hub
- Delete the YAML files for OpenShift versions you do not want to host OFFLINE
- Modify the `clusterImageSet` YAML files for the remaining images to point to the correct OFFLINE repository
```yaml
apiVersion: hive.openshift.io/v1
kind: ClusterImageSet
metadata:
    name: img4.4.0-rc.6-x86-64
spec:
    releaseImage: IMAGE_REGISTRY_IPADDRESS_or_NAME/REPO_PATH/ocp-release:4.4.0-rc.6-x86_64
```
- Make sure the images are loaded in the OFFLINE image registry referenced in the YAML
- Apply a subset of the YAML files you will host OFFLINE
```bash
oc apply -f clusterImageSets/
```
- After about 60s the Create Cluster user interface will list only the images available in  your forked repository
