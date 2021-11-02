#!/bin/bash
if [ "${GH_TOKEN}" == "" ]; then
  echo "Make sure the environment variable export GH_TOKEN is set"
  exit 1
fi

if [ -d hive-cluster-testing ]; then
  cd hive-cluster-testing
  git checkout $TRAVIS_BRANCH
  git pull
  cd ..
else
  echo "Git clone open-cluster-management/hive-cluster-testing"
  git clone https://${GH_TOKEN}@github.com/open-cluster-management/hive-cluster-testing > /dev/null 2>&1
    if [ $? -ne 0 ]; then
    echo "Git clone of open-cluster-management/hive-cluster-testing failed"
    exit 1
  fi
fi
chmod 755 hive-cluster-testing/scripts/*.sh

