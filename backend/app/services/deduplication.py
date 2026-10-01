import hashlib
import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

def make_dedupe_key(title):
    return hashlib.sha256(" ".join(re.findall(r"\w+", title.lower())).encode()).hexdigest()

def canonical_url(url):
    parts = urlsplit(str(url))
    query = [(k,v) for k,v in parse_qsl(parts.query, keep_blank_values=True) if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, urlencode(sorted(query)), ""))
