<h1 align="center">German Frequency Deck</h1>

<p align="center">
  <strong>5,009 words · A1 → C1 · the most complete free German Anki deck</strong>
</p>

<p align="center">
  <em>Native neural audio · 2,369 images · Full verb conjugations · Goethe level badges · Word families · Mobile-ready</em>
</p>

<p align="center">
  <img alt="cards" src="https://img.shields.io/badge/cards-5%2C009-1565c0">
  <img alt="audio" src="https://img.shields.io/badge/audio_files-10%2C121-2e7d32">
  <img alt="images" src="https://img.shields.io/badge/images-2%2C369-e65100">
  <img alt="conjugations" src="https://img.shields.io/badge/verb_conjugations-1%2C246-6a1b9a">
  <img alt="size" src="https://img.shields.io/badge/.apkg-162_MB-555555">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-blueviolet">
</p>

<p align="center">
  <a href="#-download">Download</a> ·
  <a href="#-whats-inside">Features</a> ·
  <a href="#-card-examples">Cards</a> ·
  <a href="#-study-strategy">Study</a> ·
  <a href="#%EF%B8%8F-how-its-built">How it's built</a> ·
  <a href="#-contributing">Contribute</a>
</p>

---

## 📥 Download

Get the latest `.apkg` from the **[Releases page](../../releases/latest)**, then in Anki: **File → Import**.

> Works on **Anki desktop** (Windows/macOS/Linux), **AnkiDroid** (Android), and **AnkiMobile** (iOS).

---

## ✨ What's inside

