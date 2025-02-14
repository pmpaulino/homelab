#!/bin/bash
set -euo pipefail

# Configuration variables - modify these as needed
TALOS_NODE="192.168.2.3"

# Make temp directory
echo "Creating temp directory..."
mkdir -p "tmp"

# Get the required secrets from 1Password
echo "Getting secrets from 1Password..."
op read "op://Private/i7sdiseuc47purydotahi7ksfm/private key" -o "tmp/sshprivatekey" --force
op document get "homelab-seal-pub.crt" -o "tmp/tls.crt" --force
op document get "homelab-seal-priv.key" -o "tmp/tls.key" --force
op document get "talos-secrets.yaml" -o "tmp/talos-secrets.yaml" --force

# Build the manifests and patch
echo "Building Talos patch with ArgoCD manifests..."
kustomize build . > "tmp/argocd-manifests.yaml"
{
    echo 'cluster:'
    echo '  inlineManifests:'
    echo '    - name: my-complete-app'
    echo '      contents: |-'
    sed 's/^/        /' "tmp/argocd-manifests.yaml"
} > "tmp/talos-patch-manifests.yaml"

# Generate talos configs with real secrets
echo "Generating talos configs with real secrets..."
talosctl gen config gamer "https://$TALOS_NODE:6443" \
    --with-secrets "tmp/talos-secrets.yaml" \
    --config-patch @"tmp/talos-patch-manifests.yaml" \
    --config-patch @talos-patch.yaml \
    --output "tmp/"

echo "Generating example talos configs with example secrets..."
talosctl gen config gamer "https://$TALOS_NODE:6443" \
    --with-secrets "example/talos-secrets.yaml" \
    --config-patch @talos-patch.yaml \
    --output "example/" \
    --force

# Bootstrap the cluster
echo "Starting cluster bootstrap process..."

# Reset Talos cluster (this requires manual intervention)
echo "Please reboot the machine and enter maintenance mode manually"
echo "Press enter when ready to continue..."
read -r

# Apply Talos configuration
echo "Applying Talos configuration..."
talosctl apply-config -n "$TALOS_NODE" --insecure \
    --file "tmp/talos-patched-controlplane.yaml"

# Bootstrap Talos cluster
echo "Bootstrapping Talos cluster..."
talosctl bootstrap -n "$TALOS_NODE" -e "$TALOS_NODE" \
    --talosconfig "tmp/talosconfig"

# Clean up Tailscale entries (requires tailscale CLI)
echo "Cleaning up stale Tailscale entries..."
echo "Press enter when ready to continue..."
read -r

# Wait for the cluster to be ready
echo "Waiting for cluster to be ready..."
talosctl health -n "$TALOS_NODE" -e "$TALOS_NODE" \
    --talosconfig "tmp/talosconfig"

echo "Bootstrap complete!"

# Get kubeconfig
talosctl kubeconfig "./tmp/kubeconfig" \
    --talosconfig "tmp/talosconfig" \
    -n "$TALOS_NODE" \
    -e "$TALOS_NODE"

# Clean up temp files
echo "You should clean up the temp files now..."
