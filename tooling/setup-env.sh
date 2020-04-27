#!/bin/bash
echo "Configure global user information:"

git config --global user.email "jpacker@redhat.com"
git config --global user.name "BOT-RHACM Hive Open Shift releases"

python3 -m pip install requests