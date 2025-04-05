# Talos Kubernetes Setup Commands

This is a collection of commands used to setup a Talos-based Kubernetes cluster.

## Important Notes

- Replace `192.168.2.3` with your actual node IP address
- The `--insecure` flag is only needed during initial setup before certificates are established
- Keep the `talosconfig` file secure - it contains cluster access credentials
- Commands use the pattern `-n` for node and `-e` for endpoint, which is more concise than the `--nodes` format
- All commands assume you're in the directory containing your configuration files `controlplane.yaml`, `talosconfig`
- Replace all placeholder values (marked with `<...>`) with your actual values
- Ensure you have created the OAuth client in Tailscale admin console before installation
- Keep your `talosconfig` and `kubeconfig` files secure
- Apply Tailscale ingress configurations after deployments are complete
- Consider storing sensitive values in secrets or a vault instead of manifest files

## Generate Talos Configuration

Replace the IP address with your control plane node's IP

```shell
talosctl gen config gamer https://192.168.2.3:6443
```

### Check Available Disks

Used to identify the disk device for installation

```shell
talosctl get disks --nodes 192.168.2.3 --insecure
```

### Change Disk Configuration

Edit the controlplane.yaml file to include the correct disk information.

## Apply Config & Bootstrap Cluster

After modifying controlplane.yaml with correct disk information

```shell
talosctl apply-config --nodes 192.168.2.3 --insecure --file controlplane.yaml
```

### Bootstrap the Cluster

-n specifies the node, -e specifies the endpoint

```shell
talosctl bootstrap -n 192.168.2.3 -e 192.168.2.3 --talosconfig ./talosconfig
```

## Check Cluster Health

- Use the dashboard command to monitor cluster health and resource usage
- The services command can help verify that all required services are running

### Access Talos Dashboard

Provides real-time cluster metrics and information

```shell
talosctl dashboard -n 192.168.2.3 -e 192.168.2.3 --talosconfig ./talosconfig
```

### View Talos Services

```shell
talosctl -n 192.168.2.3 -e 192.168.2.3 --talosconfig ./talosconfig services
```

## Get Kubernetes Configuration

Generates the kubeconfig file for kubectl access

```shell
talosctl -n 192.168.2.3 -e 192.168.2.3 --talosconfig ./talosconfig kubeconfig ./kubeconfig
```

## Local Path Provisioner

- Change into the local-path-provisioner directory with `cd local-path-provisioner`
- Apply the configuration with `kustomize build | kubectl apply -f -`
- If you need to check storage provisioning, you can list directories with:

    ```shell
    talosctl -n 192.168.2.3 -e 192.168.2.3 --talosconfig ./talosconfig ls /var/local-path-provisioner
    ```
