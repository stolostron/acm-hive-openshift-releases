# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository manages OpenShift release images for Advanced Cluster Management (ACM) through automated subscriptions. It contains ClusterImageSet YAML files that reference specific OpenShift release images from quay.io, organized by release channels (fast, stable, candidate).

## Key Commands

### Subscription Management
- `make subscribe-fast` - Subscribe to fast channel OpenShift releases (default)
- `make subscribe-stable` - Subscribe to stable channel releases (latest 2x stable releases)
- `make subscribe-candidate` - Subscribe to candidate channel releases
- `make unsubscribe-all` - Remove all subscriptions

### Pause/Unpause Subscriptions
- `make pause-fast` / `make unpause-fast` - Control fast channel subscription
- `make pause-stable` / `make unpause-stable` - Control stable channel subscription

### Image Management (CI/Automation)
- `make update-images` - Full image update workflow (setup, create, promote, visibility, prune)
- `make sync-images-job` - Complete CI job (cleanup + update-images)
- `make cleanup-images` - Remove old ClusterImageSet resources
- `make visible-images` - Mark latest images as visible in console

## Architecture

### Directory Structure
- `clusterImageSets/fast/` - Fast channel releases (fully supported, latest)
- `clusterImageSets/stable/` - Stable channel releases (customer feedback incorporated)
- `clusterImageSets/releases/` - All release images including candidates (not supported)
- `subscribe/` - Kubernetes subscription manifests and application definitions
- `tooling/` - Python scripts for automated image management

### Key Components

**ClusterImageSet YAML Structure:**
```yaml
apiVersion: hive.openshift.io/v1
kind: ClusterImageSet
metadata:
  labels:
    channel: fast|stable|candidate
    visible: 'true'|'false'
  name: img4.x.y-x86-64-appsub
spec:
  releaseImage: quay.io/openshift-release-dev/ocp-release:4.x.y-x86_64
```

**Automation Scripts:**
- `tooling/create-ocp-clusterimagesets.py` - Fetches new releases from quay.io API
- `tooling/promote-stable-clusterimagesets.py` - Promotes releases to stable channel
- `tooling/keep-visible.py` - Controls console visibility (FAST_KEEP_COUNT=1, STABLE_KEEP_COUNT=2)
- `tooling/prune.py` - Removes old releases beyond retention counts

**Version Support:**
- `supported-ocp-versions.json` - Maps ACM/backplane releases to supported OpenShift versions
- Version support varies by ACM release branch (release-2.x, backplane-2.x)

### Subscription Workflow
1. GitHub subscription monitors this repository
2. ACM applies ClusterImageSet manifests to hive-clusterimagesets namespace
3. Only `visible: 'true'` images appear in ACM console
4. Images with `-appsub` suffix support retention policies

## Environment Variables
- `TARGET_BRANCH` - Determines which OpenShift versions to support based on supported-ocp-versions.json
- `FAST_KEEP_COUNT` - Number of fast channel versions to keep visible (default: 1)
- `STABLE_KEEP_COUNT` - Number of stable channel versions to keep visible (default: 2)