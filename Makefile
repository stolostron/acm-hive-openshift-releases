all:
	@echo "Travis commands:"
	@echo "  _> make sync-images-job"
	@echo ""
	@echo "Subscribe commands:"
	@echo "  _> make subscribe-fast"
	@echo "  _> make subscribe-stable"
	@echo "  _> make subscribe-candidate"
	@echo "  _> make unsubscribe-all"
	@echo "Manual commands:"
	@echo "  _> make update-images"

verify-oc-cli:
	oc version | grep " 4.4."

update-images: setup-env
	python3 tooling/create-ocp-clusterimagesets.py
	python3 tooling/promote-stable-clusterimagesets.py
	#./tooling/gitrepo-commitpush-hive-test.sh

setup-env:
	tooling/setup-env.sh

commit-push:
	tooling/commit-push.sh

sync-images-job: update-images commit-push
	echo "DONE!"

subscribe-stable: verify-oc-cli subscribe-fast
	oc apply -f subscription/subscription-stable.yaml
	oc delete -f subscription/subscription-fast.yaml --ignore-not-found
	oc delete -f subscription/subscription-candidate.yaml --ignore-not-found

subscribe-fast: verify-oc-cli
	oc projects | grep ocp-clusterimagesets || oc new-project ocp-clusterimagesets
	oc apply -k subscription

subscribe-candidate: verify-oc-cli subscribe-fast
	oc apply -f subscription/subscription-candidate.yaml
	oc -n hive delete appsub openshift-release-fast-images --ignore-not-found
	oc -n hive delete appsub openshift-release-stable-images --ignore-not-found

unsubscribe-all: verify-oc-cli
	oc delete -f subscription/subscription-stable.yaml --ignore-not-found
	oc delete -f subscription/subscription-candidate.yaml --ignore-not-found
	oc delete -k subscription/ || true

pause-fast:
	oc -n hive patch appsub openshift-release-fast-images --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"true"}]'

unpause-fast:
	oc -n hive patch appsub openshift-release-fast-images --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"false"}]'

pause-stable:
	oc -n hive patch appsub openshift-release-stable-images --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"true"}]'

unpause-stable:
	oc -n hive patch appsub openshift-release-stable-images --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"false"}]'