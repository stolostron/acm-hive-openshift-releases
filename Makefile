STABLE_KEEP_COUNT ?=2
FAST_KEEP_COUNT ?=1
all:
	@echo "Subscribe commands:"
	@echo "  _> make subscribe-fast"
	@echo "  _> make subscribe-stable"
	@echo "  _> make subscribe-candidate"
	@echo "  _> make unsubscribe-all"

verify-oc-cli:
	@echo Client Version should be at least 4.4
	@oc version | grep "Client Version"

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