#!/bin/bash
git checkout $TRAVIS_BRANCH
git status
git add clusterImageSets/*
git commit --message "clusterImageSets updated. Travis build: $TRAVIS_BUILD_NUMBER"

echo "Creating remote"
git remote add acm-hive-ocp-releases https://${GH_TOKEN}@github.com/open-cluster-management/acm-hive-openshift-releases.git > /dev/null 2>&1
echo "Push changes"
git push --set-upstream acm-hive-ocp-releases $GH_BRANCH