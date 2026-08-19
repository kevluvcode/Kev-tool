"""Subnet Calculator - CIDR calculations."""

import ipaddress


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🧮', 'SUBNET CALCULATOR')
    kevbin.cprint(kevbin.t.secondary, "  Enter an IP/CIDR (e.g., 192.168.1.0/24) or IP with netmask.")
    kevbin.line()

    inp = kevbin.input_choice("  Network: ").strip()
    if not inp:
        return

    try:
        if '/' not in inp:
            ip_part, mask = inp.split('/') if '/' in inp else (inp, None)
            if mask is None:
                mask = kevbin.input_choice("  Netmask (e.g., 255.255.255.0 or /24): ").strip()
            if mask.startswith('/'):
                network = ipaddress.ip_network(f'{ip_part}/{mask}', strict=False)
            else:
                network = ipaddress.ip_network(f'{ip_part}/{mask}', strict=False)
        else:
            network = ipaddress.ip_network(inp, strict=False)

        kevbin.cprint(kevbin.t.highlight, f"\n  +--------------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Property                 | Value                            |")
        kevbin.cprint(kevbin.t.highlight, f"  +--------------------------+----------------------------------+")
        fields = [
            ('Network', str(network.network_address)),
            ('Netmask', str(network.netmask)),
            ('CIDR', f'/{network.prefixlen}'),
            ('Broadcast', str(network.broadcast_address)),
            ('First Host', str(list(network.hosts())[0]) if network.num_addresses > 2 else 'N/A'),
            ('Last Host', str(list(network.hosts())[-1]) if network.num_addresses > 2 else 'N/A'),
            ('Total Hosts', str(network.num_addresses)),
            ('Usable Hosts', str(max(0, network.num_addresses - 2))),
            ('Wildcard', str(ipaddress.IPv4Address(int(network.netmask) ^ 0xFFFFFFFF)) if network.version == 4 else 'N/A'),
            ('Version', f'IPv{network.version}'),
        ]
        for k, v in fields:
            kevbin.cprint(kevbin.t.secondary, f"  | {k:<24} | {v:<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +--------------------------+----------------------------------+")

        if network.version == 4 and network.prefixlen <= 28:
            kevbin.cprint(kevbin.t.accent, "\n  Usable Range:")
            hosts = list(network.hosts())
            if hosts:
                kevbin.cprint(kevbin.t.dim, f"    {hosts[0]}  -  {hosts[-1]}")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()
