# Overview

This repository contains the ArgoCD applications for my homelab.

```shell
argocd repocreds add ssh://git@github.com/ \
  --ssh-private-key-path <SSH_PRIVATE_KEY_PATH>

argocd app create app-of-apps \
    --dest-namespace argocd \
    --dest-server https://kubernetes.default.svc \
    --repo git@github.com:pmpaulino/homelab-argo-apps.git \
    --path environments/nonprod 
argocd app sync app-of-apps
```
