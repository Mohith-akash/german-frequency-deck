"""
Re-fetch all noun images using DuckDuckGo image search (much higher quality than Openverse).
Overwrites existing files in place, then optimization is handled separately.

Strategy:
  - Query = the clean English meaning from def1 (already disambiguated)
  - For abstract nouns, append "concept" or "icon" to get cleaner imagery
  - 5 concurrent workers + 0.4s sleep per worker = polite to DDG
  - Skip on rate limit, retry after backoff
"""
import urllib.request, json, sys, re, os, time, random
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from ddgs import DDGS

sys.stdout.reconfigure(encoding="utf-8")

MEDIA   = Path("C:/Users/Mohith Akash/AppData/Roaming/Anki2/User 1/collection.media")
MAP     = Path("C:/Users/Mohith Akash/AppData/Local/Temp/image_map.json")
UA      = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
WORKERS = 4

with open("C:/Users/Mohith Akash/AppData/Local/Temp/deck_notes.json", encoding="utf-8") as f:
    notes = json.load(f)
with open(MAP, encoding="utf-8") as f:
    existing_map = json.load(f)

ARTICLES = ('der','die','das','der, die','die (pl)','der, das','die, das','der, die, das','das, die (pl)')
nouns = [n for n in notes if n['pos1'] in ARTICLES]
print(f"Nouns to refresh: {len(nouns)}")

# Bad/spammy domains to skip (return next result)
SKIP_DOMAINS = {
    "logo.com",          # logo generators
    "lookaside.fbsbx.com",
    "scontent",
    "fbcdn",
    "instagram",
    "tiktok",
}
# Preferred sources (high quality)
PREFERRED_DOMAINS = {
    "upload.wikimedia.org",
    "britannica.com",
    "istockphoto.com",
    "shutterstock.com",
    "dreamstime.com",
    "alamy.com",
    "gettyimages.com",
    "pixabay.com",
    "pexels.com",
    "unsplash.com",
    "flickr.com",
}

def english_term(noun):
    en = (noun.get('def1','') or '').strip()
    en = re.sub(r'\(.*?\)', '', en).strip()
    en = en.split(',')[0].split(';')[0].strip().rstrip('.,;:').strip()
    en = re.sub(r'^(a|an|the)\s+', '', en, flags=re.I).strip()
    en = re.sub(r'^to\s+', '', en, flags=re.I).strip()
    return en

def safe_filename(word):
    base = word.split(',')[0].strip().lower()
    for art in ('der ','die ','das '):
        if base.startswith(art): base = base[len(art):]
    base = re.sub(r'[^\w]','_', base)[:40].strip('_')
    return f"img_de_{base}.jpg"

def domain_of(url):
    try:
        return url.split('/')[2].lower()
    except Exception:
        return ""

def pick_best(results):
    """From the DDG result list, pick the best URL — preferred domain first, skip junk."""
    if not results: return None
    # Pass 1: preferred domains
    for r in results:
        url = r.get('image','')
        d = domain_of(url)
        if any(p in d for p in PREFERRED_DOMAINS):
            return url
    # Pass 2: any non-junk
    for r in results:
        url = r.get('image','')
        d = domain_of(url)
        if not any(s in d for s in SKIP_DOMAINS):
            return url
    return None

def download(url, path):
    if not url: return False
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://duckduckgo.com/"})
            r   = urllib.request.urlopen(req, timeout=15)
            data = r.read()
            if len(data) < 1500: return False
            # Verify it's actually an image
            if not (data[:3] == b'\xff\xd8\xff' or data[:4] == b'\x89PNG' or data[:4] == b'RIFF' or data[:6] in (b'GIF87a',b'GIF89a')):
                return False
            path.write_bytes(data)
            return True
        except Exception:
            if attempt == 0: time.sleep(1.5)
    return False

# Thread-local DDGS instance
import threading
_tls = threading.local()
def get_ddgs():
    if not hasattr(_tls, 'ddgs'):
        _tls.ddgs = DDGS()
    return _tls.ddgs

def process(noun):
    nid   = str(noun['id'])
    fname = safe_filename(noun['word'])
    out   = MEDIA / fname
    en    = english_term(noun)
    if not en:
        return nid, "", "no_query"

    # Small polite delay
    time.sleep(0.2 + random.random()*0.3)

    try:
        results = list(get_ddgs().images(query=en, max_results=5, safesearch="off"))
    except Exception as e:
        return nid, "", f"ddg_err:{str(e)[:30]}"

    url = pick_best(results)
    if not url:
        return nid, "", "no_url"
    if download(url, out):
        return nid, fname, "ok"
    return nid, "", "dl_fail"

# ── Run ────────────────────────────────────────────────────────────────────────
results_map = {}
counters = {"ok":0, "no_url":0, "dl_fail":0, "no_query":0, "ddg_err":0}

print(f"Refreshing with {WORKERS} workers …")
start = time.time()

with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futures = {ex.submit(process, n): n for n in nouns}
    done = 0
    for fut in as_completed(futures):
        nid, fname, status = fut.result()
        if fname:
            results_map[nid] = fname
            counters['ok'] += 1
        else:
            kind = status.split(':')[0]
            counters[kind] = counters.get(kind, 0) + 1
        done += 1
        if done % 25 == 0 or done == len(nouns):
            elapsed = time.time() - start
            rate = done / elapsed if elapsed else 0
            eta = (len(nouns) - done) / rate if rate else 0
            print(f"  {done}/{len(nouns)}  ok:{counters['ok']} fail:{sum(counters.values())-counters['ok']} "
                  f"({rate:.1f}/s, ETA {eta/60:.1f}min)")

print(f"\nDone in {(time.time()-start)/60:.1f} min")
print(f"  OK:       {counters['ok']}")
for k, v in counters.items():
    if k != 'ok' and v:
        print(f"  {k}: {v}")

# Merge new successes into existing map (don't lose images that worked before)
final_map = dict(existing_map)
final_map.update(results_map)
with open(MAP, "w", encoding="utf-8") as f:
    json.dump(final_map, f, ensure_ascii=False)
print(f"\nUpdated image_map.json — total: {len(final_map)} images")
