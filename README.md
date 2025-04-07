# Homelab Kubernetes Infrastructure

This repository contains the GitOps configuration for a Kubernetes-based homelab infrastructure. It uses ArgoCD for continuous deployment and follows modern DevOps practices.

## Repository Structure

```
.
├── app-of-apps/           # ArgoCD Application of Applications pattern
│   ├── apps/             # Application definitions
│   ├── environments/     # Environment-specific configurations
│   │   ├── nonprod/     # Development/Testing environment
│   │   └── prod/        # Production environment
│   └── infra/           # Infrastructure component definitions
├── apps/                 # Individual application configurations
│   ├── hello-world/     # Test application
│   ├── home-assistant/  # Home automation platform
│   └── unifi/           # Ubiquiti UniFi controller
├── clusters/            # Cluster-specific configurations
│   └── talos/          # Talos Linux configurations
└── infra/              # Infrastructure components
    ├── argocd/         # GitOps operator
    ├── cert-manager/   # SSL/TLS certificate management
    ├── kube-prometheus-stack/  # Monitoring and alerting
    ├── sealed-secrets/ # Encrypted secrets management
    └── tailscale/      # VPN solution
```

## Infrastructure Components

### Core Infrastructure
- **ArgoCD**: GitOps operator that manages all deployments
- **Cert-Manager**: Handles SSL/TLS certificates automatically
- **Kube-Prometheus-Stack**: Provides monitoring, alerting, and visualization
- **Sealed-Secrets**: Encrypts Kubernetes secrets for secure storage
- **Tailscale**: Provides secure VPN access to the cluster

### Applications
- **Home Assistant**: Home automation platform
- **UniFi**: Network management for Ubiquiti devices
- **Hello World**: Test application for deployment validation

## Getting Started

### Prerequisites
- Kubernetes cluster (running on Talos Linux)
- `kubectl` configured to access your cluster
- ArgoCD CLI installed

### Initial Setup
1. Create the ArgoCD namespace:
   ```bash
   kubectl create namespace argocd
   ```

2. Apply the ArgoCD configuration:
   ```bash
   kubectl apply --wait=true -n argocd -k infra/argocd/overlays/nonprod
   ```

3. Get the ArgoCD admin password:
   ```bash
   kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
   ```

4. Login to ArgoCD:
   ```bash
   argocd login <argocd-url>
   ```

5. Add the repository to ArgoCD:
   ```bash
   argocd repocreds add ssh://git@github.com/ \
     --ssh-private-key-path <SSH_PRIVATE_KEY_PATH>
   ```

6. Create the app-of-apps application:
   ```bash
   argocd app create app-of-apps \
     --dest-namespace argocd \
     --dest-server https://kubernetes.default.svc \
     --repo git@github.com:pmpaulino/homelab-argo-apps.git \
     --path environments/nonprod
   ```

7. Sync the application:
   ```bash
   argocd app sync app-of-apps
   ```

## Environment Management

The repository supports multiple environments:
- **nonprod**: Development and testing environment
- **prod**: Production environment

Each environment can have its own configuration overlays while maintaining a common base configuration.

## Security

- Secrets are encrypted using Sealed-Secrets
- SSL/TLS certificates are automatically managed by Cert-Manager
- Remote access is secured through Tailscale VPN
- Talos Linux provides a security-focused Kubernetes operating system

## Monitoring

The infrastructure includes comprehensive monitoring through:
- Prometheus for metrics collection
- Grafana for visualization
- AlertManager for notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

```bash
helmfile template . | \
  yq eval '. | select(.kind != "CustomResourceDefinition")' -P | \
  yq -s '"helm/" + (.kind | downcase) + "_" + .metadata.name + ".yaml"'

[ -f '.yml' ] && rm '.yml'

cd helm && \
  kustomize create --autodetect && \
  cd ..
```

```bash
helmfile template . --include-crds | \
  yq eval '. | select(.kind == "CustomResourceDefinition")' -P | \
  yq -s '"crds/" + (.metadata.name | sub("\.", "_")) + ".yaml"'

[ -f '.yml' ] && rm '.yml'

cd crds && \
  kustomize create --autodetect && \
  cd ..
```
