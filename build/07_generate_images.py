"""
v2 image fetcher — accuracy-first.

Strategy (priority order):
  1. English Wikipedia (using English definition) — most semantic, broadest coverage
  2. German Wikipedia (using German noun) — for German-specific cultural items
  3. Openverse with disambiguated English query
  4. Openverse with German term as last resort

Disambiguation: For polysemous nouns (Bank=bank/bench, Schloss=castle/lock),
the deck's `def1` field already gives us the PRIMARY meaning. We use it directly
rather than the German word, which avoids ambiguity.
"""
import urllib.request, urllib.parse, json, sys, re, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

MEDIA   = Path("C:/Users/Mohith Akash/AppData/Roaming/Anki2/User 1/collection.media")
MAP     = Path("C:/Users/Mohith Akash/AppData/Local/Temp/image_map.json")
UA      = "GermanAnkiDeck/4.0 (educational; community deck)"
WORKERS = 8

with open("C:/Users/Mohith Akash/AppData/Local/Temp/deck_notes.json", encoding="utf-8") as f:
    notes = json.load(f)

ARTICLES = ('der','die','das','der, die','die (pl)','der, das',
            'die, das','der, die, das','das, die (pl)')
nouns = [n for n in notes if n['pos1'] in ARTICLES]
print(f"Eligible noun cards: {len(nouns)}")

# ── helpers ────────────────────────────────────────────────────────────────────

def german_base(word):
    base = word.split(',')[0].strip()
    parts = base.split()
    if parts and parts[0].lower() in ('der','die','das'):
        parts = parts[1:]
    return ' '.join(parts).strip()

def english_term(noun):
    """Clean English search term from def1."""
    en = (noun.get('def1','') or '').strip()
    en = re.sub(r'\(.*?\)', '', en).strip()      # strip parentheticals
    en = en.split(',')[0].strip()                # first meaning only
    en = en.split(';')[0].strip()
    en = en.rstrip('.,;:').strip()
    # Strip leading articles like "a", "an", "the"
    en = re.sub(r'^(a|an|the)\s+', '', en, flags=re.I).strip()
    # Strip "to " infinitive markers
    en = re.sub(r'^to\s+', '', en, flags=re.I).strip()
    return en

def safe_filename(word):
    base = german_base(word).lower()
    base = re.sub(r'[^\w]','_', base)[:40].strip('_')
    return f"img_de_{base}.jpg"

# ── image sources ──────────────────────────────────────────────────────────────

def wiki_image(lang, query):
    """Fetch lead image from <lang>.wikipedia.org for `query`."""
    if not query: return None
    url = (f"https://{lang}.wikipedia.org/w/api.php?action=query"
           f"&titles={urllib.parse.quote(query)}"
           f"&prop=pageimages&pithumbsize=400"
           f"&format=json&redirects=1")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        r = urllib.request.urlopen(req, timeout=8)
        d = json.loads(r.read())
        for pid, page in d['query']['pages'].items():
            if pid == '-1': return None
            return page.get('thumbnail', {}).get('source')
    except Exception:
        return None
    return None

def openverse_image(query):
    if not query: return None
    url = (f"https://api.openverse.org/v1/images/"
           f"?q={urllib.parse.quote(query)}"
           f"&page_size=1"
           f"&license_type=commercial,modification")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        r = urllib.request.urlopen(req, timeout=10)
        d = json.loads(r.read())
        results = d.get('results', [])
        if results:
            return results[0].get('thumbnail') or results[0].get('url')
    except Exception:
        return None
    return None

def download(url, path):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        r = urllib.request.urlopen(req, timeout=15)
        data = r.read()
        if len(data) < 800: return False
        path.write_bytes(data)
        return True
    except Exception:
        return False

# ── per-noun resolution ────────────────────────────────────────────────────────

def process(noun):
    nid   = str(noun['id'])
    fname = safe_filename(noun['word'])
    out   = MEDIA / fname

    de = german_base(noun['word'])
    en = english_term(noun)

    # 1. English Wikipedia — primary
    if en:
        url = wiki_image('en', en)
        if url and download(url, out):
            return nid, fname, "en_wiki"

    # 2. German Wikipedia — for German-specific concepts
    if de:
        url = wiki_image('de', de)
        if url and download(url, out):
            return nid, fname, "de_wiki"

    # 3. Openverse with English definition
    if en:
        url = openverse_image(en)
        if url and download(url, out):
            return nid, fname, "ov_en"

    # 4. Openverse with German base
    if de:
        url = openverse_image(de)
        if url and download(url, out):
            return nid, fname, "ov_de"

    return nid, "", "fail"

# ── main ───────────────────────────────────────────────────────────────────────

print(f"Re-fetching all images using priority strategy ({WORKERS} workers) …")
results = {}
counters = {"en_wiki":0,"de_wiki":0,"ov_en":0,"ov_de":0,"fail":0}

with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futures = {ex.submit(process, n): n for n in nouns}
    done = 0
    for fut in as_completed(futures):
        nid, fname, src = fut.result()
        if fname:
            results[nid] = fname
        counters[src] = counters.get(src, 0) + 1
        done += 1
        if done % 100 == 0 or done == len(nouns):
            print(f"  {done}/{len(nouns)}  "
                  f"enWiki:{counters['en_wiki']} deWiki:{counters['de_wiki']} "
                  f"ovEn:{counters['ov_en']} ovDe:{counters['ov_de']} fail:{counters['fail']}")

total = len(nouns)
print(f"\nDone — {len(results)}/{total} images ({100*len(results)//total}% coverage)")
print(f"  English Wikipedia: {counters['en_wiki']}")
print(f"  German Wikipedia:  {counters['de_wiki']}")
print(f"  Openverse (en):    {counters['ov_en']}")
print(f"  Openverse (de):    {counters['ov_de']}")
print(f"  Failed:            {counters['fail']}")

with open(MAP, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False)
print(f"Saved → {MAP}")
