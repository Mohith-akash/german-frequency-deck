"""
Step 1 — extract the source .apkg into JSON files used by the rest of the pipeline.

Usage:
  python 01_extract_deck.py path/to/source.apkg

Outputs (written to system temp directory):
  deck_notes.json   — every note with all 16 fields (rank, word, IPA, defs, examples, …)
  deck_verbs.json   — subset where part-of-speech is verb/aux (used by step 04)
"""
import json
import os
import re
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

if len(sys.argv) < 2:
    print("Usage: python 01_extract_deck.py <source.apkg>")
    sys.exit(1)

apkg = Path(sys.argv[1]).expanduser().resolve()
if not apkg.exists():
    print(f"File not found: {apkg}")
    sys.exit(1)

# Where the rest of the pipeline expects to read from
TMP = Path(os.environ.get("TEMP", "/tmp"))

# Extract the .apkg (it's just a zip)
with tempfile.TemporaryDirectory() as tmpdir:
    with zipfile.ZipFile(apkg) as z:
        z.extractall(tmpdir)

    # Newer Anki uses collection.anki21, older uses collection.anki2
    db_path = Path(tmpdir) / "collection.anki21"
    if not db_path.exists():
        db_path = Path(tmpdir) / "collection.anki2"
    if not db_path.exists():
        raise FileNotFoundError("No collection.anki21 or collection.anki2 inside .apkg")

    db = sqlite3.connect(str(db_path))
    cur = db.cursor()
    cur.execute(
        "SELECT id, flds FROM notes "
        "ORDER BY cast(substr(flds,1,instr(flds,char(31))-1) as int)"
    )
    rows = cur.fetchall()
    db.close()

SEP = "\x1f"
notes, verbs, sent_audio_data = [], [], {}


def safe_fname(note_id: str, slot: str, text: str) -> str:
    slug = re.sub(r"[^\w]", "_", text[:40]).strip("_")
    return f"de_sent_{note_id}_{slot}_{slug}.mp3"


for note_id, flds in rows:
    f = flds.split(SEP)
    nid = str(note_id)

    notes.append({
        "id": note_id,
        "rank": f[0], "word": f[1], "ipa": f[2],
        "pos1": f[3], "def1": f[4], "de1": f[5], "en1": f[6],
        "pos2": f[7], "def2": f[8], "de2": f[9], "en2": f[10],
        "pos3": f[11], "def3": f[12], "de3": f[13], "en3": f[14],
        "freq": f[15] if len(f) > 15 else "",
    })

    # Pre-compute filenames for the sentence audio step
    sent_audio_data[nid] = {}
    for slot, idx in [("s1", 5), ("s2", 9), ("s3", 13)]:
        if len(f) > idx and f[idx].strip():
            sent_audio_data[nid][slot] = safe_fname(nid, slot, f[idx].strip())

    if (
        f[3] in ("verb", "aux")
        or (len(f) > 7 and f[7] in ("verb", "aux"))
        or (len(f) > 11 and f[11] in ("verb", "aux"))
    ):
        inf = f[1].split(",")[0].strip()
        verbs.append({"id": note_id, "word": f[1], "infinitive": inf})

with open(TMP / "deck_notes.json", "w", encoding="utf-8") as fp:
    json.dump(notes, fp, ensure_ascii=False)
with open(TMP / "deck_verbs.json", "w", encoding="utf-8") as fp:
    json.dump(verbs, fp, ensure_ascii=False)
with open(TMP / "sentence_audio.json", "w", encoding="utf-8") as fp:
    json.dump(sent_audio_data, fp, ensure_ascii=False)

print(f"Extracted {len(notes)} notes ({len(verbs)} verbs)")
print(f"Outputs written to {TMP}")
