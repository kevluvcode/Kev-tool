"""UUID Generator — v1/v3/v4/v5 + batch generate + format options."""

import uuid
import hashlib
import time
import datetime


def run(kevbin):
    while True:
        kevbin.clear()
        kevbin.section_header('🎲', 'UUID GENERATOR')
        kevbin.cprint(kevbin.t.secondary, "  [1]  UUID v4 (random)")
        kevbin.cprint(kevbin.t.secondary, "  [2]  UUID v1 (timestamp)")
        kevbin.cprint(kevbin.t.secondary, "  [3]  UUID v3 (MD5 name-based)")
        kevbin.cprint(kevbin.t.secondary, "  [4]  UUID v5 (SHA1 name-based)")
        kevbin.cprint(kevbin.t.secondary, "  [5]  Batch generate")
        kevbin.cprint(kevbin.t.secondary, "  [6]  Parse/decode UUID")
        kevbin.cprint(kevbin.t.secondary, "  [0]  Back")
        kevbin.line()
        choice = kevbin.input_choice()
        if choice == '0':
            return

        if choice == '1':
            format_choice = kevbin.input_choice("  Format (standard/short/urn/bytes) [standard]: ").strip().lower() or "standard"
            u = uuid.uuid4()
            result = _format_uuid(u, format_choice)
            kevbin.cprint(kevbin.t.accent, f"\n  {result}")
            _show_uuid_info(kevbin, u)
            kevbin.pause()

        elif choice == '2':
            u = uuid.uuid1()
            result = str(u)
            kevbin.cprint(kevbin.t.accent, f"\n  {result}")
            _show_uuid_info(kevbin, u)
            ms = u.time - 0x01b21dd213814000
            ts = datetime.datetime.utcfromtimestamp(ms / 1e7).strftime('%Y-%m-%d %H:%M:%S.%f')
            kevbin.cprint(kevbin.t.txt, f"  Timestamp: {ts} UTC")
            kevbin.cprint(kevbin.t.txt, f"  Node: {u.node}")
            kevbin.pause()

        elif choice == '3':
            ns = kevbin.input_choice("  Namespace (dns/url/oid/x500) [dns]: ").strip().lower() or 'dns'
            name = kevbin.input_choice("  Name: ").strip()
            if not name:
                continue
            ns_map = {'dns': uuid.NAMESPACE_DNS, 'url': uuid.NAMESPACE_URL,
                      'oid': uuid.NAMESPACE_OID, 'x500': uuid.NAMESPACE_X500}
            namespace = ns_map.get(ns, uuid.NAMESPACE_DNS)
            u = uuid.uuid3(namespace, name)
            kevbin.cprint(kevbin.t.accent, f"\n  {u}")
            _show_uuid_info(kevbin, u)
            kevbin.pause()

        elif choice == '4':
            ns = kevbin.input_choice("  Namespace (dns/url/oid/x500) [dns]: ").strip().lower() or 'dns'
            name = kevbin.input_choice("  Name: ").strip()
            if not name:
                continue
            ns_map = {'dns': uuid.NAMESPACE_DNS, 'url': uuid.NAMESPACE_URL,
                      'oid': uuid.NAMESPACE_OID, 'x500': uuid.NAMESPACE_X500}
            namespace = ns_map.get(ns, uuid.NAMESPACE_DNS)
            u = uuid.uuid5(namespace, name)
            kevbin.cprint(kevbin.t.accent, f"\n  {u}")
            _show_uuid_info(kevbin, u)
            kevbin.pause()

        elif choice == '5':
            count = kevbin.input_choice("  How many [10]: ").strip() or '10'
            try:
                count = max(1, min(1000, int(count)))
            except ValueError:
                count = 10
            version = kevbin.input_choice("  Version (4/1) [4]: ").strip() or '4'
            fmt = kevbin.input_choice("  Format (standard/short/urn) [standard]: ").strip().lower() or 'standard'
            uuids = []
            for _ in range(count):
                if version == '1':
                    u = uuid.uuid1()
                else:
                    u = uuid.uuid4()
                uuids.append(_format_uuid(u, fmt))
            if count <= 30:
                for i, u in enumerate(uuids, 1):
                    kevbin.cprint(kevbin.t.txt, f"  {i:>3}. {u}")
            else:
                kevbin.box_table(headers=["#", "UUID"], rows=[[str(i+1), u] for i, u in enumerate(uuids[:30])], title=f"{count} UUIDs")
                kevbin.cprint(kevbin.t.dim, f"  ... ({count} total)")
            save = kevbin.input_choice("\n  Save to file? (y/n): ").strip().lower()
            if save == 'y':
                path = kevbin.input_choice("  Path [uuids.txt]: ").strip() or 'uuids.txt'
                try:
                    with open(path, 'w') as f:
                        f.write('\n'.join(uuids) + '\n')
                    kevbin.cprint(kevbin.t.success, f"  [+] Saved {count} UUIDs to {path}")
                except Exception as e:
                    kevbin.cprint(kevbin.t.error, f"  [X] {e}")
            kevbin.pause()

        elif choice == '6':
            raw = kevbin.input_choice("  UUID to parse: ").strip()
            if not raw:
                continue
            try:
                u = uuid.UUID(raw)
                kevbin.cprint(kevbin.t.accent, f"\n  UUID:    {u}")
                kevbin.cprint(kevbin.t.accent, f"  Version: {u.version}")
                kevbin.cprint(kevbin.t.accent, f"  Variant: {u.variant}")
                kevbin.cprint(kevbin.t.accent, f"  Hex:     {u.hex}")
                kevbin.cprint(kevbin.t.accent, f"  Fields:")
                kevbin.cprint(kevbin.t.txt, f"    time_low:    {u.time_low}")
                kevbin.cprint(kevbin.t.txt, f"    time_mid:    {u.time_mid}")
                kevbin.cprint(kevbin.t.txt, f"    time_hi:     {u.time_hi_version}")
                kevbin.cprint(kevbin.t.txt, f"    clock_seq:   {u.clock_seq}")
                kevbin.cprint(kevbin.t.txt, f"    node:        {u.node}")
            except ValueError as e:
                kevbin.cprint(kevbin.t.error, f"  [X] Invalid UUID: {e}")
            kevbin.pause()


def _format_uuid(u, fmt='standard'):
    if fmt == 'short':
        return str(u).replace('-', '')
    elif fmt == 'urn':
        return f"urn:uuid:{u}"
    return str(u)


def _show_uuid_info(kevbin, u):
    kevbin.cprint(kevbin.t.txt, f"  Version: {u.version}  Variant: {u.variant}")
    kevbin.cprint(kevbin.t.txt, f"  Hex: {u.hex}")
