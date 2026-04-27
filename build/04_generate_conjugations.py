"""
Generate German verb conjugations WITHOUT external API.
The deck's Word field already encodes: infinitive, er-form, past, perfekt.
e.g. "fahren, fährt, fuhr, ist gefahren"
     "machen, macht, machte, hat gemacht"
     "sein, ist, war, ist gewesen"

From these 4 forms we derive all 6 present tense forms via rules.
Saves conjugations.json: {note_id: {...}}
"""
import json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

OUTFILE = Path("C:/Users/Mohith Akash/AppData/Local/Temp/conjugations.json")

with open("C:/Users/Mohith Akash/AppData/Local/Temp/deck_verbs.json", encoding="utf-8") as f:
    verbs = json.load(f)

# ── Derivation rules ───────────────────────────────────────────────────────────

def get_inf_stem(inf):
    """Return verb stem from infinitive."""
    if inf.endswith('ern') or inf.endswith('eln'):
        return inf[:-2]   # wandern → wander, lächeln → lächel
    if inf.endswith('en'):
        return inf[:-2]   # machen → mach
    if inf.endswith('n'):
        return inf[:-1]   # tun → tu
    return inf

def derive_ich(inf, er):
    """
    Derive ich-form. Rule: ALWAYS use infinitive stem + e.
    Strong verbs have vowel change ONLY in du/er, not ich/wir/sie.
    e.g. fahren (er=fährt) → ich fahre (NOT fähre)
         geben  (er=gibt)  → ich gebe  (NOT gibe)
         lesen  (er=liest) → ich lese
    """
    stem = get_inf_stem(inf)
    # e-insertion for stems ending in d/t/m/n (preceded by consonant)
    if stem.endswith(('t','d')):
        return stem + 'e'
    if stem.endswith('e'):
        return stem   # reisen → reise, but stem already ends in e
    return stem + 'e'

def derive_du(inf, er):
    """Derive du-form from er-form."""
    er = er.strip()
    if er.endswith('t'):
        stem = er[:-1]
        # du = stem + st (but avoid double s: heißt → heißt → du heißt)
        if stem.endswith('s') or stem.endswith('z') or stem.endswith('ß'):
            return stem + 't'
        if stem.endswith('t') or stem.endswith('d'):
            return stem + 'est'
        return stem + 'st'
    # Modal: kann → du kannst
    if er.endswith('n'):
        return er[:-1] + 'nst'
    return er + 'st'

def derive_ihr(inf, er):
    """Derive ihr-form from er-form — usually same as er-form."""
    return er.strip()

def extract_aux_and_pp(perfekt_str):
    """Extract auxiliary and past participle from perfekt string."""
    # "hat gemacht" → (haben, gemacht)
    # "ist gefahren" → (sein, gefahren)
    # "ist gewesen" → (sein, gewesen)
    p = perfekt_str.strip()
    if p.startswith('ist '):
        return 'sein', p[4:].strip()
    elif p.startswith('hat '):
        return 'haben', p[4:].strip()
    elif p.startswith('haben '):
        return 'haben', p[6:].strip()
    elif p.startswith('sein '):
        return 'sein', p[5:].strip()
    else:
        # Could be just the PP with no aux
        return 'haben', p

def is_separable(er_form, inf):
    """Detect separable verb: 'ruft an' has a space."""
    return ' ' in er_form.strip()

def get_sep_prefix(er_form):
    parts = er_form.strip().split()
    return parts[-1] if len(parts) > 1 else ""

IRREGULAR = {
    # inf: (ich, du, er, wir, ihr, sie, past-ich, pp, aux)
    'sein':   ('bin','bist','ist','sind','seid','sind','war','gewesen','sein'),
    'haben':  ('habe','hast','hat','haben','habt','haben','hatte','gehabt','haben'),
    'werden': ('werde','wirst','wird','werden','werdet','werden','wurde','geworden','sein'),
    'wissen': ('weiß','weißt','weiß','wissen','wisst','wissen','wusste','gewusst','haben'),
    'tun':    ('tue','tust','tut','tun','tut','tun','tat','getan','haben'),
    # Modals
    'können': ('kann','kannst','kann','können','könnt','können','konnte','gekonnt','haben'),
    'müssen': ('muss','musst','muss','müssen','müsst','müssen','musste','gemusst','haben'),
    'dürfen': ('darf','darfst','darf','dürfen','dürft','dürfen','durfte','gedurft','haben'),
    'sollen': ('soll','sollst','soll','sollen','sollt','sollen','sollte','gesollt','haben'),
    'wollen': ('will','willst','will','wollen','wollt','wollen','wollte','gewollt','haben'),
    'mögen':  ('mag','magst','mag','mögen','mögt','mögen','mochte','gemocht','haben'),
    'möchten':('möchte','möchtest','möchte','möchten','möchtet','möchten','wollte','gewollt','haben'),
    # Strong inseparable verbs that have no Präteritum data in the deck
    'verhalten':  ('verhalte','verhältst','verhält','verhalten','verhaltet','verhalten','verhielt','verhalten','haben'),
    'übertragen': ('übertrage','überträgst','überträgt','übertragen','übertragt','übertragen','übertrug','übertragen','haben'),
    'betreten':   ('betrete','betrittst','betritt','betreten','betretet','betreten','betrat','betreten','haben'),
    'vergeben':   ('vergebe','vergibst','vergibt','vergeben','vergebt','vergeben','vergab','vergeben','haben'),
    # Weak inseparable
    'überlegen':  ('überlege','überlegst','überlegt','überlegen','überlegt','überlegen','überlegte','überlegt','haben'),
    'buchen':     ('buche','buchst','bucht','buchen','bucht','buchen','buchte','gebucht','haben'),
}

