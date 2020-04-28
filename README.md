# OpenShift Release Images
This repository provides a subscription that will populate all the latest OpenShift images into Advanced Cluster Management for OpenShift deployments.

# Repository layout
This repository will provide
1. The two latest `stable` channel images via the default subscription. All older `clusterImageSets` are in `clusterImageSets/archive`
2. The two latest `fast` channel images via via the `subscription-fast.yaml`.

See the next section on curating automatic updates

## Latest stable images (ONLINE)
- Populates the 2x latest OpenShift stable release images
- Run the following command
```bash
# Connect to you Red hat Advanced Cluster Management hub
oc apply -k subscription/
```
- After about 60s the Create Cluster console will list the latest available OpenShift 4.4 stable images
### Fast channel images
- To include `fast` channel images activate the subscription-fast.yaml
```
oc apply -f subscription/subscription-fast.yaml
```

### Continuous updates
- This repository periodically updates as new fast and stable channel release images are minted
- Changes in this repository will be applied to your subscribed cluster
- This is the stable channel list being followed by this repository, [link](https://github.com/openshift/cincinnati-graph-data/blob/master/channels/stable-4.3.yaml)

### Uninstall
```
oc delete -f subscription/subscription-fast.yaml  #If your using the fast channel
oc delete -k subscription/
```

### Tested STABLE CHANNEL OpenShift install images - Latest
|         |4.3.0|4.3.5|4.3.10|4.3.11|4.3.12|4.3.13|
|:-------:|:---:|:---:|:----:|:----:|:----:|:----:|
| AWS     |  X  |  X  |   X  |   X  |   X  |   X  |
| GCP     |  X  |  X  |   X  |   X  |   X  |   X  |
| Azure   |  X  |  X  |   X  |   X  |   X  |   X  |

### Tested FAST CHANNEL OpenShift install images
|         |4.4.0-rc13|
|:-------:|:--------:|
| AWS     |     X    |
| GCP     |     X    |
| Azure   |     X    |

## Custom curated (ONLINE)
- Fork this repository
- Update the the `./subscription/channel.yaml` file, changing `open-cluster-management` organization name to your `organization name` or `github name` for the forked repository.
```yaml
spec:
  type: GitHub
  pathname: https://github.com/NAME_or_ORGANIZATION/acm-hive-openshift-versions.git
```
- Place the YAML files for the images you want to appear in the Red Hat Advanced Cluster Management console under `./clusterImageSets/stable/*` or `./clusterImageSets/fast/*`
- Commit and push your changes to the forked repository
- Run the following command
```bash
oc apply -k subscription/   #Stable channel
oc apply -f subscription/subscription-fast.yaml   #Fast channel
```
- After about 60s the Create Cluster user interface will list the new images available in your forked repository
- Add new OpenShift install images by created additional files in the `clusterImageSets/stable/*` and `clusterImageSets/fast` directories

## How to get new versions
- This repository will automatically update with the latest stable and fast versions
- You can monitor this repository and merge changes to your forked repository
- As soon as new images are committed to this repository and merged to your fork, they will become available in the Red Hat Advanced Cluster Management console (about 60s)
- This is the stable stream being followed by this repository: https://github.com/openshift/cincinnati-graph-data/blob/master/channels/stable-4.3.yaml

## (Technical Preview) Usecase - OFFLINE - limited images
- Copy the `clusterImageSets` directory to a system that has access to the disconnected Red Hat Advanced Cluster Management Hub
- Delete the YAML files for OpenShift versions you do not want to host OFFLINE
- Modify the `clusterImageSet` YAML files for the remaining OpenShift release images to point to the correct `OFFLINE` repository
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
oc apply -f clusterImageSets/FILE_NAME.yaml
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
oc apply -k subscription/
``
