# tailscale

## Generate k8s manifests from helmfile

### Generate base manifests

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

### Generate CRDs

```bash
rm -f crds/*

helmfile template . | \
  yq eval '. | select(.kind == "CustomResourceDefinition")' -P | \
  yq -s '"crds/" + (.metadata.name | sub("\.", "_")) + ".yaml"'

[ -f '.yml' ] && rm '.yml'

cd crds && \
  kustomize create --autodetect && \
  cd ..
```

## Install

### Startup k8s cluster with limactl

- `limactl create --name=k8s template://k8s`
- `limactl start k8s`
- `export KUBECONFIG="/Users/<user name>/.lima/k8s/copied-from-guest/kubeconfig.yaml"`

### Prepare tailscale for k8s operator

- Create a new OAuth client on the tailscale admin console.
- This will allow ingresses within your tailnet and to the internet via funnel.

```json
    "tagOwners": {
        "tag:k8s-operator": [],
        "tag:k8s":          ["tag:k8s-operator"],
    },
    "nodeAttrs": [
        {
            "target": ["autogroup:member", "tag:k8s"],
            "attr":   ["funnel"],
        },
    ],
```

### Install tailscale-operator

I also included the manifest of the version I used in this repo. You can use that instead of the helm repo if preferred.

- `helm repo add tailscale https://pkgs.tailscale.com/helmcharts`
- `helm repo update`
- Then run the upgrade command with your OAuth client ID and secret.

```bash
helm upgrade \
  --install \
  tailscale-operator \
  tailscale/tailscale-operator \
  --namespace=tailscale \
  --create-namespace \
  --set-string oauth.clientId=<OAauth client ID> \
  --set-string oauth.clientSecret=<OAuth client secret> \
  --set-string apiServerProxyConfig.mode="noauth" \ # this will expose the kube-apiserver to the tailnet
  --wait
```

### Install sample app

- `kubectl apply -f sample-app.yaml`
- I had issues having the ingress in the same file as the deployment. I had to apply the deployment first then the ingress. Which helps since you may want to expose the ingress to the internet. This might be a side effect of the limactl setup, not sure.
- Chose between just exposing ingress in tailnet or to the internet with funnel
  - `kubectl apply -f sample-app-ingress.yaml`
  - `kubectl apply -f sample-app-ingress-funnel.yaml`

### Get hostname from ingress

- `kubectl get ingress -n tailscale`

## Uninstall

- `kubectl delete -f sample-app-ingress.yaml`
- `kubectl delete -f sample-app.yaml`
- `helm uninstall tailscale-operator -n tailscale`

## References

- [Tailscale Operator Manifests](https://github.com/tailscale/tailscale/blob/main/cmd/k8s-operator/deploy/manifests/operator.yaml)
- [Tailscale Operator Documentation](https://tailscale.com/kb/1236/kubernetes-operator)

## Notes

- Had to apply the ingress well after the deployment of the app otherwise the tailscale ingress wouldn't work as expected.
- helm install of operator failed on first try. Had to run it again.

## TODO

- Don't store secrets in manifest files. Use secrets or vault.
  - kubectl create secret generic my-secret --from-literal=username=admin --from-literal=password=1f2d1e2e67df

```yaml
    spec:
      containers:
      - name: my-container
        image: my-image
        env:
        - name: USERNAME
          valueFrom:
            secretKeyRef:
              name: my-secret
              key: username
        - name: PASSWORD
          valueFrom:
            secretKeyRef:
              name: my-secret
              key: password
```
