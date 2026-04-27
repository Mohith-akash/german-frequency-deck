"""Download Noto Sans subset that supports IPA characters."""
import urllib.request, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

MEDIA = Path("C:/Users/Mohith Akash/AppData/Roaming/Anki2/User 1/collection.media")
ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'

# Get the CSS listing all subsets
url = 'https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&display=swap'
req = urllib.request.Request(url, headers={'User-Agent': ua})
css = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')

# Parse subsets
sections = re.split(r'/\*\s*([^*]+)\s*\*/', css)
subsets = []
for i in range(1, len(sections)-1, 2):
    name = sections[i].strip()
    block = sections[i+1]
    m_url = re.search(r'src:\s*url\(([^)]+\.woff2)\)', block)
    m_rng = re.search(r'unicode-range:\s*([^;]+);', block)
    m_wgt = re.search(r'font-weight:\s*(\d+)', block)
    if m_url and m_rng:
        subsets.append({
            'name': name, 'url': m_url.group(1),
            'range': m_rng.group(1), 'weight': m_wgt.group(1) if m_wgt else '400'
        })

# We need: latin-ext (covers most IPA chars used) and latin (basic Latin)
# IPA range is U+0250-02AF and U+02B0-02FF (modifier letters)
# These might be in 'latin-ext' or a dedicated subset
print("Subsets available:")
for s in subsets:
    print(f"  {s['name']:15} weight={s['weight']} range={s['range'][:60]}")

# Download the latin-ext subset (most likely to contain IPA Extensions)
# AND latin (covers basic chars)
target_subsets = [s for s in subsets if s['name'] in ('latin', 'latin-ext')]
font_files = []
for s in target_subsets:
    fname = f"NotoSans-{s['weight']}-{s['name']}.woff2"
    out = MEDIA / fname
    print(f"Downloading {s['name']} weight {s['weight']} ...")
    req = urllib.request.Request(s['url'], headers={'User-Agent': ua})
    data = urllib.request.urlopen(req, timeout=15).read()
    out.write_bytes(data)
    print(f"  -> {fname} ({len(data)//1024} KB)")
    font_files.append({'name': s['name'], 'weight': s['weight'], 'fname': fname, 'range': s['range']})

# Now we also need an explicit IPA-supporting font
# Charis SIL is the gold standard for IPA — let me try downloading it
# Actually, let me use Noto Sans Phonetic (a separate Google Font designed for IPA)
print("\nDownloading Noto Sans Phonetic for IPA...")
url2 = 'https://fonts.googleapis.com/css2?family=Charis+SIL:wght@400;700&display=swap'
try:
    req = urllib.request.Request(url2, headers={'User-Agent': ua})
    css2 = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    # Get URL
    m = re.search(r'src:\s*url\(([^)]+\.woff2)\)', css2)
    if m:
        data = urllib.request.urlopen(urllib.request.Request(m.group(1), headers={'User-Agent': ua}), timeout=15).read()
        (MEDIA / "CharisSIL-Regular.woff2").write_bytes(data)
        print(f"  -> CharisSIL-Regular.woff2 ({len(data)//1024} KB)")
        font_files.append({'name': 'CharisSIL', 'weight': '400', 'fname': 'CharisSIL-Regular.woff2', 'range': 'U+0000-FFFF'})
except Exception as e:
    print(f"  Charis SIL failed: {e}")

# Save mapping for the addon
import json
with open("C:/Users/Mohith Akash/AppData/Local/Temp/font_files.json", "w", encoding="utf-8") as f:
    json.dump(font_files, f, ensure_ascii=False, indent=2)
print(f"\nFont files saved to media folder.")
print(f"Mapping saved → font_files.json")
