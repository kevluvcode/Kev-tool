"""HTTP Status - Lookup HTTP status codes."""

HTTP_CODES = {
    100: ('Continue', 'Server received request headers'),
    101: ('Switching Protocols', 'Server switching protocols'),
    102: ('Processing', 'WebDAV processing'),
    200: ('OK', 'Successful response'),
    201: ('Created', 'Resource created'),
    202: ('Accepted', 'Accepted for processing'),
    203: ('Non-Authoritative Info', 'Transformed proxy response'),
    204: ('No Content', 'Success, no body'),
    205: ('Reset Content', 'Reset document view'),
    206: ('Partial Content', 'Range request fulfilled'),
    300: ('Multiple Choices', 'Multiple options'),
    301: ('Moved Permanently', 'Permanent redirect'),
    302: ('Found', 'Temporary redirect'),
    303: ('See Other', 'Redirect to GET'),
    304: ('Not Modified', 'Cached version valid'),
    307: ('Temporary Redirect', 'Temp redirect, keep method'),
    308: ('Permanent Redirect', 'Perm redirect, keep method'),
    400: ('Bad Request', 'Invalid request syntax'),
    401: ('Unauthorized', 'Authentication required'),
    402: ('Payment Required', 'Reserved'),
    403: ('Forbidden', 'Access denied'),
    404: ('Not Found', 'Resource not found'),
    405: ('Method Not Allowed', 'HTTP method not supported'),
    406: ('Not Acceptable', 'Cannot satisfy Accept header'),
    407: ('Proxy Auth Required', 'Proxy auth needed'),
    408: ('Request Timeout', 'Server timed out'),
    409: ('Conflict', 'Resource conflict'),
    410: ('Gone', 'Resource permanently gone'),
    411: ('Length Required', 'Content-Length needed'),
    412: ('Precondition Failed', 'Precondition failed'),
    413: ('Payload Too Large', 'Request body too large'),
    414: ('URI Too Long', 'Request URI too long'),
    415: ('Unsupported Media Type', 'Media type not supported'),
    416: ('Range Not Satisfiable', 'Invalid range'),
    417: ('Expectation Failed', 'Expect header failed'),
    418: ("I'm a Teapot", 'RFC 2324 easter egg'),
    422: ('Unprocessable Entity', 'Semantic errors'),
    425: ('Too Early', 'Replay risk'),
    426: ('Upgrade Required', 'Protocol upgrade needed'),
    428: ('Precondition Required', 'Precondition header needed'),
    429: ('Too Many Requests', 'Rate limited'),
    431: ('Request Header Fields Too Large', 'Headers too large'),
    451: ('Unavailable Legal', 'Legal restriction'),
    500: ('Internal Server Error', 'Server error'),
    501: ('Not Implemented', 'Method not implemented'),
    502: ('Bad Gateway', 'Invalid upstream response'),
    503: ('Service Unavailable', 'Server overloaded/down'),
    504: ('Gateway Timeout', 'Upstream timeout'),
    505: ('HTTP Version Not Supported', 'Version not supported'),
    506: ('Variant Also Negotiates', 'Negotiation error'),
    507: ('Insufficient Storage', 'Storage full'),
    508: ('Loop Detected', 'Infinite loop'),
    510: ('Not Extended', 'Extension required'),
    511: ('Network Auth Required', 'Network auth needed'),
}


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('📊', 'HTTP STATUS CODES')
    kevbin.cprint(kevbin.t.secondary, "  Enter a status code to lookup, or 'list' for all.")
    kevbin.line()

    choice = kevbin.input_choice("  Code or 'list': ").strip().lower()
    if not choice:
        return

    if choice == 'list':
        kevbin.cprint(kevbin.t.highlight, f"\n  +------+--------------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Code | Name                     | Description                      |")
        kevbin.cprint(kevbin.t.highlight, f"  +------+--------------------------+----------------------------------+")
        for code, (name, desc) in sorted(HTTP_CODES.items()):
            kevbin.cprint(kevbin.t.secondary, f"  | {code:<4} | {name:<24} | {desc:<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +------+--------------------------+----------------------------------+")
        kevbin.pause()
        return

    try:
        code = int(choice)
        name, desc = HTTP_CODES.get(code, ('Unknown', 'No description'))
        kevbin.cprint(kevbin.t.highlight, f"\n  +------+--------------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Code | Name                     | Description                      |")
        kevbin.cprint(kevbin.t.highlight, f"  +------+--------------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.secondary, f"  | {code:<4} | {name:<24} | {desc:<34} |")
        kevbin.cprint(kevbin.t.highlight, f"  +------+--------------------------+----------------------------------+")

        category = code // 100
        cats = {1: 'Informational', 2: 'Success', 3: 'Redirection', 4: 'Client Error', 5: 'Server Error'}
        kevbin.cprint(kevbin.t.accent, f"\n  Category: {cats.get(category, 'Unknown')} ({category}xx)")
    except ValueError:
        kevbin.cprint(kevbin.t.error, "  [X] Invalid input")
    kevbin.pause()
