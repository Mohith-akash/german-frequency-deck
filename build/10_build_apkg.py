"""
Build the v2.1 .apkg directly from the current Anki collection, bypassing the GUI export.
Strips scheduling info but keeps all media.
"""
import json, os, re, shutil, sqlite3, sys, tempfile, zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ANKI_DIR  = Path("C:/Users/Mohith Akash/AppData/Roaming/Anki2/User 1")
COLLECTION = ANKI_DIR / "collection.anki2"
MEDIA_DIR  = ANKI_DIR / "collection.media"
OUTPUT     = Path("C:/Users/Mohith Akash/OneDrive/Desktop/german-frequency-deck-v2.1.apkg")

print(f"Source collection: {COLLECTION}")
print(f"Source media:      {MEDIA_DIR}")
print(f"Output:            {OUTPUT}")

# 0. Checkpoint the WAL into the main DB so our copy has all writes
print("\nCheckpointing WAL into main DB …")
src_db = sqlite3.connect(str(COLLECTION), timeout=10)
src_db.create_collation("unicase", lambda a,b: (a > b) - (a < b))
src_db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
src_db.close()

# 1. Build the working .apkg in a temp dir
work = Path(tempfile.mkdtemp(prefix="apkg_build_"))
print(f"Work dir: {work}")

# 2. Copy + clean collection DB (strip scheduling so importers start fresh)
print("Copying collection DB …")
shutil.copy2(COLLECTION, work / "collection.anki21")

db = sqlite3.connect(str(work / "collection.anki21"))
db.create_collation("unicase", lambda a,b: (a > b) - (a < b))
cur = db.cursor()

# Strip review history & reset scheduling — but PRESERVE queue=-1 (suspended)
cur.execute("DELETE FROM revlog")
cur.execute("""
    UPDATE cards
    SET due  = ord,
        ivl  = 0,
        factor = 0,
        reps = 0,
        lapses = 0,
        left = 0,
        odue = 0,
        odid = 0,
        type = 0,
        queue = CASE WHEN queue = -1 THEN -1 ELSE 0 END,
        mod  = strftime('%s','now')
""")
cur.execute("SELECT COUNT(*) FROM cards WHERE queue = -1")
sus = cur.fetchone()[0]
print(f"  Scheduling stripped (revlog cleared, {sus} suspensions preserved)")

# Note: empty/orphan notetypes (with 0 notes) are kept in the DB since Anki
# uses FTS triggers that make safe deletion from `fields` non-trivial without
# the full Anki Python library. They're harmless — importers only see notetypes
# linked to actual notes in the deck browser. The duplicate "Card 1" name only
# appears in raw DB queries, never in the UI.

db.commit()
db.close()

# 3. Scan the DB for referenced media (so we only include used files)
db = sqlite3.connect(str(work / "collection.anki21"))
cur = db.cursor()
cur.execute("SELECT flds FROM notes")
referenced = set()
snd_re = re.compile(r"\[sound:([^\]]+)\]")
img_re = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']')
for (flds,) in cur.fetchall():
    referenced.update(snd_re.findall(flds))
    referenced.update(img_re.findall(flds))

# Also scan templates and CSS for media (the IPA font)
cur.execute("SELECT config FROM notetypes")
for (cfg,) in cur.fetchall():
    if cfg:
        # CSS may reference _charis.woff2
        try:
            txt = cfg.decode("utf-8", errors="ignore")
            for m in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", txt):
                if not m.startswith("http"):
                    referenced.add(m)
        except Exception:
            pass

cur.execute("SELECT config FROM templates")
for (cfg,) in cur.fetchall():
    if cfg:
        try:
            txt = cfg.decode("utf-8", errors="ignore")
            referenced.update(snd_re.findall(txt))
            referenced.update(img_re.findall(txt))
        except Exception:
            pass

db.close()
print(f"  Found {len(referenced)} referenced media files")

# 4. Copy media files with sequential numeric names + build manifest
print("Bundling media …")
manifest = {}
idx = 0
missing = 0
for fname in sorted(referenced):
    src = MEDIA_DIR / fname
    if not src.exists():
        missing += 1
        continue
    dst = work / str(idx)
    shutil.copy2(src, dst)
    manifest[str(idx)] = fname
    idx += 1

with open(work / "media", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False)
print(f"  Bundled {idx} files ({missing} missing references skipped)")

# 5. Zip into .apkg
print(f"\nZipping → {OUTPUT.name} …")
if OUTPUT.exists():
    OUTPUT.unlink()

with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for item in work.iterdir():
        if item.is_file():
            zf.write(item, item.name)

shutil.rmtree(work)
size_mb = OUTPUT.stat().st_size / 1024 / 1024
print(f"\n✓ Built: {OUTPUT}")
print(f"  Size: {size_mb:.1f} MB")
