"""
German Anki Deck Enhancer
Improvements:
  1. Neural German TTS audio (Microsoft KatjaNeural) for every word
  2. Improved card template — back now shows English translations of German examples
  3. Gender-color-coded words (der=blue, die=red, das=green)
  4. Fixed CSS (.spanish → .german), better typography & layout
  5. Audio auto-plays on card flip
"""

import asyncio
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import zipfile
from pathlib import Path

import edge_tts

# ── Paths ──────────────────────────────────────────────────────────────────────
APKG_IN  = Path("D:/Downloads/English-German_Sorted_by_Frequency.apkg")
APKG_OUT = Path("D:/Downloads/English-German_Improved.apkg")
ANKI_MEDIA = Path("C:/Users/Mohith Akash/AppData/Roaming/Anki2/User 1/collection.media")

VOICE = "de-DE-KatjaNeural"   # warm, natural female German
CONCURRENCY = 15              # parallel TTS requests

# ── Card templates ─────────────────────────────────────────────────────────────
FRONT_TEMPLATE = """\
<div id="front-side">
{{#Part-of-Speech 1}}
<ul>
  <li>
    <span class="pos">{{Part-of-Speech 1}}</span>
    <span class="definition">{{Definition 1}}</span>
    {{#English 1}}<div class="eng-example">{{English 1}}</div>{{/English 1}}
  </li>
  {{#Part-of-Speech 2}}
  <li>
    <span class="pos">{{Part-of-Speech 2}}</span>
    <span class="definition">{{Definition 2}}</span>
    {{#English 2}}<div class="eng-example">{{English 2}}</div>{{/English 2}}
  </li>
  {{/Part-of-Speech 2}}
  {{#Part-of-Speech 3}}
  <li>
    <span class="pos">{{Part-of-Speech 3}}</span>
    <span class="definition">{{Definition 3}}</span>
    {{#English 3}}<div class="eng-example">{{English 3}}</div>{{/English 3}}
  </li>
  {{/Part-of-Speech 3}}
</ul>
{{/Part-of-Speech 1}}
</div>

<script>
(function(){
  var articles = ['der','die','das','der, die','die (pl)','der, das','die, das','der, die, das','das, die (pl)','(pl)','der, das, die'];
  var posEls = document.querySelectorAll('#front-side .pos');
  posEls.forEach(function(el){
    if(articles.indexOf(el.textContent.trim()) !== -1){
      el.textContent = 'noun';
    }
  });
})();
</script>
"""

BACK_TEMPLATE = """\
{{FrontSide}}

<hr id="answer">

<div id="back-main">
  <div class="word-block">
    <span class="word" id="word-display">{{Word}}</span>
    <span class="ipa">[{{IPA}}]</span>
  </div>

  {{#Audio}}<div class="audio-wrap">{{Audio}}</div>{{/Audio}}

  <ul class="meanings">
    {{#Part-of-Speech 1}}
    <li class="meaning-item">
      <div class="meaning-header">
        <span class="pos-back">{{Part-of-Speech 1}}</span>
        <span class="def-back">{{Definition 1}}</span>
      </div>
      {{#German 1}}<div class="de-sentence">{{German 1}}</div>{{/German 1}}
      {{#English 1}}<div class="en-translation">{{English 1}}</div>{{/English 1}}
    </li>
    {{/Part-of-Speech 1}}
    {{#Part-of-Speech 2}}
    <li class="meaning-item">
      <div class="meaning-header">
        <span class="pos-back">{{Part-of-Speech 2}}</span>
        <span class="def-back">{{Definition 2}}</span>
      </div>
      {{#German 2}}<div class="de-sentence">{{German 2}}</div>{{/German 2}}
      {{#English 2}}<div class="en-translation">{{English 2}}</div>{{/English 2}}
    </li>
    {{/Part-of-Speech 2}}
    {{#Part-of-Speech 3}}
    <li class="meaning-item">
      <div class="meaning-header">
        <span class="pos-back">{{Part-of-Speech 3}}</span>
        <span class="def-back">{{Definition 3}}</span>
      </div>
      {{#German 3}}<div class="de-sentence">{{German 3}}</div>{{/German 3}}
      {{#English 3}}<div class="en-translation">{{English 3}}</div>{{/English 3}}
    </li>
    {{/Part-of-Speech 3}}
  </ul>

  <div class="rank-badge">#{{Rank}}</div>
</div>

<script>
(function(){
  var word = document.getElementById('word-display');
  if(!word) return;
  var pos1 = '{{Part-of-Speech 1}}'.trim();
  if(pos1 === 'der' || pos1 === 'der, die' || pos1 === 'der, das' || pos1 === 'der, die, das') {
    word.classList.add('gender-der');
  } else if(pos1 === 'die' || pos1 === 'die (pl)' || pos1 === 'die, das' || pos1 === 'das, die (pl)') {
    word.classList.add('gender-die');
  } else if(pos1 === 'das') {
    word.classList.add('gender-das');
  }
})();
</script>
"""

