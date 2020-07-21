#!/bin/bash

# Copyright 2020 Red Hat Inc.

LOC=$(dirname $0)
CLUSTER_REGION=${CLUSTER_REGION:-us-east-1}
CLUSTER_TYPE=${CLUSTER_TYPE:-AWS}
CLUSTER_IMAGE_SET=${CLUSTER_IMAGE_SET:-img4.4.8-x86-64}
CLUSTER_NAME=${CLUSTER_NAME:-}
OVERWRITE=${OVERWRITE:-}
BASEDOMAIN=${BASEDOMAIN:-}

echo "*"
if [ "${CLUSTER_NAME}" == "" ]; then
    printf "|> Enter a name for your cluster\n|= "
    read -r CLUSTER_NAME
fi
if [ "${BASEDOMAIN}" == "" ]; then
    printf "|> Enter the BASEDOMAIN for your cluster\n|= "
    read -r BASEDOMAIN
fi

NEW_CLUSTER_DIR=$LOC/../deployed/${CLUSTER_NAME}
printf "|\n|  Setting up $NEW_CLUSTER_DIR\n"

if [ -d $NEW_CLUSTER_DIR ]; then
    if [ "${OVERWRITE}"  == "" ]; then
        printf "|> Cluster definition already exists, overwrite? y/n\n|= "
        read -r OVERWRITE
    fi
    if [ "${OVERWRITE}" != "y" ] && [ "${OVERWRITE}" != "Y" ]; then
        echo "|  Cluster definition exists"
        echo "*WARNING"
        exit 1
    fi
    printf "|\n"
    rm -rf $NEW_CLUSTER_DIR
fi

mkdir -p $NEW_CLUSTER_DIR
echo "|  Created directory $NEW_CLUSTER_DIR"
cp $LOC/../${CLUSTER_TYPE}-Template/clusterdeployment.yaml $LOC/../${CLUSTER_TYPE}-Template/namespace.yaml ${NEW_CLUSTER_DIR}
cp $LOC/../${CLUSTER_TYPE}-Template/kustomization.tmp  ${NEW_CLUSTER_DIR}/kustomization.yaml
cp $LOC/../secret-management/subscription.yaml ${NEW_CLUSTER_DIR}
echo "|  Copied appropriate YAMLs"
for i in `ls ${NEW_CLUSTER_DIR}/*.yaml`; do
    sed -i "s|TEMPLATE_NAME|${CLUSTER_NAME}|g" ${i}
    sed -i "s|SECRET_NAME|hive|g" ${i}
    sed -i "s/TEMPLATE_REGION/${CLUSTER_REGION}/g" ${i}
    sed -i "s/TEMPLATE_CLUSTERIMAGESET/${CLUSTER_IMAGE_SET}/g" ${i}
    sed -i "s/BASEDOMAIN/${BASEDOMAIN}/g" ${i}
done
echo "|  Applied Cluster name to all template files"

echo "*Done"



