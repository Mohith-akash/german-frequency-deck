"""
German Deck Ultimate Enhancer — One-shot Anki add-on
Applies ALL improvements to the English-Deutsch+ notetype:

  1. German → English card direction
  2. Goethe level badge (A1 / A2 / B1 / B2+)
  3. Verb conjugation table (Präsens + Perfekt for all 1246 verbs)
  4. Sentence audio auto-play on back card
  5. Separable verb prefix highlighted on the word header
  6. Word family cluster shown on back
  7. Gender colour-coding (der/die/das)
  8. Full dark-mode support
  9. Frequency rank badge
"""

import json
import os
from pathlib import Path
from aqt import mw, gui_hooks
from aqt.utils import showInfo

NOTETYPE_NAME = "English-Deutsch+"
DONE_FLAG     = "german_deck_ultimate_v6"
DATA_DIR      = Path(os.environ.get("TEMP", "/tmp"))

# ── Load pre-generated data ────────────────────────────────────────────────────

def load_json(name):
    p = DATA_DIR / name
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}

# ── Card templates ─────────────────────────────────────────────────────────────

FRONT = r"""
<div class="front-wrap">

  <div class="word-header" id="word-header">
    <div class="level-badge" id="level-badge">{{Level}}</div>
    <div class="gender-badge" id="gender-badge"></div>
    <div class="word-main" id="word-main">{{Word}}</div>
    <div class="word-plural" id="word-plural"></div>
    <div class="ipa-line">[{{IPA}}]</div>
  </div>

  {{#WordAudio}}<div class="audio-row">{{WordAudio}}</div>{{/WordAudio}}

  <div class="prompt-hint">Was bedeutet das?</div>

</div>

<script>
(function(){
  var pos1   = '{{Part-of-Speech 1}}'.trim();
  var header = document.getElementById('word-header');
  var badge  = document.getElementById('gender-badge');
  var wordEl = document.getElementById('word-main');
  var plurEl = document.getElementById('word-plural');

  // Gender detection
  var gender = null;
  if(pos1==='der'||pos1==='der, die'||pos1==='der, das') gender='der';
  else if(pos1==='die'||pos1==='die (pl)'||pos1==='die, das'||pos1==='(pl)') gender='die';
  else if(pos1==='das'||pos1==='das, die (pl)') gender='das';
  else if(pos1==='der, die, das') gender='mixed';

  if(gender){
    header.classList.add('gender-'+gender);
    var lbl={der:'der \u2014 maskulin',die:'die \u2014 feminin',das:'das \u2014 neutrum',mixed:'mixed'};
    badge.textContent = lbl[gender]||pos1;
    // Split "das Jahr, -e" → word + plural
    var raw=wordEl.textContent.trim(), ci=raw.indexOf(',');
    if(ci!==-1){
      wordEl.textContent = raw.slice(0,ci).trim();
      plurEl.textContent = 'Pl. '+raw.slice(ci+1).trim();
    }
  } else {
    badge.style.display='none';
    plurEl.style.display='none';
  }

  // Level badge colour
  var lvl = '{{Level}}'.trim();
  var lb = document.getElementById('level-badge');
  if(lb){
    if(lvl){ lb.classList.add('lvl-'+lvl.replace('+','plus')); }
    else { lb.style.display='none'; }
  }

  // Highlight separable prefix in the word display
  // e.g. "anrufen" → "<span class='sep-prefix'>an</span>rufen"
  var sepPrefixes = ['ab','an','auf','aus','bei','ein','fort','her','hin','los',
    'mit','nach','nieder','vor','weg','weiter','zu','zurück','zusammen',
    'durch','über','um','unter','wieder','zwischen','dar','empor','entgegen',
    'gegenüber','hinter','vorbei','vorüber','heran','herauf','heraus',
    'herein','herüber','herum','herunter','hervor','hinauf','hinaus',
    'hinein','hinüber','hinunter','hinweg'];
  var wText = wordEl.textContent.trim();
  var matched = false;
  for(var pi=0; pi<sepPrefixes.length && !matched; pi++){
    var pfx = sepPrefixes[pi];
    if(wText.toLowerCase().startsWith(pfx) && wText.length > pfx.length + 3){
      wordEl.innerHTML = '<u class="sep-prefix">'+wText.slice(0,pfx.length)+'</u>'+wText.slice(pfx.length);
      matched = true;
    }
  }
})();
</script>
"""

