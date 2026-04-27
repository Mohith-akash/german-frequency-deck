# Changelog

## v2.0 — 2026-04 — *Image, conjugation & mobile overhaul*

### Added
- 🖼️ **2,369 noun images** sourced via English-meaning matching (avoids polysemy errors like `Bank` returning a bench when you meant the financial institution)
- 📖 **Verb conjugation tables** for all 1,246 verbs — full present tense (`ich/du/er/wir/ihr/sie`) + Präteritum + Perfekt with correct auxiliary
- 🎯 **Goethe level badge** (A1/A2/B1/B2+) on every card, with manual overrides for the ~80 fundamental grammar words missing from the official lists
- 🔊 **Sentence audio** — TTS for all 5,112 example sentences (was: word audio only)
- 👨‍👩‍👧 **Word family clusters** for 1,790 entries — surfaces related words sharing the same stem
- 🔡 **Bundled Charis SIL font** so IPA renders correctly on AnkiDroid offline (fixes "NO GLYPH" bug)
- 🎨 **Gender colour-coded headers** with German labels (*maskulin / feminin / neutrum*)
- ✂️ **Separable verb prefix highlighted** on the front (e.g. <ins>an</ins>rufen)

### Changed
- 🔄 **Direction flipped to German → English** (was: English → German). Forces active recall; passive recognition was teaching nothing.
- 🎨 **Card design rebuilt from scratch** — clean modern layout, full dark mode, mobile-first sizing
- 📦 **Image optimization** — resized to max 300px, JPG quality 75 → 91 MB saved with no visible quality loss

### Fixed
- 🐛 Image fields now wrapped in `<img>` tags so Anki's media exporter actually includes them in `.apkg` (previously bare filenames were being stripped on export)
- 🐛 Add-on no longer freezes Anki when re-running on already-processed collection
- 🐛 Strong inseparable verbs (`verhalten`, `vergeben`, etc.) now get correct Partizip II
- 🐛 Pronouns and basic determiners (`ein`, `du`, `mir`, `mich`, etc.) correctly tagged A1 (were falling into B2+ due to non-standard format in the source list)

### Stats
| Metric | v1.0 | v2.0 |
|---|---|---|
| Cards | 5,009 | 5,009 |
| Word audio | ✅ 5,009 | ✅ 5,009 |
| Sentence audio | ❌ | ✅ 5,112 |
| Images | ❌ | ✅ 2,369 |
| Conjugations | ❌ | ✅ 1,246 |
| Goethe levels | ❌ | ✅ 5,009 |
| Word families | ❌ | ✅ 1,790 |
| Mobile IPA | broken | ✅ |

---

## v1.0 — 2026-04 — *Initial release*

- 5,009 words sorted by corpus frequency
- KatjaNeural word audio
- Basic German → English template
- Gender colour coding (initial pass)
