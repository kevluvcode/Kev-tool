"""Tech Stack - Detect website technologies."""

try:
    import requests
except ImportError:
    requests = None


SIGNATURES = {
    'WordPress': ['wp-content', 'wp-includes', 'wordpress'],
    'React': ['react', '_reactRootContainer', 'react-dom'],
    'Vue.js': ['vue.js', 'vue.min.js', 'data-v-'],
    'Angular': ['angular', 'ng-version', 'ng-app'],
    'Next.js': ['_next/', 'next.js', '__NEXT_DATA__'],
    'Nuxt.js': ['_nuxt/', 'nuxt.js'],
    'Svelte': ['svelte', '__SVELTE__'],
    'jQuery': ['jquery', 'jquery.min.js'],
    'Bootstrap': ['bootstrap.min.css', 'bootstrap.min.js'],
    'Tailwind': ['tailwind', 'tailwindcss'],
    'Cloudflare': ['cf-ray', 'cloudflare'],
    'Nginx': ['nginx'],
    'Apache': ['apache'],
    'IIS': ['iis', 'microsoft-iis'],
    'PHP': ['x-powered-by: php'],
    'Node.js': ['x-powered-by: express', 'express'],
    'Django': ['django', 'csrftoken'],
    'Flask': ['flask', 'session'],
    'Laravel': ['laravel_session', 'x-powered-by: laravel'],
    'Ruby on Rails': ['rails', '_session_id'],
    'Go': ['go', 'golang'],
    'Python': ['python'],
    'Java': ['jsp', 'jsessionid', 'tomcat', 'jetty'],
    'ASP.NET': ['asp.net', '__viewstate', 'x-aspnet-version'],
    'GraphQL': ['graphql'],
    'Webpack': ['webpack'],
    'Vite': ['vite'],
    'Parcel': ['parcel'],
    'Gatsby': ['gatsby'],
    'Hugo': ['hugo'],
    'Jekyll': ['jekyll'],
    'Shopify': ['shopify', 'shopify.theme'],
    'Wix': ['wix', 'wixstatic'],
    'Squarespace': ['squarespace'],
    'Webflow': ['webflow'],
    'Framer': ['framer'],
    'Vercel': ['vercel', 'x-vercel'],
    'Netlify': ['netlify', 'x-nf'],
    'Firebase': ['firebase', 'firebaseapp'],
    'AWS': ['amazonaws', 'cloudfront', 'awselb'],
    'Google Cloud': ['googleapis', 'gstatic'],
    'Azure': ['azure', 'azurewebsites'],
    'Heroku': ['heroku'],
    'DigitalOcean': ['digitalocean'],
    'Fastly': ['fastly', 'x-served-by'],
    'Akamai': ['akamai', 'akamaighost'],
}


def run(kevbin):
    kevbin.clear()
    kevbin.section_header('🔧', 'TECH STACK DETECTOR')
    kevbin.cprint(kevbin.t.secondary, "  Enter a URL to detect technologies used.")
    kevbin.line()

    if requests is None:
        kevbin.cprint(kevbin.t.error, "  [X] pip install requests")
        kevbin.pause()
        return

    url = kevbin.input_choice("  URL: ").strip()
    if not url:
        return

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        headers = {k.lower(): v.lower() for k, v in r.headers.items()}
        html = r.text.lower()

        found = []
        for tech, sigs in SIGNATURES.items():
            for sig in sigs:
                if sig in html or any(sig in v for v in headers.values()):
                    found.append(tech)
                    break

        kevbin.cprint(kevbin.t.highlight, f"\n  +------------------+")
        kevbin.cprint(kevbin.t.highlight, f"  | Technology       |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+")
        if found:
            for tech in sorted(found):
                kevbin.cprint(kevbin.t.secondary, f"  | {tech:<18} |")
        else:
            kevbin.cprint(kevbin.t.dim, f"  | (none detected)  |")
        kevbin.cprint(kevbin.t.highlight, f"  +------------------+")

        kevbin.cprint(kevbin.t.txt, f"\n  Status: {r.status_code} | Server: {r.headers.get('Server', '?')}")
    except Exception as e:
        kevbin.cprint(kevbin.t.error, f"  [X] {e}")
    kevbin.pause()