BACK = r"""
{{FrontSide}}

<div class="answer-divider"></div>

<div class="back-wrap">

  <!-- Image (nouns only) — Image field already contains full <img> tag -->
  {{#Image}}
  <div class="image-wrap">{{Image}}</div>
  {{/Image}}

  <!-- Meanings -->
  <div class="meanings-wrap">

    {{#Definition 1}}
    <div class="meaning-block" id="m1">
      <div class="meaning-head">
        <span class="pos-tag" id="pos1-tag">{{Part-of-Speech 1}}</span>
        <span class="meaning-def">{{Definition 1}}</span>
      </div>
      {{#German 1}}
      <div class="example-wrap">
        {{#SentenceAudio1}}<span class="sent-audio">{{SentenceAudio1}}</span>{{/SentenceAudio1}}
        <div class="de-sent">{{German 1}}</div>
        {{#English 1}}<div class="en-sent">{{English 1}}</div>{{/English 1}}
      </div>
      {{/German 1}}
    </div>
    {{/Definition 1}}

    {{#Definition 2}}
    <div class="meaning-block">
      <div class="meaning-head">
        <span class="pos-tag">{{Part-of-Speech 2}}</span>
        <span class="meaning-def">{{Definition 2}}</span>
      </div>
      {{#German 2}}
      <div class="example-wrap">
        {{#SentenceAudio2}}<span class="sent-audio">{{SentenceAudio2}}</span>{{/SentenceAudio2}}
        <div class="de-sent">{{German 2}}</div>
        {{#English 2}}<div class="en-sent">{{English 2}}</div>{{/English 2}}
      </div>
      {{/German 2}}
    </div>
    {{/Definition 2}}

    {{#Definition 3}}
    <div class="meaning-block">
      <div class="meaning-head">
        <span class="pos-tag">{{Part-of-Speech 3}}</span>
        <span class="meaning-def">{{Definition 3}}</span>
      </div>
      {{#German 3}}
      <div class="example-wrap">
        {{#SentenceAudio3}}<span class="sent-audio">{{SentenceAudio3}}</span>{{/SentenceAudio3}}
        <div class="de-sent">{{German 3}}</div>
        {{#English 3}}<div class="en-sent">{{English 3}}</div>{{/English 3}}
      </div>
      {{/German 3}}
    </div>
    {{/Definition 3}}

  </div>

  <!-- Verb conjugation table -->
  {{#Conjugation}}
  <div class="conj-section">
    <div class="conj-title">Konjugation</div>
    {{Conjugation}}
  </div>
  {{/Conjugation}}

  <!-- Word family -->
  {{#WordFamily}}
  <div class="family-section">
    <span class="family-label">Wortfamilie</span>
    <span class="family-words">{{WordFamily}}</span>
  </div>
  {{/WordFamily}}

  <div class="rank-tag">#{{Rank}} häufigste Wörter</div>

</div>

<script>
(function(){
  // Gender → colour example borders
  var pos1 = '{{Part-of-Speech 1}}'.trim();
  var gender = null;
  if(pos1==='der'||pos1==='der, die'||pos1==='der, das') gender='der';
  else if(pos1==='die'||pos1==='die (pl)'||pos1==='die, das'||pos1==='(pl)') gender='die';
  else if(pos1==='das'||pos1==='das, die (pl)') gender='das';
  else if(pos1==='der, die, das') gender='mixed';
  if(gender){
    document.querySelectorAll('.example-wrap').forEach(function(el){
      el.classList.add('eg-'+gender);
    });
  }

  // Hide article pos-tag in meanings (shown as badge already)
  var ARTS=['der','die','das','der, die','die (pl)','der, das','die, das','der, die, das','das, die (pl)','(pl)'];
  var p1=document.getElementById('pos1-tag');
  if(p1 && ARTS.indexOf(p1.textContent.trim())!==-1) p1.style.display='none';
})();
</script>
"""

