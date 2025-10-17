#!/usr/bin/env python3
import csv
import hashlib
import pathlib
import re
import sys
from datetime import datetime
import os
import io





def build_suffix():
    run = os.getenv("GITHUB_RUN_NUMBER") or os.getenv("BUILD_NUMBER")
    if run:
        return f"build{run}"
    return datetime.now().strftime("%Y%m%d-%H%M")

import genanki

# --- Repo layout ---
ROOT = pathlib.Path(__file__).resolve().parent.parent
TXT_DIR = ROOT / "txt_export"
OUT = ROOT / "os_theory.apkg"

# --- Global deck name (root). Subdecks seront "OS Theory (202.1)::<Deck>" si colonne deck présente.
ROOT_DECK_NAME = "OS Theory (202.1)"


VERSION_FILE = ROOT / "VERSION"

def read_version():
    if VERSION_FILE.exists():
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    return "0.0.0"

# ---------- utils ----------
def stable_id(seed: str) -> int:
    # 32-bit signed range; stable across runs
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return int(h, 16) & 0x7FFFFFFF

def guid_for(front: str, back: str) -> str:
    seed = f"{front}\u241F{back}"
    return hashlib.md5(seed.encode("utf-8")).hexdigest()

# Cache de modèles et decks dynamiques (par notetype/deck rencontrés)
MODEL_CACHE = {}
DECK_CACHE = {}

def get_or_make_model(notetype_name: str):
    """
    Crée un modèle 'Basic' (Front/Back/Source) pour chaque notetype rencontré.
    Si tu veux des templates différents par notetype, on peut étendre ici.
    """
    if notetype_name in MODEL_CACHE:
        return MODEL_CACHE[notetype_name]

    model_id = stable_id(f"model::{notetype_name}::v1")
    model = genanki.Model(
        model_id,
        f"{notetype_name} – Basic (Front/Back)",
        fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Source"}],
        templates=[{
            "name": "Card 1",
            "qfmt": "<div class='front'>{{Front}}</div>",
            "afmt": "{{FrontSide}}<hr id='answer'><div class='back'>{{Back}}</div>"
                    "<div class='src'>{{#Source}}<hr><em>{{Source}}{{/Source}}</em></div>",
        }],
        css="""
.card { font-family: Inter, Segoe UI, Arial; font-size: 18px; line-height: 1.35; }
.front { font-weight: 600; }
.src { color: #777; font-size: 0.9em; }
""",
    )
    MODEL_CACHE[notetype_name] = model
    return model

def get_or_make_deck(deck_path: str):
    """
    deck_path = ""  -> root deck
    deck_path = "OS" -> ROOT::OS
    deck_path peut déjà contenir '::' pour des sous-decks imbriqués.
    """
    full_name = ROOT_DECK_NAME if not deck_path else f"{ROOT_DECK_NAME}::{deck_path}"
    if full_name in DECK_CACHE:
        return DECK_CACHE[full_name]
    deck_id = stable_id(f"deck::{full_name}::v1")
    deck = genanki.Deck(deck_id, full_name)
    DECK_CACHE[full_name] = deck
    return deck

# ---------- parseurs ----------
HEADER_SIMPLE_RE = re.compile(r"^#\s*([A-Za-z_-]+)\s*:\s*(.*)\s*$")
NT_RE   = re.compile(r"^#\s*notetype\s+column\s*:\s*(\d+)\s*$", re.I)
DECK_RE = re.compile(r"^#\s*deck\s+column\s*:\s*(\d+)\s*$", re.I)
TAGS_RE = re.compile(r"^#\s*tags\s+column\s*:\s*(\d+)\s*$", re.I)

def parse_header_directives(lines):
    """
    Supporte:
      #separator:tab|comma
      #html:true|false
      #notetype column:1
      #deck column:2
      #tags column:5
    Retourne (config, start_index)
    """
    cfg = {
        "separator": "\t",
        "html": False,
        "nt_col": None,
        "deck_col": None,
        "tags_col": None,
    }
    idx = 0
    while idx < len(lines):
        line = lines[idx].rstrip("\n")
        if not line.startswith("#"):
            break

        # Cas spécifiques avec "column:"
        m = NT_RE.match(line)
        if m:
            cfg["nt_col"] = int(m.group(1)) - 1
            idx += 1
            continue
        m = DECK_RE.match(line)
        if m:
            cfg["deck_col"] = int(m.group(1)) - 1
            idx += 1
            continue
        m = TAGS_RE.match(line)
        if m:
            cfg["tags_col"] = int(m.group(1)) - 1
            idx += 1
            continue

        # Cas simples "key:value" (#separator, #html)
        m = HEADER_SIMPLE_RE.match(line)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip()
            if key == "separator":
                if val.lower().startswith("tab"):
                    cfg["separator"] = "\t"
                elif val.lower().startswith("comma"):
                    cfg["separator"] = ","
            elif key == "html":
                cfg["html"] = val.lower() == "true"

        idx += 1

    return cfg, idx



