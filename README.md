# NOTICE:
On **11-01-2021** we changed the default retention for clusterImageSets. Going forward we will include all supported clusterImageSets with the suffix `-appsub`, but only the latest clusterImageSet will be visible (`metadata.labels.visible: 'true'`) in the console (this is similar to what happens today). This was done to make sure that after two new Z stream releases, any provisioning flow that references a clusterImageSet will not be interrupted.

# OpenShift Release Images
This repository provides ClusterImageSet resources that populate OpenShift release images into Advanced Cluster Management for OpenShift deployments. More information about OpenShift release images and the channels mentioned below can be found here: https://docs.openshift.com/container-platform/4.4/updating/updating-cluster-between-minor.html#understanding-upgrade-channels_updating-cluster-between-minor

# Repository layout
- `fast` `./clusterImageSets/fast/*` : The fast channel OpenShift releases, generally available and fully supported
- `stable` `./clusterImageSets/stable/*` : The latest stable OpenShift releases, same as fast, but with connected customer feedback
- `candidate` `./clusterImageSets/releases/*` : All release images are in this folder, those labelled `candidate` releases are not supported

See the `Offline Deployments` section on controlling your own OpenShift release timelines with Advanced Cluster Management

# Make Targets

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TARGET_BRANCH` | Yes | - | Branch name from `supported-ocp-versions.json` (e.g., `backplane-2.10`) |
| `STABLE_KEEP_COUNT` | No | 2 | Stable channel images to retain. Do not modify unless required. |
| `FAST_KEEP_COUNT` | No | 1 | Fast channel images to retain. Do not modify unless required. |
| `DEBUG` | No | - | Set to `true` for verbose logging |

## Syncing ClusterImageSets

Sync ClusterImageSets from upstream OpenShift releases:

```bash
TARGET_BRANCH=backplane-2.10 make sync-images-job
```

This target:
1. Cleans up existing ClusterImageSet files
2. Fetches the latest release images from OpenShift channels
3. Marks appropriate images as visible in the console
4. Prunes older images based on retention settings

Example with custom retention:
```bash
TARGET_BRANCH=backplane-2.10 STABLE_KEEP_COUNT=3 make sync-images-job
```

## Validation

Validate ClusterImageSet YAML files before committing changes:

### Structure validation only (fast)
```bash
make validate-images
```
Validates YAML syntax, required fields, and image reference format.

### Full validation with registry checks
```bash
make validate-images-registry
```
Additionally verifies that each image exists in quay.io (no authentication required).

## Branch Management

Manage release branches for different backplane versions:

### View branch suggestions
```bash
make suggest-branch
```

Shows the last 3 backplane releases and suggests the next branch with appropriate OCP versions. No changes are made.

### Add a new branch
```bash
make add-branch
```

Interactive mode that:
1. Shows the last 3 backplane releases
2. Suggests the next branch and OCP versions
3. Prompts for confirmation
4. Automatically updates all required files:
   - `supported-ocp-versions.json`
   - `.github/workflows/cron-sync-imageset.yml`
   - `.github/workflows/post-submit-imageset.yml`

After running, create a PR to `main`. The new branch will be created automatically when the GitHub Action runs.

### Example

```
$ make add-branch

=== Last 3 Backplane Releases ===
--------------------------------------------------
  backplane-2.8: OCP 4.16, 4.17, 4.18, 4.19
  backplane-2.9: OCP 4.17, 4.18, 4.19, 4.20
  backplane-2.10: OCP 4.18, 4.19, 4.20, 4.21
--------------------------------------------------

=== Suggested Next Branch ===
  Branch: backplane-2.11
  OCP Versions: 4.19, 4.20, 4.21, 4.22

==================================================
Add backplane-2.11 with OCP versions ['4.19', '4.20', '4.21', '4.22']? [Y/n]: y

Adding backplane-2.11...
  Updated supported-ocp-versions.json
  Updated .github/workflows/cron-sync-imageset.yml
  Updated .github/workflows/post-submit-imageset.yml

Done! Files updated:
  - supported-ocp-versions.json
  - .github/workflows/cron-sync-imageset.yml
  - .github/workflows/post-submit-imageset.yml

Next steps:
  1. Review the changes: git diff
  2. Commit and create a PR to main
  3. The backplane-2.11 branch will be created automatically on first workflow run
```

### Release Image Format

ClusterImageSet files use different `releaseImage` formats depending on the branch:

| Branch | releaseImage format |
|--------|---------------------|
| backplane-2.10 and below | `quay.io/.../ocp-release:4.19.0-x86_64` |
| backplane-2.11 and above | `quay.io/.../ocp-release:4.19.0-x86_64@sha256:...` |

The combined tag and SHA digest format provides both human-readable version information and cryptographic integrity verification.

This is controlled by the `use_combined_tag_sha()` function in `tooling/create-ocp-clusterimagesets.py`.

# Offline Deployments

For disconnected environments:

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
- The Create Cluster console will list only the images available from the `clusterImageSets` directory

# Channel Subscription (Deprecated)

For legacy subscription-based deployments, see [SUBSCRIBE.md](SUBSCRIBE.md).