# ══════════════════════════════════════════════════════════════════════════════
# CARD 2 — Production (English → German). Forces active retrieval.
# ══════════════════════════════════════════════════════════════════════════════
PROD_FRONT = r"""
<div class="prod-front">
  <div class="prod-level-badge" id="prod-level-badge">{{Level}}</div>

  <div class="prod-pos-pill">{{Part-of-Speech 1}}</div>
  <div class="prod-def">{{Definition 1}}</div>

  {{#English 1}}
  <div class="prod-en-hint">{{English 1}}</div>
  {{/English 1}}

  <div class="prod-prompt">Wie sagt man das auf Deutsch?</div>
</div>

<script>
(function(){
  var ARTICLES = ['der','die','das','der, die','die (pl)','der, das','die, das','der, die, das','das, die (pl)','(pl)'];
  document.querySelectorAll('.prod-pos-pill').forEach(function(el){
    if(ARTICLES.indexOf(el.textContent.trim()) !== -1) el.textContent = 'noun';
  });
  var lvl = '{{Level}}'.trim();
  var lb = document.getElementById('prod-level-badge');
  if(lb){
    if(lvl){ lb.classList.add('lvl-'+lvl.replace('+','plus')); }
    else { lb.style.display='none'; }
  }
})();
</script>
"""

PROD_BACK = r"""
{{FrontSide}}

<div class="answer-divider"></div>

<div class="prod-back">
  <div class="word-header" id="prod-word-header">
    <div class="gender-badge" id="prod-gender-badge"></div>
    <div class="word-main" id="prod-word-main">{{Word}}</div>
    <div class="word-plural" id="prod-word-plural"></div>
    <div class="ipa-line">[{{IPA}}]</div>
  </div>

  {{#WordAudio}}<div class="audio-row">{{WordAudio}}</div>{{/WordAudio}}

  {{#German 1}}
  <div class="prod-example">
    {{#SentenceAudio1}}<span class="sent-audio">{{SentenceAudio1}}</span>{{/SentenceAudio1}}
    <div class="de-sent">{{German 1}}</div>
  </div>
  {{/German 1}}

  {{#Conjugation}}
  <div class="conj-section">
    <div class="conj-title">Konjugation</div>
    {{Conjugation}}
  </div>
  {{/Conjugation}}
</div>

<script>
(function(){
  var pos1 = '{{Part-of-Speech 1}}'.trim();
  var header  = document.getElementById('prod-word-header');
  var badge   = document.getElementById('prod-gender-badge');
  var wordEl  = document.getElementById('prod-word-main');
  var plurEl  = document.getElementById('prod-word-plural');

  var gender = null;
  if(pos1==='der'||pos1==='der, die'||pos1==='der, das') gender='der';
  else if(pos1==='die'||pos1==='die (pl)'||pos1==='die, das'||pos1==='(pl)') gender='die';
  else if(pos1==='das'||pos1==='das, die (pl)') gender='das';
  else if(pos1==='der, die, das') gender='mixed';

  if(gender){
    header.classList.add('gender-'+gender);
    var lbl={der:'der — maskulin',die:'die — feminin',das:'das — neutrum',mixed:'mixed'};
    badge.textContent = lbl[gender]||pos1;
    var raw=wordEl.textContent.trim(), ci=raw.indexOf(',');
    if(ci!==-1){
      wordEl.textContent = raw.slice(0,ci).trim();
      plurEl.textContent = 'Pl. '+raw.slice(ci+1).trim();
    }
  } else {
    badge.style.display='none';
    plurEl.style.display='none';
  }
})();
</script>
"""

