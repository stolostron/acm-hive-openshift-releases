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
	@echo Client Version should be at least 4.4
	@oc version | grep "Client Version"

update-images: setup-env
	python3 tooling/create-ocp-clusterimagesets.py
	python3 tooling/promote-stable-clusterimagesets.py
	make prune-images
	#./tooling/gitrepo-commitpush-hive-test.sh

prune-images:
	@echo === Start ClusterImageSet pruning ===
	python3 tooling/prune.py 1 clusterImageSets/fast
	@echo
	python3 tooling/prune.py 2 clusterImageSets/stable
	@echo === Finished Pruning ===

setup-env:
	tooling/setup-env.sh

commit-push:
	tooling/commit-push.sh

sync-images-job: update-images commit-push
	echo "DONE!"

subscribe-stable: subscribe-fast
	oc apply -f subscribe/subscription-stable.yaml
	oc delete -f subscribe/subscription-fast.yaml --ignore-not-found
	oc delete -f subscribe/subscription-candidate.yaml --ignore-not-found

subscribe-fast: verify-oc-cli delete-clusterimagesets
	oc apply -k subscribe

subscribe-candidate: subscribe-fast
	oc apply -f subscribe/subscription-candidate.yaml
	oc delete -f subscribe/subscription-fast.yaml --ignore-not-found
	oc delete -f subscribe/subscription-stable.yaml --ignore-not-found

unsubscribe-all: verify-oc-cli
	oc delete -f subscribe/subscription-stable.yaml --ignore-not-found
	oc delete -f subscribe/subscription-candidate.yaml --ignore-not-found
	oc delete -k subscribe/ || true

pause-fast:
	oc -n hive patch appsub hive-clusterimagesets-subscription-fast-0 --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"true"}]'

unpause-fast:
	oc -n hive patch appsub hive-clusterimagesets-subscription-fast-0 --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"false"}]'

pause-stable:
	oc -n hive patch appsub hive-clusterimagesets-subscription-stable-0 --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"true"}]'

unpause-stable:
	oc -n hive patch appsub hive-clusterimagesets-subscription-stable-0 --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"false"}]'

delete-clusterimagesets:
	oc delete clusterimagesets --all