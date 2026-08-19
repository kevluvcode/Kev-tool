import requests
import json

def run(kevbin):
    kevbin.box.title("HTTP Request Builder")
    
    method = kevbin.box.select("Method", ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
    url = kevbin.box.input("URL: ")
    if not url:
        return
    
    headers = {}
    while True:
        add_header = kevbin.box.confirm("Add header?", default=False)
        if not add_header:
            break
        key = kevbin.box.input("Header name: ")
        if not key:
            continue
        value = kevbin.box.input(f"Value for {key}: ")
        headers[key] = value
    
    body = None
    if method in ["POST", "PUT", "PATCH"]:
        body_type = kevbin.box.select("Body type", ["JSON", "Form Data", "Raw Text", "None"])
        if body_type == "JSON":
            raw = kevbin.box.input("JSON body: ")
            try:
                body = json.loads(raw)
            except:
                kevbin.box.error("Invalid JSON")
                return
        elif body_type == "Form Data":
            body = {}
            while True:
                add_field = kevbin.box.confirm("Add form field?", default=False)
                if not add_field:
                    break
                key = kevbin.box.input("Field name: ")
                if not key:
                    continue
                value = kevbin.box.input(f"Value for {key}: ")
                body[key] = value
        elif body_type == "Raw Text":
            body = kevbin.box.input("Raw body: ")
    
    verify_ssl = kevbin.box.confirm("Verify SSL?", default=True)
    timeout = kevbin.box.input("Timeout (seconds, default 30): ", default="30")
    try:
        timeout = int(timeout)
    except:
        timeout = 30
    
    kevbin.box.info(f"Sending {method} {url}...")
    
    try:
        resp = requests.request(method, url, headers=headers, json=body if isinstance(body, dict) and body_type == "JSON" else None, data=body if body_type in ["Form Data", "Raw Text"] else None, verify=verify_ssl, timeout=timeout)
    except Exception as e:
        kevbin.box.error(f"Request failed: {e}")
        return
    
    kevbin.box.table(
        ["Field", "Value"],
        [["Status", f"{resp.status_code} {resp.reason}"], ["URL", resp.url], ["Time", f"{resp.elapsed.total_seconds():.3f}s"]]
    )
    
    kevbin.box.title("Response Headers")
    header_rows = [[k, v] for k, v in resp.headers.items()]
    kevbin.box.table(["Header", "Value"], header_rows)
    
    kevbin.box.title("Response Body")
    content_type = resp.headers.get("Content-Type", "")
    if "json" in content_type.lower():
        try:
            kevbin.box.code(json.dumps(resp.json(), indent=2))
        except:
            kevbin.box.code(resp.text[:5000])
    else:
        kevbin.box.code(resp.text[:5000])