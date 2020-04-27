#!/bin/bash
git checkout -b $GH_BRANCH
git add ./cluster_imageSets *
git commit --message "Travis build: $TRAVIS_BUILD_NUMBER"

git remote add acm-hive-ocp-releases https://${GH_TOKEN}@github.com/open-cluster-management/acm-hive-openshift-releases.git > /dev/null 2>&1
git push --quiet --set-upstream acm-hive-ocp-releases $GH_BRANCH