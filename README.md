# Overview

This repository contains the ArgoCD applications for my homelab.

```shell
argocd repo add git@github.com:pmpaulino/homelab-argo-apps.git \
  --ssh-private-key-path <SSH_PRIVATE_KEY_PATH>

kubectl apply -f argo-app-of-apps.yaml
```
