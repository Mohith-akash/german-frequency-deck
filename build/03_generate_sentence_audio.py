"""
Generate TTS audio for all example sentences.
Uses de-DE-KatjaNeural for German sentences.
Writes MP3s to Anki media folder.
Saves sentence_audio.json: {note_id: {s1: filename, s2: filename, s3: filename}}
"""
import asyncio, json, sys, re
from pathlib import Path
import edge_tts

sys.stdout.reconfigure(encoding='utf-8')

MEDIA  = Path("C:/Users/Mohith Akash/AppData/Roaming/Anki2/User 1/collection.media")
VOICE  = "de-DE-KatjaNeural"
CONC   = 20
OUTMAP = Path("C:/Users/Mohith Akash/AppData/Local/Temp/sentence_audio.json")

with open("C:/Users/Mohith Akash/AppData/Local/Temp/deck_notes.json", encoding="utf-8") as f:
    notes = json.load(f)

def safe_fname(note_id, slot, text):
    slug = re.sub(r'[^\w]', '_', text[:40]).strip('_')
    return f"de_sent_{note_id}_{slot}_{slug}.mp3"

async def gen_one(sem, text, path):
    if path.exists():
        return True
    async with sem:
        try:
            tts = edge_tts.Communicate(text, voice=VOICE, rate="-5%")
            await tts.save(str(path))
            return True
        except Exception as e:
            print(f"  ⚠ {path.name}: {e}", file=sys.stderr)
            return False

async def main():
    sem = asyncio.Semaphore(CONC)
    tasks, meta = [], {}

    for n in notes:
        nid = str(n['id'])
        meta[nid] = {}
        for slot, key in [('s1','de1'),('s2','de2'),('s3','de3')]:
            txt = n.get(key,'').strip()
            if txt:
                fname = safe_fname(nid, slot, txt)
                meta[nid][slot] = fname
                tasks.append((gen_one(sem, txt, MEDIA/fname), nid, slot))

    total = len(tasks)
    print(f"Generating {total} sentence audio files …")
    coros = [t[0] for t in tasks]
    results = []
    batch = 200
    for i in range(0, total, batch):
        chunk = coros[i:i+batch]
        r = await asyncio.gather(*chunk)
        results.extend(r)
        print(f"  {min(i+batch,total)}/{total} ({sum(results)} ok)", end='\r')

    print(f"\nDone: {sum(results)}/{total}")
    with open(OUTMAP, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False)
    print(f"Saved map → {OUTMAP}")

asyncio.run(main())