def read_cards_from_txt(txt_path: pathlib.Path):
    """
    Lit un export texte Anki avec directives (#separator, #html, #notetype column, etc.)
    en respectant les champs multi-lignes (HTML) grâce à csv.reader.
    Mapping attendu (comme OS.txt) :
      col1 = notetype, col2 = deck, col3 = front, col4 = back, col5 = tags (optionnel)
    """
    raw_text = txt_path.read_text(encoding="utf-8")
    lines = raw_text.splitlines()
    cfg, start = parse_header_directives(lines)

    sep = cfg["separator"]
    nt_idx   = cfg["nt_col"]    # ex: 0
    deck_idx = cfg["deck_col"]  # ex: 1
    tags_idx = cfg["tags_col"]  # ex: 4

    # Si notetype + deck sont définis, on force Front/Back juste après (col 3 et 4)
    explicit_fb = nt_idx is not None and deck_idx is not None
    if explicit_fb:
        front_idx = max(nt_idx, deck_idx) + 1
        back_idx  = front_idx + 1
    else:
        front_idx = back_idx = None  # heuristique fallback plus bas

    # Reconstitue le bloc "données" après les entêtes et parse avec csv.reader
    data_block = "\n".join(lines[start:])
    reader = csv.reader(io.StringIO(data_block), delimiter=sep, quotechar='"', doublequote=True)

    for cols in reader:
        if not cols:
            continue

        # Nettoyage doux (on garde les retours à la ligne internes, csv l’a déjà fait)
        cols = [c for c in cols]

        # Champs réservés présents ?
        reserved = set(i for i in [nt_idx, deck_idx, tags_idx] if i is not None and i < len(cols))

        # Choix Front/Back
        if explicit_fb and back_idx is not None and back_idx < len(cols):
            f_idx, b_idx = front_idx, back_idx
        else:
            # Fallback : 2 premières colonnes non réservées
            candidates = [i for i in range(len(cols)) if i not in reserved]
            if len(candidates) < 2:
                continue
            f_idx, b_idx = candidates[0], candidates[1]

        notetype = cols[nt_idx]   if nt_idx   is not None and nt_idx   < len(cols) else "Basique"
        deck     = cols[deck_idx] if deck_idx is not None and deck_idx < len(cols) else ""
        tags     = cols[tags_idx] if tags_idx is not None and tags_idx < len(cols) else ""
        front    = cols[f_idx] if f_idx < len(cols) else ""
        back     = cols[b_idx] if b_idx < len(cols) else ""

        # Trim léger en bout, on NE supprime PAS les \n internes
        front = front.strip()
        back  = back.strip()

        if not front or not back:
            continue

        yield (notetype, deck, front, back, tags, txt_path.name)



def read_cards_from_tsv(tsv_path: pathlib.Path):
    """
    Format TSV "simple": Front<TAB>Back<TAB>tags  (tags optionnel)
    """
    with tsv_path.open("r", encoding="utf-8") as f:
        rdr = csv.reader(f, delimiter="\t")
        for row in rdr:
            if not row or (row[0].strip().startswith("#")):
                continue
            while len(row) < 3:
                row.append("")
            front, back, tags = row[0].strip(), row[1].strip(), row[2].strip()
            if not front or not back:
                continue
            yield ("Basique", "", front, back, tags, tsv_path.name)

def iter_all_cards():
    if not TXT_DIR.exists():
        print(f"[!] Missing folder: {TXT_DIR}", file=sys.stderr)
        sys.exit(1)

    for p in sorted(TXT_DIR.glob("*")):
        if p.suffix.lower() == ".txt":
            yield from read_cards_from_txt(p)
        elif p.suffix.lower() in {".tsv", ".tab"}:
            yield from read_cards_from_tsv(p)
        # (tu peux ajouter .csv ici si besoin)

# ---------- build ----------
def build_package():
    # On construit un paquet unique qui contient tous les sous-decks
    # (genanki n'autorise pas de multi-decks *directement*, mais on peut
    # attacher les notes à des Decks différents, puis regrouper via Package.media_files)
    all_decks = set()
    count = 0

    for notetype, deck_path, front, back, tags, source in iter_all_cards():
        model = get_or_make_model(notetype)
        deck = get_or_make_deck(deck_path)
        all_decks.add(deck)

        note = genanki.Note(
            model=model,
            fields=[front, back, source],
            tags=[t.strip() for t in tags.split(",") if t.strip()],
            guid=guid_for(front, back),
        )
        deck.add_note(note)
        count += 1

    if count == 0:
        print("[!] No cards found in txt_export", file=sys.stderr)
        sys.exit(2)

    # Le Package prend soit un seul deck, soit une liste de decks via 'decks' (API non officielle).
    # Astuce: on crée un "dummy" deck racine et on y ajoute rien; mais genanki>=0.13.1
    # permet de passer 'decks' au Package via attribut privé. Plus simple:
    # On prend arbitrairement le 1er deck et on lui ajoute les autres via l'attribut .decks
    # (implémentation interne de genanki tolère ça). Sinon: fusionner sous un deck unique.
    decks_list = list(all_decks)
    primary = decks_list[0]
    pkg = genanki.Package(primary)
    if len(decks_list) > 1:
        # hack doux: attacher tous les decks
        pkg.decks = decks_list  # type: ignore[attr-defined]

    pkg.media_files = []
    suffix = build_suffix()
    version = read_version()
    versioned_out = ROOT / f"os_theory-v{version}+{suffix}.apkg"
    pkg.write_to_file(str(versioned_out))
    pkg.write_to_file(str(OUT))
    print(f"[✓] Built {versioned_out.name} and {OUT.name}")



def main():
    build_package()

if __name__ == "__main__":
    main()
