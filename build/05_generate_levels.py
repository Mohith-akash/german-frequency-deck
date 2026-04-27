"""
Fixed level generation with proper Goethe word list cleaning.
Handles all edge cases:
  - ein-(1)   → ein
  - ihr/ihm/ihn(1) → ihr, ihm, ihn  (expand slash forms)
  - ander-    → ander
  - meist-    → meist
  - welch-    → welch
  - das Mädchen, – → mädchen
  - einfach(3) → einfach
"""
import urllib.request, json, re, sys, string
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

LEVELS_OUT = Path("C:/Users/Mohith Akash/AppData/Local/Temp/levels.json")
base_url   = "https://raw.githubusercontent.com/ilkermeliksitki/goethe-institute-wordlist/main"

def clean_goethe(raw):
    """
    Returns a SET of cleaned lemmas from one raw Goethe entry.
    One entry can yield multiple lemmas (slash-separated forms).
    """
    w = raw.strip().lower()

    # Strip sense numbers: (1), (2), (3) anywhere
    w = re.sub(r'\(\d+\)$', '', w).strip()

    # Expand slash-separated pronoun forms: "ihr/ihm/ihn" → ['ihr','ihm','ihn']
    if '/' in w:
        parts = w.split('/')
        result = set()
        for part in parts:
            result |= clean_goethe(part)  # recurse on each
        return result

    # Strip article prefix
    for art in ('der ', 'die ', 'das ', 'sich '):
        if w.startswith(art):
            w = w[len(art):]
            break

    # Strip plural/genitive info after comma: "Jahr, -e" → "jahr"
    w = w.split(',')[0].strip()

    # Strip trailing dash/hyphen (stem markers): "ein-" → "ein", "ander-" → "ander"
    w = w.rstrip('-').rstrip('–').strip()

    # Strip trailing parenthetical if still present
    w = re.sub(r'\s*\(.*\)\s*$', '', w).strip()

    return {w} if w else set()


print("Fetching Goethe word lists …")
goethe = {}
for level in ['a1', 'a2', 'b1']:
    goethe[level] = set()
    for letter in string.ascii_lowercase:
        url = f"{base_url}/{level}/{letter}.tsv"
        try:
            r = urllib.request.urlopen(url, timeout=8)
            for line in r.read().decode('utf-8').splitlines():
                col0 = line.split('\t')[0] if '\t' in line else line
                if col0.strip():
                    goethe[level] |= clean_goethe(col0)
        except Exception:
            pass
    print(f"  {level}: {len(goethe[level])} lemmas")

# Verify fixes
for w in ['ein','du','mir','mich','ihr','dies','all','ander','meist','welch']:
    found = [l for l in ['a1','a2','b1'] if w in goethe[l]]
    print(f"  '{w}' in: {found if found else 'NONE — needs manual fallback'}")

# Exclusive level sets
a1_only = goethe['a1']
a2_only = goethe['a2'] - goethe['a1']
b1_only = goethe['b1'] - goethe['a2']

# ── Manual overrides for words that appear in Goethe exams
# but are stored in unusual formats not captured by the lists
# These are all unambiguously basic grammar words.
MANUAL_A1 = {
    # Pronouns (all cases)
    'ich','mich','mir','du','dich','dir','er','ihn','ihm','sie','es',
    'wir','uns','ihr','euch','sie','sich',
    # Articles (all forms)
    'ein','eine','einen','einem','einer','eines',
    'der','die','das','den','dem','des',
    'kein','keine','keinen','keinem','keiner','keines',
    # Possessives
    'mein','meine','meinen','meinem','meiner','meines',
    'dein','deine','deinen','deinem','deiner','deines',
    'sein','seine','seinen','seinem','seiner','seines',
    'ihr','ihre','ihren','ihrem','ihrer','ihres',
    'unser','unsere','unseren','unserem','unserer','unseres',
    'euer','eure','euren','eurem','eurer','eures',
    # Demonstratives
    'dies','diese','diesen','diesem','dieser','dieses',
    'jed','jede','jeden','jedem','jeder','jedes',
    # Indefinites
    'all','alle','allen','allem','aller','alles',
    'ander','andere','anderen','anderem','anderer','anderes',
    'meist','meiste','meisten',
    'manch','manche','manchen',
    'welch','welche','welchen','welchem','welcher','welches',
    # Basic adverbs/particles always at A1
    'da','hier','dort','nun','jetzt','schon','noch','auch','sehr',
    'mehr','viel','so','wie','als','doch','gar','ja','nein',
    'nicht','nur','aber','oder','und','weil','wenn','dass',
    'wer','was','wo','wie','wann','warum','woher','wohin',
    # Numbers (all unambiguously A1)
    'null','ein','zwei','drei','vier','fünf','sechs','sieben','acht',
    'neun','zehn','elf','zwölf','zwanzig','hundert','tausend',
    # Ordinals
    'erst','erste','ersten','zweite','zweiten','dritte','letzt','letzte',
    # Common nouns always taught at A1 even if not in list
    'jahr','tag','mal','mensch','kind','frau','mann','zeit','hand',
    'land','welt','haus','stadt','schule','arbeit','geld','frage',
    'wort','buch','auto','weg','platz','kopf','auge','herz',
    # Common adjectives A1
    'groß','klein','gut','schlecht','neu','alt','jung','lang','kurz',
    'schön','schnell','langsam','viel','wenig','mehr','letzt',
}

a1_only = a1_only | MANUAL_A1
# Remove manual overrides from higher levels to avoid promotion
a2_only = a2_only - MANUAL_A1
b1_only = b1_only - MANUAL_A1

print(f"\nAfter manual overrides:")
print(f"  A1: {len(a1_only)} | A2-excl: {len(a2_only)} | B1-excl: {len(b1_only)}")

# Verify fixes
print("\nVerification:")
for w in ['ein','du','mir','mich','dies','ihr','all','ander','meist','welch','da','hier','jetzt']:
    if w in a1_only:   lvl = 'A1'
    elif w in a2_only: lvl = 'A2'
    elif w in b1_only: lvl = 'B1'
    else:              lvl = 'B2+ (still not found)'
    print(f"  {w}: {lvl}")

# ── Cross-reference deck ────────────────────────────────────────────────────────
with open("C:/Users/Mohith Akash/AppData/Local/Temp/deck_notes.json", encoding='utf-8') as f:
    notes = json.load(f)

def deck_base(word):
    w = word.split(',')[0].strip().lower()
    # Strip article prefix
    for art in ('der ','die ','das ','sich '):
        if w.startswith(art):
            w = w[len(art):]
    # Strip inflection markers: "andere (r" → "andere", "jede (r" → "jede"
    w = re.sub(r'\s*\(.*$', '', w).strip()
    return w.strip()

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
    counts[v] = counts.get(v,0)+1
print(f"\nFinal level counts: {counts}")

# Sanity check — show top 30 by rank and their levels
print("\nTop 30 words by frequency rank:")
top30 = sorted(notes, key=lambda n: int(n['rank']))[:30]
for n in top30:
    nid = str(n['id'])
    print(f"  #{n['rank']:>4} {n['word'][:30]:<32} → {levels_map[nid]}")

with open(LEVELS_OUT, 'w', encoding='utf-8') as f:
    json.dump(levels_map, f, ensure_ascii=False)
print(f"\nSaved → {LEVELS_OUT}")
