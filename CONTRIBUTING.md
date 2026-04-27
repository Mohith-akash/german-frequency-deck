# Contributing

Thanks for wanting to improve the deck! Here's how to help.

## Easy contributions (no coding)

### Report a bad image, wrong meaning, or weird audio

Open an [issue](../../issues/new) with:
- The German word
- What's wrong
- Ideally a screenshot

### Replace a specific image

If a noun's image isn't great:

1. Find a better image (must be Creative Commons / public domain — Wikipedia, Openverse, Pixabay, etc.)
2. Save it as `img_de_<noun>.jpg` (e.g. `img_de_zeit.jpg`) — ideally ≤ 300px max dimension, JPG quality 75
3. Open a PR adding it to `media/replacements/` with a one-line note describing the swap

## Medium contributions

### Add B2/C1 vocabulary

The deck currently has 5,009 words covering A1-C1. To extend further:

1. Add new entries to a CSV in the same column structure as the original (`build/data/extra_words.csv`)
2. Run `build/01_extract_deck.py` followed by the rest of the pipeline (see `build/README.md`)
3. PR the result

### Fix a wrong conjugation

Conjugations are derived rule-based from the deck's `Word` field. The full irregular verb table is in [`build/04_generate_conjugations.py`](build/04_generate_conjugations.py) — `IRREGULAR` dictionary.

If a verb is conjugated wrong:
1. Add it to the `IRREGULAR` map with the correct forms
2. Re-run the conjugation generator
3. PR

## Advanced contributions

### Improve the card template / CSS

The Anki add-on at [`addon/german_deck_ultimate/__init__.py`](addon/german_deck_ultimate/__init__.py) contains the card templates and CSS as Python strings. Edit and PR with screenshots of before/after.

### New language pairs

The build pipeline is German-specific in places (Goethe levels, German Wikipedia, KatjaNeural voice). But the architecture is general. If you want to fork it for Spanish/French/etc., the pipeline shape stays the same — swap the data sources.

## Pull request guidelines

- Keep changes focused (one fix per PR is best)
- For data changes, include a sample of the before/after
- For code changes, document any new dependencies in `build/requirements.txt`

## Build the deck from scratch

See [`build/README.md`](build/README.md) for the full reproducible pipeline.