CSS = """
/* ── IPA-supporting font (Charis SIL — bundled in media folder) ── */
@font-face {
  font-family: 'CharisSIL';
  src: url('_charis.woff2') format('woff2');
  font-display: swap;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

.card {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
               'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
  font-size: 17px;
  line-height: 1.6;
  text-align: center;
  background: #fff;
  color: #111;
  padding: 0;
}
.nightMode.card, .nightMode .card, body.nightMode .card {
  background: #1c1c1e; color: #ececec;
}

/* ══ WORD HEADER ════════════════════════════════════════════════ */
.word-header {
  padding: 22px 20px 16px;
  background: #f5f5f7;
  border-bottom: 3px solid #ddd;
  position: relative;
}
.nightMode .word-header, body.nightMode .word-header
  { background:#2c2c2e; border-bottom-color:#444; }

/* gender tints */
.gender-der  { background:#e8f0fe; border-bottom-color:#4285f4; }
.gender-die  { background:#fce8e6; border-bottom-color:#ea4335; }
.gender-das  { background:#e6f4ea; border-bottom-color:#34a853; }
.gender-mixed{ background:#fef7e0; border-bottom-color:#fbbc04; }
.nightMode .gender-der,  body.nightMode .gender-der  { background:#172040; border-bottom-color:#4285f4; }
.nightMode .gender-die,  body.nightMode .gender-die  { background:#3b1210; border-bottom-color:#ea4335; }
.nightMode .gender-das,  body.nightMode .gender-das  { background:#0d2b18; border-bottom-color:#34a853; }
.nightMode .gender-mixed,body.nightMode .gender-mixed{ background:#2e2512; border-bottom-color:#fbbc04; }

/* Level badge — top-right corner */
.level-badge {
  position: absolute;
  top: 10px; right: 12px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 12px;
  border: 1.5px solid currentColor;
}
.lvl-A1   { color:#2e7d32; }
.lvl-A2   { color:#1565c0; }
.lvl-B1   { color:#e65100; }
.lvl-B2plus{ color:#6a1b9a; }
.nightMode .lvl-A1,    body.nightMode .lvl-A1    { color:#81c784; }
.nightMode .lvl-A2,    body.nightMode .lvl-A2    { color:#7baeff; }
.nightMode .lvl-B1,    body.nightMode .lvl-B1    { color:#ffcc80; }
.nightMode .lvl-B2plus,body.nightMode .lvl-B2plus{ color:#ce93d8; }

/* Gender label */
.gender-badge {
  font-size: 11px; font-weight: 800;
  letter-spacing: 1px; text-transform: uppercase;
  margin-bottom: 6px; color: #aaa;
}
.gender-der  .gender-badge { color:#1a56db; }
.gender-die  .gender-badge { color:#c62828; }
.gender-das  .gender-badge { color:#2e7d32; }
.gender-mixed .gender-badge{ color:#e65100; }
.nightMode .gender-der  .gender-badge, body.nightMode .gender-der  .gender-badge { color:#7baeff; }
.nightMode .gender-die  .gender-badge, body.nightMode .gender-die  .gender-badge { color:#ff8080; }
.nightMode .gender-das  .gender-badge, body.nightMode .gender-das  .gender-badge { color:#7ecf86; }
.nightMode .gender-mixed .gender-badge,body.nightMode .gender-mixed .gender-badge{ color:#ffd080; }

/* Main word */
.word-main {
  font-size: 40px; font-weight: 800;
  letter-spacing: -0.5px; line-height: 1.1;
  color: #111;
}
.nightMode .word-main, body.nightMode .word-main { color:#f0f0f0; }
.gender-der  .word-main { color:#1a56db; }
.gender-die  .word-main { color:#c62828; }
.gender-das  .word-main { color:#2e7d32; }
.gender-mixed .word-main{ color:#e65100; }
.nightMode .gender-der  .word-main, body.nightMode .gender-der  .word-main { color:#7baeff; }
.nightMode .gender-die  .word-main, body.nightMode .gender-die  .word-main { color:#ff8080; }
.nightMode .gender-das  .word-main, body.nightMode .gender-das  .word-main { color:#7ecf86; }
.nightMode .gender-mixed .word-main,body.nightMode .gender-mixed .word-main { color:#ffd080; }

/* Separable prefix highlight inside word-main */
.sep-prefix { text-decoration: underline; text-underline-offset: 4px; }

.word-plural {
  font-size: 14px; color:#999; margin-top:5px; font-style:italic;
}
.nightMode .word-plural, body.nightMode .word-plural { color:#777; }

.ipa-line {
  font-size:15px; color:#aaa; margin-top:8px; font-style:italic;
  /* Charis SIL is bundled with the deck — guarantees IPA renders on all devices */
  font-family: 'CharisSIL', 'Charis SIL', 'Doulos SIL',
               'DejaVu Sans', 'Lucida Sans Unicode',
               'Arial Unicode MS', 'Segoe UI', sans-serif;
}

/* ══ AUDIO + PROMPT ═══════════════════════════════════════════ */
.audio-row { padding:12px 0 2px; }

/* ══ IMAGE ════════════════════════════════════════════════════ */
.image-wrap {
  margin: 14px auto 4px;
  text-align: center;
  padding: 0 16px;
}
.image-wrap img {
  max-width: 100%;
  max-height: 220px;
  width: auto;
  height: auto;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.12);
  display: inline-block;
  background: #f0f0f0;
}
.nightMode .image-wrap img, body.nightMode .image-wrap img {
  box-shadow: 0 2px 12px rgba(0,0,0,0.5);
  background: #2a2a2c;
}
.prompt-hint {
  font-size:12px; color:#bbb; letter-spacing:0.8px;
  margin-top:8px; text-transform:uppercase; font-weight:600;
}
.nightMode .prompt-hint, body.nightMode .prompt-hint { color:#555; }

/* ══ DIVIDER ══════════════════════════════════════════════════ */
.answer-divider {
  height:1px;
  background:linear-gradient(to right,transparent,#ccc 20%,#ccc 80%,transparent);
  margin:4px 0;
}
.nightMode .answer-divider, body.nightMode .answer-divider {
  background:linear-gradient(to right,transparent,#444 20%,#444 80%,transparent);
}

/* ══ BACK MEANINGS ════════════════════════════════════════════ */
.back-wrap { padding:0 0 24px; }

.meanings-wrap {
  display:inline-block; text-align:left;
  max-width:520px; width:calc(100% - 32px);
  margin:12px 16px 0;
}

.meaning-block {
  padding:11px 0;
  border-bottom:1px solid #ebebeb;
}
.nightMode .meaning-block, body.nightMode .meaning-block { border-bottom-color:#2e2e2e; }
.meaning-block:last-child { border-bottom:none; }

.meaning-head { margin-bottom:5px; }

.pos-tag {
  display:inline-block; font-size:10px; font-weight:700;
  text-transform:uppercase; letter-spacing:0.5px;
  background:#eee; color:#555; border-radius:4px;
  padding:2px 7px; margin-right:8px; vertical-align:middle;
}
.nightMode .pos-tag, body.nightMode .pos-tag { background:#333; color:#bbb; }

.meaning-def { font-size:19px; font-weight:700; vertical-align:middle; }

.example-wrap {
  margin-top:7px; padding:9px 12px;
  border-radius:7px; background:#f5f5f7;
  border-left:4px solid #ccc;
}
.nightMode .example-wrap, body.nightMode .example-wrap { background:#252527; }

.eg-der { border-left-color:#4285f4; }
.eg-die { border-left-color:#ea4335; }
.eg-das { border-left-color:#34a853; }
.eg-mixed{ border-left-color:#fbbc04; }

/* Sentence audio — inline, small */
.sent-audio { display:inline-block; margin-bottom:4px; vertical-align:middle; }
.sent-audio .replaybutton { transform:scale(0.75); transform-origin:left center; }

.de-sent {
  font-size:15px; font-weight:500; color:#1a1a1a; line-height:1.45;
  display:inline;
}
.nightMode .de-sent, body.nightMode .de-sent { color:#e0e0e0; }

.en-sent {
  font-size:13px; color:#888; font-style:italic;
  margin-top:5px; line-height:1.4;
}
.nightMode .en-sent, body.nightMode .en-sent { color:#777; }

/* ══ CONJUGATION TABLE ════════════════════════════════════════ */
.conj-section {
  display:inline-block; text-align:left;
  max-width:520px; width:calc(100% - 32px);
  margin:10px 16px 0;
  background:#f0f4ff;
  border-radius:8px; padding:12px 14px;
  border:1px solid #d0d9ff;
}
.nightMode .conj-section, body.nightMode .conj-section
  { background:#1a1f35; border-color:#2a3060; }

.conj-title {
  font-size:11px; font-weight:700; text-transform:uppercase;
  letter-spacing:0.8px; color:#4285f4; margin-bottom:10px;
}

.conj-table {
  width:100%; border-collapse:collapse; font-size:14px;
}
.conj-table td {
  padding:4px 10px 4px 0;
}
.conj-table .pronoun {
  color:#888; font-style:italic; width:28%; white-space:nowrap;
}
.nightMode .conj-table .pronoun, body.nightMode .conj-table .pronoun { color:#888; }
.conj-table .form {
  font-weight:600; color:#111;
}
.nightMode .conj-table .form, body.nightMode .conj-table .form { color:#e0e0e0; }

.conj-extra {
  margin-top:8px; font-size:13px; color:#555;
  border-top:1px solid #d0d9ff; padding-top:7px;
}
.nightMode .conj-extra, body.nightMode .conj-extra { color:#999; border-top-color:#2a3060; }

.conj-extra strong { color:#4285f4; }

/* Perf box */
.perf-box {
  display:inline-block;
  background:#fff; border:1px solid #c0cef8;
  border-radius:5px; padding:3px 10px;
  font-size:14px; margin-top:4px;
}
.nightMode .perf-box, body.nightMode .perf-box
  { background:#0d1225; border-color:#2a3060; }

/* ══ WORD FAMILY ═══════════════════════════════════════════════ */
.family-section {
  display:inline-block; text-align:left;
  max-width:520px; width:calc(100% - 32px);
  margin:8px 16px 0;
  padding:9px 14px;
  background:#fdf6ff; border-radius:8px;
  border:1px solid #e0ccff;
}
.nightMode .family-section, body.nightMode .family-section
  { background:#1e1430; border-color:#3d2570; }

.family-label {
  font-size:11px; font-weight:700; text-transform:uppercase;
  letter-spacing:0.7px; color:#8e44ad; margin-right:10px;
}
.nightMode .family-label, body.nightMode .family-label { color:#ce93d8; }

.family-words { font-size:14px; color:#333; }
.nightMode .family-words, body.nightMode .family-words { color:#ddd; }

/* ══ RANK ══════════════════════════════════════════════════════ */
.rank-tag {
  margin-top:18px; font-size:11px; color:#ccc;
  letter-spacing:0.8px; text-transform:uppercase;
}
.nightMode .rank-tag, body.nightMode .rank-tag { color:#444; }

/* ══ PRODUCTION CARD (Card 2: EN → DE) ═════════════════════════════ */
.prod-front {
  padding: 32px 24px 24px;
  text-align: center;
  position: relative;
}

.prod-level-badge {
  position: absolute;
  top: 14px; right: 16px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 12px;
  border: 1.5px solid currentColor;
  color: #999;
}
.prod-level-badge.lvl-A1    { color:#2e7d32; }
.prod-level-badge.lvl-A2    { color:#1565c0; }
.prod-level-badge.lvl-B1    { color:#e65100; }
.prod-level-badge.lvl-B2plus{ color:#6a1b9a; }
.nightMode .prod-level-badge.lvl-A1,    body.nightMode .prod-level-badge.lvl-A1    { color:#81c784; }
.nightMode .prod-level-badge.lvl-A2,    body.nightMode .prod-level-badge.lvl-A2    { color:#7baeff; }
.nightMode .prod-level-badge.lvl-B1,    body.nightMode .prod-level-badge.lvl-B1    { color:#ffcc80; }
.nightMode .prod-level-badge.lvl-B2plus,body.nightMode .prod-level-badge.lvl-B2plus{ color:#ce93d8; }

.prod-pos-pill {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #fff;
  background: #888;
  border-radius: 4px;
  padding: 3px 9px;
  margin-bottom: 14px;
}

.prod-def {
  font-size: 30px;
  font-weight: 800;
  color: #111;
  letter-spacing: -0.3px;
  line-height: 1.2;
  margin-bottom: 14px;
}
.nightMode .prod-def, body.nightMode .prod-def { color:#f0f0f0; }

.prod-en-hint {
  font-size: 15px;
  color: #777;
  font-style: italic;
  margin-bottom: 22px;
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.4;
}
.nightMode .prod-en-hint, body.nightMode .prod-en-hint { color:#999; }

.prod-prompt {
  font-size: 12px;
  color: #bbb;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  font-weight: 600;
}
.nightMode .prod-prompt, body.nightMode .prod-prompt { color:#555; }

.prod-back { padding: 0 0 24px; }

.prod-example {
  display: inline-block;
  text-align: left;
  max-width: 500px;
  width: calc(100% - 32px);
  margin: 12px 16px 4px;
  padding: 9px 13px;
  border-radius: 7px;
  background: #f5f5f7;
  border-left: 4px solid #0193c4;
}
.nightMode .prod-example, body.nightMode .prod-example { background:#252527; }
"""

