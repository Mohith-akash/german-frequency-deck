# Anki Add-on

This is the add-on that injects all enrichments (audio, images, conjugations, levels, families, IPA font) into the Anki notes after import.

## Install

1. Quit Anki if it's open
2. Copy the entire `german_deck_ultimate/` folder into your Anki add-ons directory:
   - **Windows:** `%APPDATA%\Anki2\addons21\`
   - **macOS:** `~/Library/Application Support/Anki2/addons21/`
   - **Linux:** `~/.local/share/Anki2/addons21/`
3. Make sure all the JSON data files (`levels.json`, `conjugations.json`, `sentence_audio.json`, `families.json`, `image_map.json`) are in your system **TEMP** directory (the build pipeline writes them there)
4. Open Anki — the add-on auto-runs on collection load
5. Wait ~1-2 minutes for the progress bar
6. After the success popup, you can disable or delete the add-on (it's one-shot)

## What it does

1. Adds 7 new fields to the `English-Deutsch+` notetype: `Level`, `WordFamily`, `Conjugation`, `SentenceAudio1/2/3`, `Image`
2. Replaces the card templates (front + back) with the redesigned versions
3. Replaces the CSS with the new design (gender colours, dark mode, mobile-friendly)
4. Iterates all 5,009 notes and populates the new fields from the pre-generated JSON files
5. Sets a config flag so subsequent Anki launches don't re-run the work

## How it knows it's already done

Reads `col.get_config("german_deck_ultimate_v5")`. If `True`, skips silently with no UI.

If you're iterating on the add-on during development, change `DONE_FLAG` to a new version string to force re-run.
