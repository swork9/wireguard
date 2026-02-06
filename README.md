# WireGuard Config Generator

A Python script to manage WireGuard configurations using a single YAML file. It handles key generation, IP validation, and produces both server and client configurations.

## Features

- **Automatic Key Generation**: Generates `private_key`, `public_key`, and `preshared_key` automatically if they are missing or empty in the YAML file.
- **Format Preservation**: Uses `ruamel.yaml` to save generated keys back to your YAML while keeping comments and formatting intact.
- **IP Validation**:
    - Ensures no duplicate IPs across server and clients.
    - Verifies all IPs belong to the defined `allowed_ips` network.
- **Simplified Configuration**: Centralizes server settings and client lists in one place.

## Prerequisites

1.  **Python 3.x**
2.  **WireGuard Tools**: The `wg` command must be available in your PATH for key generation.
3.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration (YAML)

Create a YAML file (e.g., `wg0.yml`) based on the following structure:

```yaml
server:
  address: 10.0.0.1/24
  listen_port: 51820
  endpoint: 1.2.3.4       # Public IP or Domain
  post_up: "iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE"
  post_down: "iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE"

common:
  persistent_keepalive: 25
  allowed_ips: 10.0.0.0/24

clients:
  - name: alice
    address: 10.0.0.2/24
  - name: bob
    address: 10.0.0.3/24
```

*Note: Keys will be automatically added to this file upon first run.*

## Usage

### 1. Generate Server Configuration
```bash
python3 wireguard.py wg0.yml server > /etc/wireguard/wg0.conf
```

### 2. Generate Client Configuration
```bash
python3 wireguard.py wg0.yml alice > alice.conf
```

## Post-Setup & Management

### Start/Stop Interface
```bash
wg-quick up wg0
wg-quick down wg0
```

### Enable on Boot
```bash
systemctl enable wg-quick@wg0
```

### Check Status
```bash
wg show
```

## Security Recommendations

- **File Permissions**: Keep your YAML and generated `.conf` files secure.
  ```bash
  chmod 600 wg0.yml /etc/wireguard/wg0.conf
  ```
- **Preshared Keys**: This script generates PresharedKeys by default for each client to provide post-quantum resistance.
- **Firewall**: Ensure the `ListenPort` (UDP) is open on your server's firewall.
