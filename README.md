# Sealed Secrets

## References

- <https://github.com/bitnami-labs/sealed-secrets/tree/main?tab=readme-ov-file#usage>
- <https://github.com/bitnami-labs/sealed-secrets/blob/main/docs/bring-your-own-certificates.md#bring-your-own-certificates>

## Generate TLS certificate steps from scratch

```shell
export PRIVATEKEY="homelab-seal-priv.key"
export PUBLICKEY="homelab-seal-pub.crt"
export NAMESPACE="sealed-secrets" # TODO: change to sealed-secrets
export SECRETNAME="homelab-seal"
```

- `openssl req -x509 -days 365 -nodes -newkey rsa:4096 -keyout "$PRIVATEKEY" -out "$PUBLICKEY" -subj "/CN=sealed-secret/O=sealed-secret"`
- `k -n "$NAMESPACE" create secret tls "$SECRETNAME" --cert="$PUBLICKEY" --key="$PRIVATEKEY"`
- `k -n "$NAMESPACE" label secret "$SECRETNAME" sealedsecrets.bitnami.com/sealed-secrets-key=active`
- `k -n  "$NAMESPACE" delete pod -l name=sealed-secrets-controller`

### Seal a secret from scratch

- `echo -n bar | k create secret generic mysecret --dry-run=client --from-file=foo=/dev/stdin >mysecret.yaml`
- `kubeseal --cert "./${PUBLICKEY}" -f mysecret.yaml -w mysealedsecret.yaml`
- `k apply -f mysealedsecret.yaml`
- `k get secret mysecret -o yaml`
- `echo "YmFy" | base64 -d` # bar

## Steps from existing certs

```shell
export PRIVATEKEY="homelab-seal-priv.key"
export PUBLICKEY="homelab-seal-pub.crt"
export NAMESPACE="sealed-secrets" # TODO: change to sealed-secrets
export SECRETNAME="homelab-seal"
```

### Seal a secret from existing certs

- `op document get homelab-seal-pub.crt`
- `op document get homelab-seal-priv.key`
- `k -n "$NAMESPACE" create secret tls "$SECRETNAME" --cert="/tmp/pub.crt" --key="/tmp/priv.key"`
- `k -n "$NAMESPACE" label secret "$SECRETNAME" sealedsecrets.bitnami.com/sealed-secrets-key=active`
- `k -n "$NAMESPACE" delete pod -l name=sealed-secrets-controller`

## Notes

- I guess I'll store the certs in 1password
- Need to do this for tailscale secret `kubeseal --cert "./${PUBLICKEY}" --scope cluster-wide < mysecret.yaml`