# ── Build conjugation HTML ─────────────────────────────────────────────────────

def make_conj_html(c):
    """Turn conjugation dict into a clean HTML table."""
    if not c:
        return ""

    sep = c.get("sep", "")
    inf = c.get("inf", "")
    aux = c.get("aux", "haben")

    # Detect separable: if ich-form has a space (e.g. "rufe an")
    def fmt(form):
        if not form:
            return "—"
        if sep and form.endswith(" " + sep):
            stem = form[: -(len(sep) + 1)]
            return f'{stem} <u>{sep}</u>'
        return form

    wir = c.get("wir") or inf  # wir = infinitive for regular verbs
    ihr = c.get("ihr") or ""
    sie = c.get("sie") or wir

    rows = [
        ("ich",   c.get("ich","")),
        ("du",    c.get("du","")),
        ("er/sie/es", c.get("er","")),
        ("wir",   wir),
        ("ihr",   ihr),
        ("sie/Sie", sie),
    ]

    html  = '<table class="conj-table">'
    for pronoun, form in rows:
        if form:
            html += f'<tr><td class="pronoun">{pronoun}</td><td class="form">{fmt(form)}</td></tr>'
    html += "</table>"

    # Perfekt — auxiliary must be CONJUGATED (ich bin / ich habe), not infinitive
    AUX_ICH = {"sein": "bin", "haben": "habe"}
    aux_ich = AUX_ICH.get(aux, "habe")

    pp = c.get("pp", "")
    past = c.get("past", "")
    if pp or past:
        html += '<div class="conj-extra">'
        if past:
            html += f'<strong>Prät.</strong> ich {past} &nbsp;|&nbsp; '
        if pp:
            html += f'<strong>Perf.</strong> <span class="perf-box">ich {aux_ich} {pp}</span>'
        html += "</div>"

    return html


