#!/bin/bash
cur_dir=$(dirname $(readlink -f $0))

rm -rf $cur_dir/../clusterImageSets/fast/*
rm -rf $cur_dir/../clusterImageSets/stable/*
rm -rf $cur_dir/../clusterImageSets/releases/*

git checkout main

