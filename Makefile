verify-oc-cli:
	oc version | grep " 4.4."

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

subscribe-stable: verify-oc-cli
	oc apply -k subscription/

subscribe-fast: verify-oc-cli subscribe-stable
	oc apply -f subscription/subscription-fast.yaml

subscribe-candidate: verify-oc-cli subscribe-stable
	oc apply -f subscription/subscription-candidate.yaml

unsubscribe: verify-oc-cli
	oc delete -f subscription/subscription-fast.yaml --ignore-not-found
	oc delete -k subscription/ || true