CARD_CSS = """\
/* ── Base ─────────────────────────────── */
.card {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
  font-size: 18px;
  text-align: center;
  color: #1a1a1a;
  background-color: #fafafa;
  padding: 12px 8px;
  line-height: 1.5;
}

/* ── Front ────────────────────────────── */
#front-side ul {
  display: inline-block;
  text-align: left;
  list-style: none;
  padding: 0;
  margin: 8px 0;
  max-width: 480px;
}

#front-side li {
  margin-bottom: 10px;
}

.pos {
  font-size: 13px;
  font-style: italic;
  color: #888;
  margin-right: 5px;
}

.definition {
  font-weight: 700;
  color: #1a1a1a;
}

.eng-example {
  font-size: 15px;
  color: #555;
  margin-top: 2px;
  margin-left: 4px;
}

hr#answer {
  margin: 14px auto;
  border: none;
  border-top: 1px solid #ddd;
  max-width: 400px;
}

/* ── Back ─────────────────────────────── */
#back-main {
  padding: 4px 0;
}

.word-block {
  margin-bottom: 6px;
}

.word {
  font-size: 30px;
  font-weight: 800;
  color: #0193c4;        /* default (non-noun) */
  display: block;
  margin-bottom: 2px;
}

/* Gender colours */
.word.gender-der { color: #1565c0; }   /* der → blue */
.word.gender-die { color: #c62828; }   /* die → red  */
.word.gender-das { color: #2e7d32; }   /* das → green */

.ipa {
  font-size: 15px;
  color: #888;
  font-style: italic;
}

/* Audio button */
.audio-wrap {
  margin: 6px 0 10px;
}

/* Meanings list */
.meanings {
  display: inline-block;
  text-align: left;
  list-style: none;
  padding: 0;
  margin: 8px auto;
  max-width: 500px;
}

.meaning-item {
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #e0e0e0;
}

.meaning-item:last-child {
  border-bottom: none;
}

.meaning-header {
  margin-bottom: 4px;
}

.pos-back {
  font-size: 13px;
  font-style: italic;
  color: #999;
  margin-right: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  padding: 1px 5px;
}

.def-back {
  font-weight: 700;
  font-size: 17px;
}

/* German example sentence */
.de-sentence {
  font-size: 15px;
  color: #222;
  margin-top: 4px;
  padding-left: 10px;
  border-left: 3px solid #0193c4;
  line-height: 1.4;
}

/* English translation of the sentence */
.en-translation {
  font-size: 14px;
  color: #777;
  padding-left: 10px;
  margin-top: 2px;
  font-style: italic;
  line-height: 1.4;
}

/* Rank badge */
.rank-badge {
  margin-top: 14px;
  font-size: 12px;
  color: #bbb;
  letter-spacing: 0.5px;
}
"""

# ── Helpers ────────────────────────────────────────────────────────────────────

def tts_text(word: str) -> str:
    """Return the text to synthesise — strip plural/conjugation info after first comma."""
    # e.g. "das Jahr, -e" → "das Jahr"
    #      "sein, ist, war, ist gewesen" → "sein"
    #      "in" → "in"
    text = word.split(",")[0].strip()
    return text or word


async def generate_one(sem: asyncio.Semaphore, word: str, out_path: Path) -> bool:
    """Generate one TTS file; returns True on success."""
    if out_path.exists():
        return True
    text = tts_text(word)
    async with sem:
        try:
            tts = edge_tts.Communicate(text, voice=VOICE, rate="-5%")
            await tts.save(str(out_path))
            return True
        except Exception as e:
            print(f"  ⚠  TTS failed for '{word}': {e}", file=sys.stderr)
            return False


