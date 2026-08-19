import requests

def run(kevbin):
    kevbin.box.title("HTTP Header Inspector")
    url = kevbin.box.input("URL to inspect: ")
    if not url:
        return
    
    method = kevbin.box.select("Method", ["GET", "HEAD"])
    follow_redirects = kevbin.box.confirm("Follow redirects?", default=True)
    verify_ssl = kevbin.box.confirm("Verify SSL?", default=True)
    
    try:
        if method == "HEAD":
            resp = requests.head(url, allow_redirects=follow_redirects, verify=verify_ssl, timeout=30)
        else:
            resp = requests.get(url, allow_redirects=follow_redirects, verify=verify_ssl, timeout=30, stream=True)
            resp.close()
    except Exception as e:
        kevbin.box.error(f"Request failed: {e}")
        return
    
    kevbin.box.table(
        ["Field", "Value"],
        [["Status", f"{resp.status_code} {resp.reason}"], ["Final URL", resp.url]]
    )
    
    kevbin.box.title("Response Headers")
    rows = []
    for k, v in sorted(resp.headers.items()):
        rows.append([k, v])
    kevbin.box.table(["Header", "Value"], rows)
    
    if resp.history:
        kevbin.box.title("Redirect Chain")
        redirect_rows = []
        for i, r in enumerate(resp.history):
            redirect_rows.append([str(i+1), f"{r.status_code} {r.reason}", r.url])
        redirect_rows.append([str(len(resp.history)+1), f"{resp.status_code} {resp.reason}", resp.url])
        kevbin.box.table(["Step", "Status", "URL"], redirect_rows)