# Architecture

How the deck is built end-to-end.

## Data flow

```
                  ┌────────────────────────────────┐
                  │   source.apkg (5,009 notes)    │
                  │   - rank, word, IPA            │
                  │   - 3 meanings × {pos, def,    │
                  │     German example, English}   │
                  └───────────────┬────────────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │ 01_extract_deck.py   │
                       └──────────┬───────────┘
                                  │
                ┌─────────────────┴─────────────────┐
                │                                   │
                ▼                                   ▼
        deck_notes.json                     deck_verbs.json
        (5,009 entries)                     (1,246 entries)
                │                                   │
    ┌───────────┼─────────────┬──────────┐          │
    ▼           ▼             ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐
│  step   │ │  step   │ │  step    │ │  step  │ │  step 04:    │
│  02:    │ │  03:    │ │  05:     │ │  06:   │ │  conjugate   │
│ word    │ │ sentence│ │ levels   │ │ family │ │  verbs       │
│ audio   │ │ audio   │ │          │ │        │ │              │
│         │ │         │ │ Goethe   │ │ shared │ │ rule-based   │
│ edge-tts│ │ edge-tts│ │ A1/A2/B1 │ │ stems  │ │ from deck    │
│ Katja   │ │ Katja   │ │ + manual │ │        │ │ field        │
└────┬────┘ └────┬────┘ └────┬─────┘ └───┬────┘ └──────┬───────┘
     │           │           │           │             │
     ▼           ▼           ▼           ▼             ▼
   5,009       5,112      levels    families   conjugations
   word       sentence    .json      .json         .json
   MP3s        MP3s
                                    
                       (filter: nouns only)
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │ 07_generate_images   │
                       │                      │
                       │ 1. EN Wikipedia      │
                       │ 2. DE Wikipedia      │
                       │ 3. Openverse (en)    │
                       │ 4. Openverse (de)    │
                       └──────────┬───────────┘
                                  │
                                  ▼
                              2,369 JPGs
                                  │
                       ┌──────────▼───────────┐
                       │ 08_optimize_images   │
                       │ resize 300px, q=75   │
                       └──────────┬───────────┘
                                  │
                                  ▼
                              ~28 MB
                                  
                       ┌──────────────────────┐
                       │ 09_get_ipa_font      │
                       │ Charis SIL .woff2    │
                       └──────────────────────┘
                                  
                                  │
                                  ▼ (all artifacts in TEMP + media folder)
                       ┌──────────────────────┐
                       │ Anki Add-on          │
                       │                      │
                       │ - reads JSONs        │
                       │ - adds 7 fields      │
                       │ - rewrites template  │
                       │ - rewrites CSS       │
                       │ - populates notes    │
                       └──────────┬───────────┘
                                  │
                                  ▼
                          ✨ Final deck (162 MB)
```

## Why these choices

### Audio: edge-tts

- **Free & no API key** required
- **Microsoft KatjaNeural voice** is genuinely natural-sounding German
- Concurrency: `asyncio.Semaphore(15)` keeps it fast (~3 min for 5k+ files) without triggering rate limits

### Conjugations: rule-based, not Wiktionary

Wiktionary scraping hit 429 rate limits at 23/1,246. Pivoted to deriving from the deck's own `Word` field which encodes `infinitive, er-form, präteritum, perfekt`:

```python
"fahren, fährt, fuhr, ist gefahren"
                    ↓
ich fahre · du fährst · er fährt · wir fahren · ihr fährt · sie fahren
                    ↓
Prät: ich fuhr · Perf: ist gefahren
```

The `IRREGULAR` table handles ~20 verbs (sein, haben, modals, strong inseparables) where rules don't apply.

100% coverage in <2 seconds, no network needed.

### Images: English meaning, not German word

German Wikipedia: only 81/2435 nouns had usable lead images.

Switched to **English Wikipedia + Openverse-with-English-meaning**. The deck's `def1` field is already disambiguated:

| Word | def1 | Search query | Result |
|---|---|---|---|
| die Bank | "bank" | "bank" | financial bank ✅ |
| die Bank | "bench" | "bench" | bench ✅ |
| das Schloss | "castle" | "castle" | castle ✅ |
| das Schloss | "lock" | "lock" | padlock ✅ |

Coverage went from 80% (German query) to 97% (English query) AND accuracy improved dramatically.

### Goethe levels: list + manual fallback

Source: [ilkermeliksitki/goethe-institute-wordlist](https://github.com/ilkermeliksitki/goethe-institute-wordlist) (TSVs parsed from official Goethe PDFs).

The lists have inconsistent formatting:
- `ein-(1)` (trailing dash + sense number)
- `ihr/ihm/ihn(1)` (slash-separated pronoun cases)
- `andere (r, s)` (inflection markers in parens)

Plus some basic words just aren't in the official lists (`du`, `mir`, `mich`). Added a manual override list of ~80 fundamental grammar words that are unambiguously A1.

### IPA font: bundle Charis SIL

AnkiDroid's default Roboto lacks IPA Extensions (U+0250-02FF). Without bundling, AnkiDroid renders `[ˈanˌruːfn̩]` as "[NO GLYPH]" boxes when offline.

Charis SIL (130 KB woff2) is specifically designed for phonetic transcription and covers every IPA character we need. The `_charis.woff2` filename uses the underscore prefix so Anki preserves it during media checks/exports.

### Add-on, not direct DB writes

Modern Anki (2.1.50+) stores card templates as **protobuf** in SQLite. We *can* manipulate them via direct SQL + manual protobuf encoding (and we did, in earlier prototypes). But the add-on path uses Anki's stable Python API which handles edge cases:

- Media usage tracking (so files don't get marked unused)
- USN updates (so sync works correctly)
- Undo history
- Notetype schema validation

The add-on is also user-friendly: drop in folder, open Anki, done.
