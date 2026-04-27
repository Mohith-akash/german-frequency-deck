"""
Generate:
1. levels.json — {note_id: "A1"|"A2"|"B1"|"B2+"}
2. families.json — {note_id: ["related_word1", ...]}
"""
import urllib.request, json, re, sys, string
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

LEVELS_OUT  = Path("C:/Users/Mohith Akash/AppData/Local/Temp/levels.json")
FAMILIES_OUT= Path("C:/Users/Mohith Akash/AppData/Local/Temp/families.json")

with open("C:/Users/Mohith Akash/AppData/Local/Temp/deck_notes.json", encoding="utf-8") as f:
    notes = json.load(f)

# ── 1. GOETHE LEVELS ─────────────────────────────────────────────────────────

print("Fetching Goethe word lists …")
base = "https://raw.githubusercontent.com/ilkermeliksitki/goethe-institute-wordlist/main"

def clean_goethe(raw):
    w = raw.strip().lower()
    w = re.sub(r'\(\d+\)$', '', w).strip()
    for art in ('der ', 'die ', 'das ', 'sich '):
        if w.startswith(art):
            w = w[len(art):]
    return w.split(',')[0].strip()

goethe = {}
for level in ['a1', 'a2', 'b1']:
    goethe[level] = set()
    for letter in string.ascii_lowercase:
        url = f"{base}/{level}/{letter}.tsv"
        try:
            r = urllib.request.urlopen(url, timeout=8)
            for line in r.read().decode('utf-8').splitlines():
                col0 = line.split('\t')[0] if '\t' in line else line
                if col0.strip():
                    goethe[level].add(clean_goethe(col0))
        except Exception:
            pass
    print(f"  {level}: {len(goethe[level])} words")

a1_only = goethe['a1']
a2_only = goethe['a2'] - goethe['a1']
b1_only = goethe['b1'] - goethe['a2']

def deck_base(word):
    w = word.split(',')[0].strip().lower()
    for art in ('der ', 'die ', 'das ', 'sich '):
        if w.startswith(art):
            w = w[len(art):]
    return w

levels_map = {}
for n in notes:
    base = deck_base(n['word'])
    nid  = str(n['id'])
    if base in a1_only:
        levels_map[nid] = "A1"
    elif base in a2_only:
        levels_map[nid] = "A2"
    elif base in b1_only:
        levels_map[nid] = "B1"
    else:
        levels_map[nid] = "B2+"

counts = {}
for v in levels_map.values():
    counts[v] = counts.get(v, 0) + 1
print("Level counts:", counts)

with open(LEVELS_OUT, 'w', encoding='utf-8') as f:
    json.dump(levels_map, f, ensure_ascii=False)
print(f"Saved → {LEVELS_OUT}")

# ── 2. WORD FAMILIES ─────────────────────────────────────────────────────────

print("\nComputing word families …")

# Common German prefixes to strip for stem matching
PREFIXES = [
    'ver','be','ge','er','ent','zer','miss','un','ur',
    'aus','an','auf','ab','mit','nach','vor','zu','durch',
    'um','über','unter','hinter','wider','wieder','ein',
    'fort','hin','her','los','weg','vor','zurück'
]
# Common suffixes to strip for stem matching
SUFFIXES = [
    'ung','heit','keit','schaft','lich','ig','isch','isch',
    'er','erin','erin','ung','heit','keit','en','end',
    'bar','sam','los','voll','reich','arm','frei','leer',
    'ness','tion','ion','ität','tät','ment'
]

def extract_stems(word):
    """Return possible stems for this word."""
    w = deck_base(word).replace('ä','a').replace('ö','o').replace('ü','u').replace('ß','ss')
    stems = {w}
    # Strip prefixes
    for p in PREFIXES:
        if w.startswith(p) and len(w) - len(p) >= 4:
            stems.add(w[len(p):])
    # Strip suffixes
    for s in SUFFIXES:
        if w.endswith(s) and len(w) - len(s) >= 3:
            stems.add(w[:-len(s)])
    # Umlaut variants
    stems_extra = set()
    for stem in stems:
        stems_extra.add(stem.replace('ae','a').replace('oe','o').replace('ue','u'))
    stems |= stems_extra
    return {s for s in stems if len(s) >= 4}

# Build stem → notes index
stem_index = {}  # stem -> list of (nid, display_word)
for n in notes:
    nid  = str(n['id'])
    word = n['word'].split(',')[0].strip()  # display form
    for stem in extract_stems(n['word']):
        if stem not in stem_index:
            stem_index[stem] = []
        stem_index[stem].append((nid, word))

# For each note, find related words via shared stem
families = {}
for n in notes:
    nid = str(n['id'])
    related = {}  # use dict to deduplicate by word text
    for stem in extract_stems(n['word']):
        for (other_nid, other_word) in stem_index.get(stem, []):
            if other_nid != nid:
                related[other_word] = other_nid
    # Only keep if 1-5 related words (avoid overcrowding)
    if 1 <= len(related) <= 6:
        families[nid] = list(related.keys())
    else:
        families[nid] = []

has_family = sum(1 for v in families.values() if v)
print(f"Notes with word families: {has_family}/{len(notes)}")
# Sample
for n in notes[:200]:
    nid = str(n['id'])
    if families.get(nid):
        print(f"  {n['word']} → {families[nid]}")
        break

with open(FAMILIES_OUT, 'w', encoding='utf-8') as f:
    json.dump(families, f, ensure_ascii=False)
print(f"Saved → {FAMILIES_OUT}")
