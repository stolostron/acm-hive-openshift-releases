update-images: setup-env
	python3 tooling/create-ocp-clusterimagesets.py
	python3 tooling/promote-stable-clusterimagesets.py

setup-env:
	tooling/setup-env.sh

commit-push:
	tooling/commit-push.sh

sync-images-job: setup-env update-images commit-push
	echo "DONE!"

promote-stable-job:
	echo "TBD"

all:
	echo "Run travis-job-sync-images or travis-job-promote-stable"