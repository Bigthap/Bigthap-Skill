---
name: netvpn-bypass
description: Resume and manage the AIS cellular VPN bypass project using AWS Relay to Proxmox LXC. Use when the user mentions NetVPN, AIS throttling, ZIVPN, AWS Relay, Proxmox LXC routing, or wants to resume setting up VLESS-Reality or SSH SOCKS5 tunnels.
---

# NetVPN Bypass Project (AIS Throttling)

Use this skill to continue the project of bypassing AIS mobile internet throttling by routing traffic through AWS EC2 to a Home Server (Proxmox LXC Container).

## Quick Reference & IPs

*   **AWS EC2 (Relay):** Public IP `43.210.246.181` | WireGuard IP `10.9.9.1`
*   **Proxmox Host (Home Router):** LAN IP `192.168.1.60` | WireGuard IP `10.9.9.2`
*   **LXC Container (ZIVPN/Proxy Server):** LAN IP `192.168.1.144` | ZIVPN listens on UDP `5667`
*   **WireGuard Tunnel Subnet:** `10.9.9.0/24` (MTU configured to `1360`)

## Summary of Previous Work (UDP Phase)

1.  **Configuration Built:** Created a UDP port-hopping relay tunnel (ports `6000:19999`).
    *   AWS DNATs to `10.9.9.2` and MASQUERADEs output via `wg0` with `--random-fully`.
    *   Proxmox DNATs wg0 port-hopping traffic to LXC `192.168.1.144`.
    *   LXC redirects `6000:19999` to `5667` and routes `10.9.9.0/24` via Proxmox (`192.168.1.60`).
2.  **Outcome:** The UDP tunnel successfully routes packets with 0% packet loss inside the tunnel, but ZIVPN UDP (Hysteria) remains **unstable on AIS network** due to aggressive UDP QoS/DPI packet drops from the carrier.
3.  **Current Status:** WireGuard and ZIVPN services have been stopped and disabled on all nodes for resource conservation:
    *   AWS/Proxmox: `systemctl stop wg-quick@wg0 && systemctl disable wg-quick@wg0`
    *   LXC Container: `systemctl stop zivpn && systemctl disable zivpn`

## Next Steps (TCP Phase Strategy)

If the user wants to resume, focus on these two TCP-based alternatives to bypass UDP throttling:

### Strategy 1: VLESS-Reality (TCP 443 + XTLS/Vision)
*   **Concept:** Obfuscate traffic to look like normal HTTPS browsing by mimicking a major domain (SNI) like Apple or Microsoft.
*   **Implementation:** Deploy Xray-core on AWS EC2, configure Reality proxy, and route the proxy exit to the local LXC container.

### Strategy 2: SSH SOCKS5 Tunneling (SSH -D)
*   **Concept:** Use a raw SSH tunnel over TCP (Port 22/443) which is highly trusted by ISPs, avoiding the overhead of OpenVPN.
*   **Implementation:** Establish dynamic port forwarding (`ssh -D 1080`) from the client (using NekoBox) to AWS, and route SOCKS5 egress back to LXC.