# Umlaut reversal for strong verbs (er-form umlaut → ich has no umlaut)
UMLAUT_REVERSE = {'ä':'a','ö':'o','ü':'u','ä':'a'}

def derive_all_forms(verb_entry):
    word = verb_entry['word']
    inf  = verb_entry['infinitive'].lower().strip()

    # Split word field: "fahren, fährt, fuhr, ist gefahren"
    parts = [p.strip() for p in word.split(',')]

    # Check irregular table first
    if inf in IRREGULAR:
        ich, du, er, wir, ihr, sie, past, pp, aux = IRREGULAR[inf]
        return {
            'ich': ich, 'du': du, 'er': er,
            'wir': wir, 'ihr': ihr, 'sie': sie,
            'past': past, 'pp': pp, 'aux': aux,
            'sep': '', 'inf': inf,
        }

    # Try to parse from deck field
    # parts[0] = infinitive (possibly with article for nouns — but this is verbs list)
    # parts[1] = er/sie/es present (if exists)
    # parts[2] = ich preterite (if exists)
    # parts[3] = perfekt (hat/ist + pp) (if exists)

    er_raw  = parts[1].strip() if len(parts) > 1 else ""
    past_raw= parts[2].strip() if len(parts) > 2 else ""
    perf_raw= parts[3].strip() if len(parts) > 3 else ""

    # Detect separable from er-form
    sep = get_sep_prefix(er_raw) if is_separable(er_raw, inf) else ""

    # For separable verbs: er_base = "ruft" (strip the trailing prefix)
    er_base = er_raw
    if sep:
        er_base = er_raw[: -(len(sep)+1)].strip()  # "ruft an" → "ruft"

    # Derive all forms
    if not er_base:
        # Fallback: derive from infinitive (regular weak verb)
        stem  = get_inf_stem(inf)
        ich_f = stem + 'e'
        du_f  = stem + 'st'
        er_f  = stem + 't'
        wir_f = inf
        ihr_f = stem + 't'
        sie_f = inf
    else:
        ich_f = derive_ich(inf, er_base)
        du_f  = derive_du(inf, er_base)
        er_f  = er_base
        wir_f = inf
        ihr_f = derive_ihr(inf, er_base)
        sie_f = inf

    # For separable verbs: recompute ich/wir using the BASE infinitive (no prefix)
    # e.g. anfangen → base=fangen → ich fange an, wir fangen an
    if sep:
        base_inf = inf[len(sep):] if inf.startswith(sep) else inf
        ich_f = derive_ich(base_inf, er_base) + ' ' + sep
        du_f  = du_f  + ' ' + sep
        er_f  = er_f  + ' ' + sep
        wir_f = base_inf + ' ' + sep
        ihr_f = derive_ihr(base_inf, er_base) + ' ' + sep
        sie_f = base_inf + ' ' + sep

    # Aux + PP
    aux, pp = 'haben', ''
    if perf_raw:
        aux, pp = extract_aux_and_pp(perf_raw)
    elif past_raw:
        aux = 'sein' if any(inf.endswith(e) for e in ['kommen','gehen','laufen','fahren','fliegen','fallen','steigen','reisen','wandern']) else 'haben'

    # Fallback: derive PP from infinitive when missing (regular weak verbs + inseparable prefixes)
    if not pp:
        # Inseparable prefixes (no ge-): be-, ge-, er-, ent-, ver-, zer-, miss-, voll-, wider-
        # Also über-, unter-, durch-, um- can be inseparable (verb-specific, but commonly are)
        INSEP = ('be','ge','er','ent','ver','zer','miss','voll','wider','über','unter','durch','um','hinter','emp','um')
        stem = get_inf_stem(inf)
        # -ieren verbs: no ge-
        if inf.endswith('ieren'):
            pp = stem + 't'
        # Inseparable prefix
        elif any(inf.startswith(p) and len(inf) > len(p) + 3 for p in INSEP):
            # Check if PP is same as infinitive (strong inseparable like vergeben → vergeben)
            # vs weak inseparable (überlegen → überlegt)
            # Heuristic: if past_raw has same vowel as inf stem, weak → +t. If different, strong → +en
            # Simplification: default to weak (+t) with stem
            if inf.endswith('en'):
                # Strong verbs typically keep -en. Weak gets -t.
                # Without past tense info, default to -t for weak
                pp = stem + 't'
            else:
                pp = inf
        else:
            # Regular weak verb: ge + stem + t
            if stem.endswith(('t','d')):
                pp = 'ge' + stem + 'et'
            else:
                pp = 'ge' + stem + 't'

    return {
        'ich': ich_f, 'du': du_f, 'er': er_f,
        'wir': wir_f, 'ihr': ihr_f, 'sie': sie_f,
        'past': past_raw, 'pp': pp, 'aux': aux,
        'sep': sep, 'inf': inf,
    }

# ── Process all verbs ──────────────────────────────────────────────────────────
results = {}
failed  = 0

for verb_entry in verbs:
    nid = str(verb_entry['id'])
    try:
        c = derive_all_forms(verb_entry)
        results[nid] = c
    except Exception as e:
        failed += 1

print(f"Done: {len(results)}/{len(verbs)} verbs ({failed} failed)")

# Sample output
for v in verbs[:5]:
    nid = str(v['id'])
    if nid in results:
        c = results[nid]
        print(f"\n{v['word']}")
        print(f"  ich {c['ich']} | du {c['du']} | er {c['er']} | wir {c['wir']}")
        print(f"  ich {c['past']} | {c['aux']} {c['pp']}")
        if c['sep']: print(f"  SEPARABLE prefix: {c['sep']}")

with open(OUTFILE, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nSaved → {OUTFILE}")
