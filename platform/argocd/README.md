# argocd

## Install Argo CD

```shell
kubectl create namespace argocd
kubectl apply --wait=true -n argocd -k /Users/patrick/Projects/pmpaulino/homelab/argocd/overlays/nonprod
```

## Get argocd password

```shell
kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d | pbcopy
```

## Login to Argo CD

```shell
argocd login <argocd-url>
```
