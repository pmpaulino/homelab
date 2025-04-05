# Kube Prometheus Stack

## Generate base manifests

```bash
rm -f base/*

helmfile template . | \
  yq eval '. | select(.kind != "CustomResourceDefinition")' -P | \
  yq -s '"base/" + (.kind | downcase) + "_" + .metadata.name + ".yaml"'

[ -f '.yml' ] && rm '.yml'

cd base && \
  kustomize create --autodetect && \
  cd ..
```

## Generate CRDs

```bash
rm -f crds/*

helmfile template . --include-crds | \
  yq eval '. | select(.kind == "CustomResourceDefinition")' -P | \
  yq -s '"crds/" + (.metadata.name | sub("\.", "_")) + ".yaml"'

[ -f '.yml' ] && rm '.yml'

cd crds && \
  kustomize create --autodetect && \
  cd ..
```

## TODO

- [ ] figure out a way to label the ns `kubectl label namespace kube-prometheus-stack pod-security.kubernetes.io/enforce=privileged`
