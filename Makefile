STABLE_KEEP_COUNT ?=2
FAST_KEEP_COUNT ?=1
all:
	@echo "Commands:"
	@echo "  _> make sync-images-job"
	@echo ""
	@echo "Subscribe commands:"
	@echo "  _> make subscribe-fast"
	@echo "  _> make subscribe-stable"
	@echo "  _> make subscribe-candidate"
	@echo "  _> make unsubscribe-all"
	@echo "Manual commands:"
	@echo "  _> make update-images"
	@echo ""
	@echo "Branch management:"
	@echo "  _> make suggest-branch    # Show recent branches and suggest next"
	@echo "  _> make add-branch        # Interactive: add a new branch"
	@echo ""
	@echo "Validation:"
	@echo "  _> make validate-images          # Validate YAML structure and format"
	@echo "  _> make validate-images-registry # Validate + check images exist in registry"

verify-oc-cli:
	@echo Client Version should be at least 4.4
	@oc version | grep "Client Version"

cleanup-images:
	tooling/cleanup-clusterimagesets.sh

update-images: setup-env
	python3 tooling/create-ocp-clusterimagesets.py
	python3 tooling/promote-stable-clusterimagesets.py
	make visible-images
	make prune-images

visible-images:
	@echo === Start ClusterImageSet mark visability ===
	python3 tooling/keep-visible.py ${FAST_KEEP_COUNT} clusterImageSets/fast
	@echo
	python3 tooling/keep-visible.py ${STABLE_KEEP_COUNT} clusterImageSets/stable
	@echo === Finished visability ===	

prune-images:
	@echo === Start ClusterImageSet pruning ===
	python3 tooling/prune.py ${FAST_KEEP_COUNT} clusterImageSets/fast
	@echo
	python3 tooling/prune.py ${STABLE_KEEP_COUNT} clusterImageSets/stable
	@echo === Finished Pruning ===

setup-env:
	tooling/setup-env.sh


sync-images-job: cleanup-images update-images
	echo "DONE!"

subscribe-stable: subscribe-fast
	oc -n hive-clusterimagesets apply -f subscribe/subscription-stable.yaml
	oc -n hive-clusterimagesets delete -f subscribe/subscription-fast.yaml --ignore-not-found
	oc -n hive-clusterimagesets delete -f subscribe/subscription-candidate.yaml --ignore-not-found

subscribe-fast: verify-oc-cli delete-clusterimagesets
	oc -n hive-clusterimagesets apply -k subscribe

subscribe-candidate: subscribe-fast
	oc -n hive-clusterimagesets apply -f subscribe/subscription-candidate.yaml
	oc -n hive-clusterimagesets delete -f subscribe/subscription-fast.yaml --ignore-not-found
	oc -n hive-clusterimagesets delete -f subscribe/subscription-stable.yaml --ignore-not-found

unsubscribe-all: verify-oc-cli
	oc -n hive-clusterimagesets delete -f subscribe/subscription-stable.yaml --ignore-not-found
	oc -n hive-clusterimagesets delete -f subscribe/subscription-candidate.yaml --ignore-not-found
	oc -n hive-clusterimagesets delete -k subscribe/ || true

pause-fast:
	oc -n hive-clusterimagesets patch appsub hive-clusterimagesets-subscription-fast --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"true"}]'

unpause-fast:
	oc -n hive-clusterimagesets patch appsub hive-clusterimagesets-subscription-fast --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"false"}]'

pause-stable:
	oc -n hive-clusterimagesets patch appsub hive-clusterimagesets-subscription-stable --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"true"}]'

unpause-stable:
	oc -n hive-clusterimagesets patch appsub hive-clusterimagesets-subscription-stable --type='json' -p='[{"op":"replace","path": "/metadata/labels/subscription-pause","value":"false"}]'

delete-clusterimagesets:
	oc -n hive-clusterimagesets delete clusterimagesets --all

suggest-branch:
	python3 tooling/add-branch.py

add-branch:
	python3 tooling/add-branch.py --interactive

validate-images:
	@echo === Validating ClusterImageSet YAML files ===
	python3 tooling/validate-imagesets.py

validate-images-registry:
	@echo === Validating ClusterImageSet YAML files with registry checks ===
	python3 tooling/validate-imagesets.py --check-registry
