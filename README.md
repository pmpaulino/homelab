# Overview

This repository contains the ArgoCD applications for my homelab.

```shell
# There is a better way to share this credential via a credential template
argocd repo add git@github.com:pmpaulino/homelab-argo-apps.git \
  --ssh-private-key-path <SSH_PRIVATE_KEY_PATH>

argocd app create app-of-apps \
    --dest-namespace argocd \
    --dest-server https://kubernetes.default.svc \
    --repo git@github.com:pmpaulino/homelab-argo-apps.git \
    --path environments/nonprod 
argocd app sync app-of-apps
```
