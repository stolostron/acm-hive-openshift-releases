#!/bin/bash
echo "Configure global user information:"

if [ "$TRAVIS" == "true" ]; then
    git config --global user.email "$BOT_EMAIL"
    git config --global user.name "BOT-RHACM Hive Open Shift releases"
fi

python3 -m pip install requests
python3 -m pip install pyyaml
#tooling/gitrepo-clone-hive-test.sh