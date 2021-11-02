#!/bin/bash
cd hive-cluster-testing
if [ $? -ne 0 ]; then
  echo "Did not find cloned Gitrepo hive-cluster-testing"
  exit 1
fi
git add deployed/*
git commit --message "Hive test cluster deploy added. Travis build: $TRAVIS_BUILD_NUMBER"

echo "Creating remote"
git remote add hive-cluster-testing https://${GH_TOKEN}@github.com/open-cluster-management/hive-cluster-testing.git > /dev/null 2>&1

echo "Push changes"
git push --set-upstream hive-cluster-testing $TRAVIS_BRANCH

echo "Remove ./hive-cluster-testing"
cd ..
rm -rf ./hive-cluster-testing
if [ $? -ne 0 ]; then
  echo "There was a problem removing hive-cluster-testing"
  exit 1
fi
