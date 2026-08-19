"""Web Search - Simple web search via DuckDuckGo HTML."""

try:
    import requests
    from html.parser import HTMLParser
except ImportError:
    requests = None


class ResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.in_result = False
        self.in_title = False
        self.in_snippet = False
        self.current = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and attrs.get('class', '').startswith('result__url'):
            self.in_result = True
            self.current = {'url': attrs.get('href', '')}
        elif tag == 'a' and 'result__snippet' in attrs.get('class', ''):
            self.in_snippet = True
        elif tag == 'h2' and attrs.get('class', '') == 'result__title':
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == 'a' and self.in_snippet:
            self.in_snippet = False
        elif tag == 'h2' and self.in_title:
            self.in_title = False
        elif tag == 'div' and self.in_result:
            if self.current:
                self.results.append(self.current)
            self.in_result = False

    def handle_data(self, data):
        if self.in_title:
            self.current.setdefault('title', '')
            self.current['title'] += data
        elif self.in_snippet:
            self.current.setdefault('snippet', '')
            self.current['snippet'] += data


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🔎', 'WEB SEARCH')
    kevbin.cprint(kevbin.t.secondary, "  Enter a search query.")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    query = kevbin.input_choice("  Query: ").strip()
    if not query:
        return

    try:
        r = requests.get('https://html.duckduckgo.com/html/', params={'q': query}, timeout=10)
        parser = ResultParser()
        parser.feed(r.text)

        kevbin.cprint(kevbin.t.highlight, f"\n  +----+----------------------------------+----------------------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | #  | Title                            | Snippet                          |")
        kevbin.cprint(kevbin.t.highlight, f"  +----+----------------------------------+----------------------------------+")
        for i, res in enumerate(parser.results[:10], 1):
            title = res.get('title', '')[:32]
            snippet = res.get('snippet', '')[:32]
            kevbin.cprint(kevbin.t.secondary, f"  | {i:<2} | {title:<32} | {snippet:<32} |")
        kevbin.cprint(kevbin.t.highlight, f"  +----+----------------------------------+----------------------------------+")

        if not parser.results:
            kevbin.cprint(kevbin.t.warning, "  [!] No results found")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()
