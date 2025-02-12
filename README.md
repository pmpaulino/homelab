# argocd

## Install Argo CD

```shell
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

## Get argocd password

```shell
kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d | pbcopy
```

## Login to Argo CD

```shell
argocd login argocd.example.com
```

## Notes

Manual steps:

- Reset talos cluster by rebooting machine and entering maintenance mode
- Apply talos config
- Bootstrap talos cluster
- Clean up stale tailscale machine entries
- Bootstrap ArgoCD
- Port forward ArgoCD
- Login to ArgoCD CLI
- Setup repo credentials for argocd
- Install ArgoCD app of apps

Automate:

- Patch kube-prometheus-stack ns so it can complete
- Create secret for tailscale operator
- Patch argocd configmap to allow insecure connections
- Reboot argocd to pick up configmap changes
- Install argocd tailscale ingress
- Depends on keeps things out of sync
- sealed secrets to manage secrets
