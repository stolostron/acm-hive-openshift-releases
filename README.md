# NOTICE:
On **11-01-2021** we changed the default retention for clusterImageSets. Going forward we will include all supported clusterImageSets with the suffix `-appsub`, but only the latest clusterImageSet will be visible (`metadata.labels.visible: 'true'`) in the console (this is similar to what happens today). This was done to make sure that after two new Z stream releases, any provisioning flow that references a clusterImageSet will not be interrupted. 

# OpenShift Release Images
This repository provides a subscription that will populate all the latest OpenShift images into Advanced Cluster Management for OpenShift deployments. More information about OpenShift release images and the channels mentioned below can be found here: https://docs.openshift.com/container-platform/4.4/updating/updating-cluster-between-minor.html#understanding-upgrade-channels_updating-cluster-between-minor

# Repository layout
- `fast` `./clusterImageSets/fast/*` : The fast channel OpenShift releases, generally available and fully supported
- `stable` `./clusterImageSets/stable/*` : The latest stable OpenShift releases, same as fast, but with connected customer feedback
- `candidate` `./clusterImageSets/releases/*` : All release images are in this folder, those labelled `candidate` releases are not supported

See the `Custom curated` section on controlling your own OpenShift release timelines with Advanced Cluster Management

# Red Hat Advanced Cluster Management for Kubernetes
With this release, the subscription that imports the fast channel is already present. If you want to use a different channel, first pause the existing `fast` channel subscription using [these instructions](https://github.com/stolostron/rhacm-docs/blob/2.4_stage/clusters/release_images.adoc). Once the included subscription is disabled, follow the steps below to switch to a different channel.

## Latest supported images (ONLINE) - DEFAULT
- Populates the latest OpenShift `fast` release images
- Run the following command
```bash
# Connect to you Red hat Advanced Cluster Management hub
# On OpenShift Dedicated, run "oc new-project hive-clusterimagesets"
make subscribe-fast
```
- After about 60s the Create Cluster console will list the latest supported OpenShift images
## Stable channel images
- Populates the latest 2x `stable` release images
```bash
make subscribe-stable
```

### How to pause the subscription
#### Prerequisites
1. The stable channel subscription has been applied
2. Logged into the ACM hub
#### Pause the Fast Channel subscription
```bash
make pause-stable

# Alternate CLI command:
oc -n hive patch appsub hive-clusterimagesets-subscription-stable-0 --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"true"}]'
```
#### Unpause the Stable Channel subscription
```bash
make unpause-stable

# Alternate CLI command:
oc -n hive patch appsub hive-clusterimagesets-subscription-stable-0 --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"false"}]'
```

### Continuous updates
- This repository periodically updates as new fast and stable release images are minted
- Changes in this repository will be applied to your subscribed cluster
- This is the stable channel list being followed by this repository, [link](https://github.com/openshift/cincinnati-graph-data/blob/master/channels/stable-4.3.yaml)

### Uninstall
```bash
make unsubscribe-all

# Alternate CLI commands:
oc delete -k subscribe/
oc delete -f subscribe/subscription-stable.yaml  #If your using the stable channel
```

## Custom curated (ONLINE)
- Fork this repository
- Update the `./subscribe/channel.yaml` file, changing the organization `stolostron` to your `organization_name` or `github_username` where you forked the repository.
```yaml
spec:
  type: GitHub
  pathname: https://github.com/NAME_or_ORGANIZATION/acm-hive-openshift-versions.git
```
- Place the YAML files for the images you want to appear in the Red Hat Advanced Cluster Management console under `./clusterImageSets/stable/*` or `./clusterImageSets/fast/*`
- Commit and push your changes to the forked repository
- Run the following command
```bash
make subscribe-fast   #fast channel
make subscribe-stable #stable channel
```
- After about 60s the Create Cluster console will list the new images available from your forked repository
- Add new OpenShift install images by created additional files in the `clusterImageSets/stable/` or `clusterImageSets/fast/` directories

## How to get new versions
- This repository will automatically update with the latest stable and fast versions
- You can monitor this repository and merge changes to your forked repository
- As soon as new images are committed to this repository and merged to your fork, they will become available in the Red Hat Advanced Cluster Management console (about 60s)
- This is the install image repository being used: https://quay.io/repository/openshift-release-dev/ocp-release?tab=tags
- These are the streams being followed by this repository: https://github.com/openshift/cincinnati-graph-data/blob/master/channels/

## Usecase - OFFLINE - limited images
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
oc apply -f clusterImageSets/CHANNEL/VERSION/FILE_NAME.yaml
```
- The Create Cluster console will list only the images available from the `cluseterImageSets` directory

## Secure Github repository
- Uncomment the secret reference in `subscribe/channel.yaml`
- Create a `subscribe/secret.yaml` file with the following contents
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
make subscribe-fast
# OR
make subscribe-stable
```