# ── Main function ──────────────────────────────────────────────────────────────

def apply_all():
    col = mw.col
    if col is None:
        return

    # Already done?
    try:
        if col.get_config(DONE_FLAG):
            return
    except Exception:
        pass

    nt = col.models.by_name(NOTETYPE_NAME)
    if nt is None:
        showInfo(f"Notetype '{NOTETYPE_NAME}' not found — please import the deck first.")
        return

    # Load data
    levels    = load_json("levels.json")
    conj_data = load_json("conjugations.json")
    sent_audio= load_json("sentence_audio.json")
    families  = load_json("families.json")
    images    = load_json("image_map.json")

    # ── 1. Add new fields ──────────────────────────────────────────────────────
    existing = {f["name"] for f in nt["flds"]}
    new_fields = [
        "Level", "WordFamily", "Conjugation",
        "SentenceAudio1", "SentenceAudio2", "SentenceAudio3", "WordAudio",
        "Image",
    ]
    # Find existing Audio field
    # Rename Audio → WordAudio if needed
    for fld in nt["flds"]:
        if fld["name"] == "Audio":
            fld["name"] = "WordAudio"
            existing.discard("Audio")
            existing.add("WordAudio")
            break

    max_ord = max(f["ord"] for f in nt["flds"])
    for fname in new_fields:
        if fname not in existing:
            max_ord += 1
            nt["flds"].append({
                "name": fname, "ord": max_ord,
                "sticky": False, "rtl": False,
                "font": "Arial", "size": 20, "media": [],
            })
            existing.add(fname)

    # ── 2. Update templates ────────────────────────────────────────────────────
    nt["tmpls"][0]["qfmt"] = FRONT
    nt["tmpls"][0]["afmt"] = BACK
    # Card 2 — Production (EN → DE) for active recall
    if len(nt["tmpls"]) < 2:
        nt["tmpls"].append({
            "name": "Production (EN→DE)",
            "ord": 1,
            "qfmt": PROD_FRONT,
            "afmt": PROD_BACK,
            "did": None,
            "bqfmt": "", "bafmt": "",
        })
    else:
        nt["tmpls"][1]["qfmt"] = PROD_FRONT
        nt["tmpls"][1]["afmt"] = PROD_BACK
    nt["css"] = CSS
    col.models.update_dict(nt)

    # ── 3. Update all notes ────────────────────────────────────────────────────
    # Re-fetch after model update
    nt = col.models.by_name(NOTETYPE_NAME)
    field_idx = {f["name"]: f["ord"] for f in nt["flds"]}

    note_ids = col.find_notes(f'"note:{NOTETYPE_NAME}"')
    total    = len(note_ids)

    for i, nid in enumerate(note_ids):
        note  = col.get_note(nid)
        snid  = str(nid)

        # Level
        if "Level" in field_idx:
            note.fields[field_idx["Level"]] = levels.get(snid, "B2+")

        # Word family
        if "WordFamily" in field_idx:
            fam = families.get(snid, [])
            note.fields[field_idx["WordFamily"]] = " · ".join(fam) if fam else ""

        # Conjugation HTML
        if "Conjugation" in field_idx:
            cdata = conj_data.get(snid)
            note.fields[field_idx["Conjugation"]] = make_conj_html(cdata) if cdata else ""

        # Sentence audio
        smap = sent_audio.get(snid, {})
        for slot, fname_key, fld_name in [
            ("s1", "SentenceAudio1", "SentenceAudio1"),
            ("s2", "SentenceAudio2", "SentenceAudio2"),
            ("s3", "SentenceAudio3", "SentenceAudio3"),
        ]:
            if fld_name in field_idx:
                fname = smap.get(slot, "")
                note.fields[field_idx[fld_name]] = f"[sound:{fname}]" if fname else ""

        # WordAudio — copy from old Audio field if empty
        if "WordAudio" in field_idx:
            current = note.fields[field_idx["WordAudio"]]
            if not current:
                # Try old slot (index 16)
                if len(note.fields) > 16:
                    note.fields[field_idx["WordAudio"]] = note.fields[16]

        # Image — must be wrapped in <img> tag so Anki's media exporter
        # recognizes it as a referenced file (bare filenames get stripped on export)
        if "Image" in field_idx:
            img_fname = images.get(snid, "")
            if img_fname:
                note.fields[field_idx["Image"]] = f'<img src="{img_fname}" />'
            else:
                note.fields[field_idx["Image"]] = ""

        # CEFR tag — mirror the Level field as a tag so tag:A1 / tag:B1 filters work
        lvl = levels.get(snid, "")
        if lvl:
            tag = lvl.replace("+", "plus")   # B2+ → B2plus (Anki tags can't contain +)
            # Remove old level tags first
            for old in ("A1","A2","B1","B2plus"):
                if old in note.tags:
                    note.tags.remove(old)
            note.tags.append(tag)

        col.update_note(note)

        if (i + 1) % 100 == 0 or (i + 1) == total:
            mw.progress.update(
                label=f"Updating notes… {i+1}/{total}",
                value=i + 1,
                max=total,
            )

    # ── 4. Suspend Card 2 (production) for B2+ cards ──────────────────────────
    # New learners shouldn't be overwhelmed with 10K cards. B2+ production
    # cards stay suspended until the user is ready to unsuspend them.
    b2plus_note_ids = [nid for nid in note_ids
                       if levels.get(str(nid), "") == "B2+"]
    if b2plus_note_ids:
        # Get all Card-2 cards for these notes
        card_ids = col.db.list(
            "SELECT id FROM cards WHERE nid IN ("
            + ",".join("?" for _ in b2plus_note_ids)
            + ") AND ord = 1",
            *b2plus_note_ids,
        )
        if card_ids:
            col.sched.suspend_cards(card_ids)

    col.set_config(DONE_FLAG, True)
    mw.progress.finish()
    showInfo(
        "✓ German Deck v2.1 ready!\n\n"
        "New in this version:\n"
        "  • Fixed Perfekt bug (ich bin gewesen, not ich sein gewesen)\n"
        "  • Card 2 added — EN→DE production for active recall\n"
        "  • CEFR tags (use tag:A1, tag:A2, tag:B1, tag:B2plus)\n"
        "  • Better level tagging via frequency fallback\n"
        "  • B2+ production cards auto-suspended (unsuspend when ready)\n\n"
        "Total cards: ~10,000 (5,009 recognition + ~2,100 active production)\n\n"
        "You can disable the 'german_deck_ultimate' add-on now."
    )


def on_collection_loaded(col):
    # Skip immediately if already done — don't open the progress dialog at all,
    # otherwise it never closes (visible bug: Anki appears frozen on subsequent starts).
    try:
        if col.get_config(DONE_FLAG):
            return
    except Exception:
        pass

    mw.progress.start(label="Enhancing German deck…", immediate=True)
    try:
        apply_all()
    except Exception as e:
        showInfo(f"Error: {e}")
    finally:
        try:
            mw.progress.finish()
        except Exception:
            pass


gui_hooks.collection_did_load.append(on_collection_loaded)
