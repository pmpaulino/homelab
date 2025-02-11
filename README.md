# Cert Manager

```bash
helmfile template . | \
  yq eval '. | select(.kind != "CustomResourceDefinition")' -P | \
  helmYAMLizer -d base --drop-label-keys app.kubernetes.io/managed-by helm.sh/chart
```

```bash
helmfile template . | \
  yq eval '. | select(.kind == "CustomResourceDefinition")' -P | \
  helmYAMLizer -d crds --drop-label-keys app.kubernetes.io/managed-by helm.sh/chart
```
