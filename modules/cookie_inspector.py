import requests

def parse_set_cookie(header_value):
    parts = header_value.split(';')
    name_value = parts[0].strip()
    if '=' in name_value:
        name, value = name_value.split('=', 1)
    else:
        name, value = name_value, ''
    attrs = {}
    for part in parts[1:]:
        part = part.strip()
        if '=' in part:
            k, v = part.split('=', 1)
            attrs[k.lower()] = v
        else:
            attrs[part.lower()] = True
    return {"name": name, "value": value, "attrs": attrs}

def run(kevbin):
    kevbin.box.title("Cookie Inspector")
    url = kevbin.box.input("URL to inspect: ")
    if not url:
        return
    
    follow_redirects = kevbin.box.confirm("Follow redirects?", default=True)
    verify_ssl = kevbin.box.confirm("Verify SSL?", default=True)
    
    try:
        resp = requests.get(url, allow_redirects=follow_redirects, verify=verify_ssl, timeout=30)
    except Exception as e:
        kevbin.box.error(f"Request failed: {e}")
        return
    
    cookies = []
    for header_name, header_value in resp.headers.items():
        if header_name.lower() == "set-cookie":
            for cookie_str in header_value.split(', '):
                if '=' in cookie_str:
                    parsed = parse_set_cookie(cookie_str)
                    cookies.append(parsed)
    
    if not cookies:
        kevbin.box.info("No Set-Cookie headers found")
        return
    
    rows = []
    for c in cookies:
        attrs = []
        for k, v in c["attrs"].items():
            if v is True:
                attrs.append(k)
            else:
                attrs.append(f"{k}={v}")
        rows.append([c["name"], c["value"][:50] + ("..." if len(c["value"]) > 50 else ""), "; ".join(attrs)])
    
    kevbin.box.table(["Name", "Value", "Attributes"], rows)
    
    if resp.cookies:
        kevbin.box.title("Cookie Jar (after redirects)")
        jar_rows = [[c.name, c.value, c.domain, c.path, "Secure" if c.secure else "", "HttpOnly" if c._rest.get("HttpOnly") else ""] for c in resp.cookies]
        kevbin.box.table(["Name", "Value", "Domain", "Path", "Secure", "HttpOnly"], jar_rows)