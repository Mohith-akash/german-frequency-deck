"""Lightly recompress and resize all noun images.
Target: bring images from ~120 MB down to ~50-60 MB while keeping them clear.

- Max dimension 300px (was 400px) — still plenty for card display
- JPG quality 75 (was likely 85-90)
- Strip metadata
"""
import sys, os, glob
from pathlib import Path
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')

MEDIA = Path("C:/Users/Mohith Akash/AppData/Roaming/Anki2/User 1/collection.media")
files = list(MEDIA.glob("img_de_*.jpg"))
print(f"Processing {len(files)} images …")

before = sum(f.stat().st_size for f in files) / 1024 / 1024
saved = 0
errors = 0

for i, f in enumerate(files):
    try:
        img = Image.open(f)
        # Convert to RGB (in case it's RGBA/PNG-disguised-as-jpg)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # Resize: max dimension 300px, keep aspect
        img.thumbnail((300, 300), Image.LANCZOS)
        # Save back as JPG quality 75, no exif
        img.save(f, 'JPEG', quality=75, optimize=True)
        saved += 1
    except Exception as e:
        errors += 1
    if (i+1) % 200 == 0:
        print(f"  {i+1}/{len(files)}", end='\r')

after = sum(f.stat().st_size for f in files) / 1024 / 1024
print(f"\nDone: {saved}/{len(files)} ({errors} errors)")
print(f"Before: {before:.1f} MB")
print(f"After:  {after:.1f} MB")
print(f"Saved:  {before - after:.1f} MB")
