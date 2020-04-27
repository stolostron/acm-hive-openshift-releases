update-images:
	python3 tooling/create-ocp-clusterimagesets.py

setup-env:
	tooling/setup-env.sh

commit-push:
	tooling/commit-push.sh

sync-images-job: setup-env update-images commit-push
	echo "DONE!"

promote-stable-job:
	echo 'TBD"

all:
	echo "Run travis-job-sync-images or travis-job-promote-stable"