async def generate_all_audio(words: list[tuple[int, str]], media_dir: Path) -> dict[int, str]:
    """Generate audio for all words concurrently. Returns {note_id: filename}."""
    sem = asyncio.Semaphore(CONCURRENCY)
    id_to_file: dict[int, str] = {}
    tasks = []

    for note_id, word in words:
        safe = re.sub(r'[\\/:*?"<>|]', '_', word[:60])
        fname = f"de_{safe}.mp3"
        out   = media_dir / fname
        id_to_file[note_id] = fname
        tasks.append(generate_one(sem, word, out))

    total = len(tasks)
    print(f"Generating audio for {total} words using {VOICE} …")

    results = []
    batch = 100
    for i in range(0, total, batch):
        chunk = tasks[i:i+batch]
        r = await asyncio.gather(*chunk)
        results.extend(r)
        done = min(i + batch, total)
        ok   = sum(results)
        print(f"  {done}/{total}  ({ok} ok)", end="\r")

    print(f"\nAudio done: {sum(results)}/{total} files generated.")
    return id_to_file


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    sys.stdout.reconfigure(encoding="utf-8")

    # 1. Extract .apkg to temp dir
    tmpdir = Path(tempfile.mkdtemp(prefix="anki_improve_"))
    print(f"Working in {tmpdir}")
    with zipfile.ZipFile(APKG_IN) as z:
        z.extractall(tmpdir)

    # Parse media manifest (maps index → filename inside zip)
    media_manifest: dict[str, str] = {}
    media_json = tmpdir / "media"
    if media_json.exists():
        with open(media_json, encoding="utf-8") as f:
            media_manifest = json.load(f)

    # 2. Open DB
    db_path = tmpdir / "collection.anki21"
    db = sqlite3.connect(str(db_path))
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # 3. Read model and update it
    cur.execute("SELECT models FROM col")
    models: dict = json.loads(cur.fetchone()["models"])

    for mid, model in models.items():
        field_names = [f["name"] for f in model["flds"]]

        # Add "Audio" field if missing
        if "Audio" not in field_names:
            new_ord = max(f["ord"] for f in model["flds"]) + 1
            audio_fld = {
                "name": "Audio",
                "ord": new_ord,
                "sticky": False,
                "rtl": False,
                "font": "Arial",
                "size": 20,
                "media": [],
            }
            model["flds"].append(audio_fld)
            print(f"Added 'Audio' field to model '{model['name']}'")

        # Update templates
        for tmpl in model["tmpls"]:
            tmpl["qfmt"] = FRONT_TEMPLATE
            tmpl["afmt"] = BACK_TEMPLATE

        # Update CSS
        model["css"] = CARD_CSS

    cur.execute("UPDATE col SET models = ?", (json.dumps(models),))
    print("Updated card templates and CSS.")

    # 4. Read all notes
    cur.execute("SELECT id, flds FROM notes")
    rows = cur.fetchall()
    print(f"Found {len(rows)} notes.")

    # Build word list for TTS
    FIELD_SEP = "\x1f"
    word_list: list[tuple[int, str]] = []
    for row in rows:
        fields = row["flds"].split(FIELD_SEP)
        # Word is index 1
        word = fields[1] if len(fields) > 1 else ""
        if word:
            word_list.append((row["id"], word))

    # 5. Generate audio
    audio_map = asyncio.run(generate_all_audio(word_list, ANKI_MEDIA))
    print(f"Audio files written to: {ANKI_MEDIA}")

    # 6. Update note fields — append Audio field
    updated = 0
    for row in rows:
        note_id = row["id"]
        fields  = row["flds"].split(FIELD_SEP)

        # Ensure 17 fields (Rank..Frequency + Audio)
        while len(fields) < 16:
            fields.append("")

        audio_ref = ""
        if note_id in audio_map:
            audio_ref = f"[sound:{audio_map[note_id]}]"

        if len(fields) == 16:
            fields.append(audio_ref)
        else:
            fields[16] = audio_ref

        cur.execute(
            "UPDATE notes SET flds = ? WHERE id = ?",
            (FIELD_SEP.join(fields), note_id),
        )
        updated += 1

    db.commit()
    print(f"Updated {updated} notes with audio references.")

    # 7. Copy existing media files from apkg into ANKI_MEDIA
    for idx, fname in media_manifest.items():
        src = tmpdir / idx
        dst = ANKI_MEDIA / fname
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)

    # 8. Pack new .apkg
    print(f"Packing new .apkg → {APKG_OUT} …")
    # Copy audio files we generated back into the package
    # Build new media manifest
    new_media: dict[str, str] = {}
    idx = 0
    pack_tmp = Path(tempfile.mkdtemp(prefix="anki_pack_"))

    # Include original media
    for orig_idx, fname in media_manifest.items():
        src = tmpdir / orig_idx
        if src.exists():
            dst_name = str(idx)
            shutil.copy2(src, pack_tmp / dst_name)
            new_media[dst_name] = fname
            idx += 1

    # Include generated audio
    for note_id, fname in audio_map.items():
        src = ANKI_MEDIA / fname
        if src.exists():
            dst_name = str(idx)
            shutil.copy2(src, pack_tmp / dst_name)
            new_media[dst_name] = fname
            idx += 1

    with open(pack_tmp / "media", "w", encoding="utf-8") as f:
        json.dump(new_media, f)

    # Copy DB
    shutil.copy2(db_path, pack_tmp / "collection.anki21")
    # Copy anki2 for compatibility
    anki2 = tmpdir / "collection.anki2"
    if anki2.exists():
        shutil.copy2(anki2, pack_tmp / "collection.anki2")
    # meta
    meta = tmpdir / "meta"
    if meta.exists():
        shutil.copy2(meta, pack_tmp / "meta")

    APKG_OUT.unlink(missing_ok=True)
    with zipfile.ZipFile(APKG_OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for f in pack_tmp.iterdir():
            zout.write(f, f.name)

    db.close()
    size_mb = APKG_OUT.stat().st_size / 1024 / 1024
    print(f"\n✓ Done! Improved deck saved to:")
    print(f"  {APKG_OUT}  ({size_mb:.1f} MB)")
    print("\nImport steps:")
    print("  1. Close Anki completely (important — DB is locked while open)")
    print("  2. Double-click the .apkg file — Anki will open and import it")
    print("  3. When prompted about existing deck, choose 'Update existing notes'")
    print("  4. Your review history will be preserved!")


if __name__ == "__main__":
    main()
