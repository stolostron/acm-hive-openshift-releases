#!/bin/bash
if [ "${GH_TOKEN}" == "" ]; then
  echo "Make sure the environment variable export GH_TOKEN is set"
  exit 1
fi

if [ -d hive-cluster-testing ]; then
  cd hive-cluster-testing
  git checkout master
  git pull
  cd ..
else
  git clone https://${GH_TOKEN}@github.com/open-cluster-management/hive-cluster-testing > /dev/null 2>&1
fi
chmod 755 hive-cluster-testing/scripts/*.sh

