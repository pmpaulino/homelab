# unifi

```shell
helm template unifi oci://ghcr.io/mkilchhofer/unifi-chart/unifi \
  -f ../helm/values.yaml | \
  helmYAMLizer -k -d k8s \
    --drop-label-keys app.kubernetes.io/managed-by
```
