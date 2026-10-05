# Build Pipeline

This directory contains the full reproducible build pipeline for the deck.

## Overview

```
01_extract_deck.py    → deck_notes.json, deck_verbs.json
02_generate_word_audio.py     → MP3 per word
03_generate_sentence_audio.py → MP3 per example sentence
04_generate_conjugations.py   → conjugations.json (1,246 verbs)
05_generate_levels.py         → levels.json (Goethe A1/A2/B1/B2+)
06_generate_word_families.py  → families.json
07_generate_images.py         → image_map.json + JPGs
08_optimize_images.py         → resize/recompress to ≤300px, q=75
09_get_ipa_font.py            → Charis SIL bundled
```

The Anki add-on at [`../addon/german_deck_ultimate/`](../addon/german_deck_ultimate/) reads the JSON files and applies everything to the imported deck.

## Prerequisites

```bash
pip install -r requirements.txt
```

You also need:
- The original deck `.apkg` file (frequency-sorted German, e.g. [Hermit Dave's wordlist](https://github.com/hermitdave/FrequencyWords) repackaged as Anki)
- A working Anki Desktop installation (for the add-on phase)

## Running the pipeline

```bash
# 1. Extract notes from the source .apkg into JSON
python 01_extract_deck.py path/to/source.apkg

# 2. Generate all audio (~3 min, runs concurrently)
python 02_generate_word_audio.py
python 03_generate_sentence_audio.py

# 3. Generate enrichments (no internet for conjugations, internet for the rest)
python 04_generate_conjugations.py
python 05_generate_levels.py     # downloads Goethe word lists
python 06_generate_word_families.py
python 07_generate_images.py     # ~20 min, Wikipedia + Openverse APIs
python 08_optimize_images.py     # ~1 min, local resize

# 4. Bundle the IPA font
python 09_get_ipa_font.py

# 5. Apply everything via the Anki add-on
#    Copy ../addon/german_deck_ultimate/ to your Anki addons21/ folder,
#    open Anki, the add-on auto-runs on collection load
```

## Architecture decisions

### Why rule-based conjugations instead of scraping Wiktionary?

We tried Wiktionary first and got rate-limited at 23/1,246 verbs. Pivoted to deriving conjugations from the deck's own `Word` field which already encodes `infinitive, er-form, präteritum, perfekt`. From those 4 forms, all 6 present tense forms can be derived via rules + a small irregular verb table.

100% coverage in <2 seconds, no API dependencies.

### Why English Wikipedia for images instead of German?

German Wikipedia has lower lead-image coverage for common nouns (only 81/2435 had usable images). English Wikipedia + Openverse-with-English-meaning gave 97% coverage with much better semantic accuracy because the deck's `def1` field is already disambiguated (`Bank` = "bank" or "bench", never both).

### Why bundle the Charis SIL font?

AnkiDroid's default Roboto font lacks IPA glyphs (U+0250-02FF). Without bundling, IPA characters render as "NO GLYPH" boxes on mobile when offline. 130 KB woff2 with `_` filename prefix (so Anki preserves it during media exports) solves this.

### Why a Python add-on instead of editing the SQLite collection directly?

Modern Anki (2.1.50+) stores card templates as protobufs in the database. We *can* manipulate them via direct SQL + manual protobuf encoding (and we do, in earlier prototypes), but the add-on path uses Anki's stable Python API which handles edge cases like media tracking, USN updates, and undo history correctly.

## Reproducing from the original word list

If you want to start from raw frequency data (not an existing `.apkg`):

1. Download word frequencies from [hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords) (German)
2. Add German example sentences (see `tools/build_examples.py` for an LLM-assisted approach)
3. Add IPA via `epitran` or [PHOIBLE](https://phoible.org/)
4. Then run the rest of the pipeline above