| Feature | Detail |
|---|---|
| 🔊 **Word audio** | Microsoft KatjaNeural TTS — every one of 5,009 words |
| 🔊 **Sentence audio** | All 5,112 example sentences spoken naturally — train your listening |
| 🖼️ **Images** | 2,369 nouns visualised (English-meaning matched to disambiguate `Bank`/`bench` etc.) |
| 📖 **Verb conjugations** | All 1,246 verbs with full present tense, Präteritum and Perfekt — separable prefixes underlined |
| 🎯 **Goethe level badges** | Every card tagged A1 / A2 / B1 / B2+ |
| 👨‍👩‍👧 **Word families** | 1,790 cards show related words (e.g. `arbeiten` → die Arbeit, der Arbeiter, arbeitslos) |
| 🎨 **Gender colours** | `der` blue · `die` red · `das` green — both in headers and example borders |
| 📝 **IPA pronunciation** | Bundled Charis SIL font ensures it renders correctly on every device, even offline AnkiDroid |
| 🌗 **Dark mode** | Full first-class dark mode support |
| 📊 **Frequency rank** | Every card shows its corpus frequency (#1 = most common) |
| 🔄 **German → English** | Active recall direction (forces real retrieval, not passive recognition) |

---

## 📸 Card examples

### Front (the prompt)

```
                                   [A1]                  ← Goethe level
        
                  der — maskulin                          ← gender label
        
                     der Hund                             ← word (color = gender)
                       Pl. -e                             ← plural form
                       [hʊnt]                             ← IPA (Charis SIL)
                          ▶                               ← audio auto-plays

                  WAS BEDEUTET DAS?                       ← prompt
```

### Back (the reveal)

```
                ┌──────────────────────┐
                │                      │
                │     [photo of a      │   ← image (nouns only)
                │       dog]           │
                │                      │
                └──────────────────────┘

                NOUN     dog
                ┌────────────────────────────────┐
                │ ▶  Mein Hund ist mein bester   │   ← German example +
                │    Freund.                     │     sentence audio
                │    My dog is my best friend.   │   ← English translation
                └────────────────────────────────┘

                ┌─── Konjugation (verbs only) ──────────┐
                │ ich     bringe   │ wir    bringen     │
                │ du      bringst  │ ihr    bringt      │
                │ er/sie  bringt   │ sie    bringen     │
                │                                       │
                │ Prät. ich brachte │ Perf. habe gebracht│
                └───────────────────────────────────────┘

                ┌─── Wortfamilie ─────────────────────┐
                │ die Arbeit · der Arbeiter · arbeitslos │
                └─────────────────────────────────────┘

                       #287 most frequent
```

---

## 📚 Study strategy

The deck is **sorted by real-world frequency** (corpus-based). The Goethe levels are layered on top, so you can study sequentially:

| Cards | Goethe Level | What it unlocks |
|---|---|---|
| **1 → 615** | A1 | Survive in Germany (greetings, numbers, basic food/transport) |
| **616 → 1,061** | A2 | Manage daily life (shopping, simple opinions, past tense) |
| **1,062 → 2,176** | B1 | **Pass the Goethe-Zertifikat B1 exam** — the bar for the [German Blue Card](https://www.bluecard-eu.de/) |
| **2,177 → 5,009** | B2 / C1 | Read newspapers, watch TV without subtitles, professional fluency |

Recommended pace: **20 new cards/day**. You'll hit B1 in ~3 months and full deck in ~9 months.

---

## 🛠️ How it's built

This isn't a hand-crafted deck. Every enrichment was generated programmatically from the original frequency word list. The pipeline:

```
                ┌─────────────────────────────────────┐
                │   ORIGINAL: 5,009 frequency words   │
                │   (Hermit Dave / OpenSubtitles)     │
                └─────────────────┬───────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
   ┌─────────┐             ┌─────────────┐           ┌────────────┐
   │  AUDIO  │             │   IMAGES    │           │  GRAMMAR   │
   ├─────────┤             ├─────────────┤           ├────────────┤
   │ edge-tts│             │  Wikipedia  │           │ Rule-based │
   │ Katja   │             │ (English)   │           │ derivation │
   │ Neural  │             │ + Openverse │           │ from deck  │
   └────┬────┘             │ + Wikimedia │           │ data       │
        │                  │ Commons     │           └─────┬──────┘
        │                  └──────┬──────┘                 │
        │                         │                        ▼
        │                         │                 ┌────────────┐
        │                         │                 │  LEVELS    │
        │                         │                 ├────────────┤
        │                         │                 │ Goethe A1  │
        │                         │                 │ A2/B1 lists│
        │                         │                 │ + manual   │
        │                         │                 │ overrides  │
        │                         │                 └─────┬──────┘
        ▼                         ▼                       ▼
   10,121 MP3s              2,369 JPGs              1,246 conj
   (5009 words +            (resized 300px,         tables +
    5112 sentences)          quality 75)             5009 levels
        │                         │                       │
        └─────────────────────────┴─────────────────────────┘
                                  │
                                  ▼
                ┌─────────────────────────────────────┐
                │  Anki add-on injects everything     │
                │  into notes via the Python API:     │
                │  fields, templates, CSS, audio refs │
                └─────────────────────────────────────┘
                                  │
                                  ▼
                          ✨ Final deck (162 MB)
```

See **[`build/README.md`](build/README.md)** for full reproducibility — every script is included.

### Technical highlights

- **Concurrent TTS generation**: 5112 sentences via `edge-tts` + `asyncio` semaphore (15 workers) — full audio set built in ~3 minutes
- **Hybrid image source**: Tried German Wikipedia first → fell back to Openverse with the *English* meaning to avoid polysemy errors (`Bank` could mean bank OR bench — using `def1=bank` returns the right image)
- **Direct protobuf manipulation**: Anki 2.1.50+ stores card templates as protobufs in the SQLite DB. Built a manual encoder/decoder rather than ship the heavy `google.protobuf` dependency
- **Conjugation derivation**: Avoided rate-limited Wiktionary scraping by parsing conjugations directly from the deck's own `Word` field (`"fahren, fährt, fuhr, ist gefahren"` → 6 present tense forms via rules + irregular verb table)
- **Bundled IPA font**: Charis SIL `.woff2` (130 KB) with `_` prefix so Anki preserves it during media checks — fixes "NO GLYPH" rendering on AnkiDroid

---

## 🆚 Why this deck vs others

| Other "5000 German Words" decks | This deck |
|---|---|
| English → German (passive recognition) | **German → English** (active recall) |
| Audio for words only, or none | **Audio for words AND every example sentence** |
| Plain text on cards | **Gender colour coding, level badges, IPA, plural** |
| No conjugations | **Full conjugation table for all 1,246 verbs** |
| No images, or random ones | **2,369 images sourced from English meaning to avoid wrong matches** |
| Broken on mobile (IPA "NO GLYPH") | **Bundled font, works offline on every device** |

---

## 🤝 Contributing

Found a wrong image? A conjugation mistake? Want to add B2 vocabulary?

1. Open an **[issue](../../issues)** describing the change
2. Or fork → fix → PR — for image swaps you can drop replacement files in `media/` and update `image_map.json`

The whole build pipeline is reproducible from `build/` so anyone can regenerate the deck from scratch.

---

## 📜 License & credits

- **Deck content (this version)**: [MIT](LICENSE) — free to use, modify, redistribute
- **Original word list**: frequency-sorted German lemmas from OpenSubtitles via Hermit Dave (CC-BY-SA)
- **Audio**: Microsoft Edge neural TTS (KatjaNeural — German, female, natural)
- **Images**: Wikipedia / Wikimedia Commons / Openverse (all CC-licensed)
- **IPA font**: [Charis SIL](https://software.sil.org/charis/) by SIL International (free for any use)
- **Goethe word lists**: [ilkermeliksitki/goethe-institute-wordlist](https://github.com/ilkermeliksitki/goethe-institute-wordlist) (parsed from official Goethe Institut PDFs)

---

<p align="center">
  <em>Built by a learner, for learners. <strong>Viel Erfolg beim Lernen 🇩🇪</strong></em>
</p>
