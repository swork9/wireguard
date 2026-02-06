#!/usr/bin/env python3
import sys
from ruamel.yaml import YAML
import ipaddress
import subprocess

def run_wg(cmd, input_str=None):
    return subprocess.check_output(['wg', cmd], input=input_str.encode() if input_str else None).decode().strip()

def main():
    if len(sys.argv) < 3:
        sys.exit(1)

    yaml = YAML()
    yaml.preserve_quotes = True
    with open(sys.argv[1]) as f:
        cfg = yaml.load(f)

    srv = cfg['server']
    com = cfg['common']
    cls = cfg['clients']

    changed = False
    if not srv.get('private_key'):
        srv['private_key'] = run_wg('genkey')
        changed = True
    if not srv.get('public_key'):
        srv['public_key'] = run_wg('pubkey', srv['private_key'])
        changed = True

    for c in cls:
        if not c.get('private_key'):
            c['private_key'] = run_wg('genkey')
            changed = True
        if not c.get('public_key'):
            c['public_key'] = run_wg('pubkey', c['private_key'])
            changed = True
        if not c.get('preshared_key'):
            c['preshared_key'] = run_wg('genpsk')
            changed = True

    if changed:
        with open(sys.argv[1], 'w') as f:
            yaml.dump(cfg, f)

    net = ipaddress.ip_network(com['allowed_ips'], strict=False)
    ips = {ipaddress.ip_interface(srv['address']).ip: 'server'}
    for c in cls:
        addr = ipaddress.ip_interface(c['address']).ip
        if addr in ips: sys.exit(f"Error: Duplicate IP {addr} ({ips[addr]} & {c['name']})")
        if addr not in net: sys.exit(f"Error: IP {addr} ({c['name']}) outside {net}")
        ips[addr] = c['name']
    if ipaddress.ip_interface(srv['address']).ip not in net: sys.exit(f"Error: Server IP outside {net}")

    cmd = sys.argv[2]

    if cmd == 'server':
        print("[Interface]")
        print(f"Address = {srv['address']}")
        print(f"ListenPort = {srv['listen_port']}")
        print(f"PrivateKey = {srv['private_key']}")
        if 'post_up' in srv: print(f"PostUp = {srv['post_up']}")
        if 'post_down' in srv: print(f"PostDown = {srv['post_down']}")
        for c in cls:
            print(f"\n# {c['name']}")
            print("[Peer]")
            print(f"PublicKey = {c['public_key']}")
            print(f"PresharedKey = {c['preshared_key']}")
            print(f"AllowedIPs = {c['address'].split('/')[0]}/32")
    else:
        c = next((x for x in cls if x['name'] == cmd), None)
        if c:
            print("[Interface]")
            print(f"Address = {c['address']}")
            print(f"PrivateKey = {c['private_key']}")
            print("\n[Peer]")
            print(f"PublicKey = {srv['public_key']}")
            print(f"PresharedKey = {c['preshared_key']}")
            print(f"Endpoint = {srv['endpoint']}:{srv['listen_port']}")
            print(f"AllowedIPs = {com['allowed_ips']}")
            print(f"PersistentKeepalive = {com['persistent_keepalive']}")
        else:
            sys.exit(f"Error: Client {cmd} not found")

if __name__ == "__main__":
    main()
