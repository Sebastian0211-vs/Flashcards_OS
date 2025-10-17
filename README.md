# 🧠 Flashcards_OS

An **Anki deck builder** for operating system theory — written in Python and fully automated via `genanki`.  
This repository lets you **collaboratively build**, **version**, and **release** your Anki decks with Git and GitHub Actions.

---

## ✨ Features

- 🧩 **Editable text exports** (`txt_export/*.txt`) in Anki format  
- ⚙️ **Automatic build** → generates `.apkg` decks from text files  
- 📦 **Versioned releases** → each deck version tagged on GitHub  
- 💻 **Cross-platform build** → works on Windows, macOS, Linux  
- 🧑‍🤝‍🧑 **Collaborative workflow** using Git instead of AnkiWeb  

---

## 📂 Repository Structure

```
Flashcards_OS/
├── build/
│   ├── build.py              # Parser & deck builder (genanki)
│   ├── bump_version.py       # Version bump helper
│   ├── release_tag.py        # Tag & push release
│   └── requirements.txt      # Dependencies
├── txt_export/               # Text exports of your decks
│   └── OS.txt
├── .github/
│   └── workflows/
│       └── build.yml         # CI workflow (build & release)
├── Makefile                  # Build & version automation
├── VERSION                   # Current deck version
├── README.md
└── .gitignore
```

---

## ⚡ Quick Start

### 🪟 Windows (PowerShell or CMD)

1. **Clone the repo**
   ```powershell
   git clone https://github.com/<your-username>/Flashcards_OS.git
   cd Flashcards_OS
   ```

2. **Install GNU Make (optional but recommended)**  
   ```powershell
   choco install make
   ```
   *(or run the Python commands directly below)*

3. **Build the deck**
   ```powershell
   make build
   ```
   or manually:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   python -m pip install -r build/requirements.txt
   python build/build.py
   ```

4. 🎉 You’ll get:
   ```
   os_theory.apkg
   os_theory-v1.0.1.apkg
   ```

5. **Import into Anki**
   - Open Anki → `File → Import`
   - Select `os_theory.apkg`
   - Done ✅

---

### 🐧 Linux / macOS

```bash
git clone https://github.com/<your-username>/Flashcards_OS.git
cd Flashcards_OS
make build
```

---

## 🏗️ Build Workflow

| Command | Description |
|----------|--------------|
| `make build` | Create `.apkg` files from `txt_export/*.txt` |
| `make clean` | Delete generated decks |
| `make show-version` | Display current version |
| `make bump-patch` | Increment version (e.g. 1.0.0 → 1.0.1) |
| `make bump-minor` | Increment version (e.g. 1.0.0 → 1.1.0) |
| `make bump-major` | Increment version (e.g. 1.0.0 → 2.0.0) |
| `make release` | Build + create Git tag → triggers GitHub Release |

---

## 🧾 Deck Format

All flashcards live in `txt_export/` using Anki’s **text export format**:

```text
#separator:tab
#html:true
#notetype column:1
#deck column:2
#tags column:5
Basique	OS	Question ?	Réponse complète avec HTML possible.	tag1,tag2
```

- `column:1` → Notetype (e.g., “Basique”)  
- `column:2` → Deck name (creates sub-decks)  
- `column:3` → Front (question)  
- `column:4` → Back (answer, supports HTML)  
- `column:5` → Tags (comma-separated)

💡 You can export decks from Anki to text format, edit them here, and rebuild the `.apkg` with `make build`.

---

## 🔁 Contributing

### 💬 Adding new cards

1. Edit or create a new file in `txt_export/`
2. Follow the same header structure (`#separator`, `#deck`, etc.)
3. Build locally to test:
   ```bash
   make build
   ```
4. Import into Anki and verify formatting.

### 🧩 Submitting changes

```bash
git checkout -b feat/memory-fragmentation
git add txt_export/
git commit -m "add: new memory management flashcards"
git push origin feat/memory-fragmentation
```

Open a **Pull Request** on GitHub — once merged, a new version can be released.

---

## 🚀 Releasing a new version

1. Bump the version:
   ```bash
   make bump-patch
   ```
2. Build and tag:
   ```bash
   make release
   ```
3. GitHub Actions will:
   - Rebuild the deck
   - Upload `.apkg` files as **artifacts**
   - Create a **GitHub Release** with the `.apkg` attached

Your friends can download the latest deck directly from  
👉 [**GitHub → Releases**](../../releases)

---

## 🧰 CI/CD (GitHub Actions)

Every push and tag runs automatically on GitHub.

### 🔄 Workflow Summary

- **Push to main or open a PR** → builds `.apkg` and uploads as artifact  
- **Tag vX.Y.Z** → creates a release with the `.apkg` file attached  

Located in: `.github/workflows/build.yml`

---

## 🧠 Why Git Instead of AnkiWeb?

| Feature | Git Workflow | AnkiWeb |
|----------|---------------|---------|
| Version control | ✅ Full history | ❌ None |
| Collaboration | ✅ Branches + PRs | 🚫 Single maintainer |
| Offline | ✅ Works locally | ⚠️ Requires sync |
| Transparency | ✅ See every card diff | ❌ Hidden |
| Automation | ✅ CI/CD releases | ❌ Manual |

> 💡 This repo = “AnkiHub for engineers” — simple, reproducible, and free.

---

## 💙 Troubleshooting

| Problem | Fix |
|----------|------|
| `make` not recognized | Install via `choco install make` or run Python commands manually |
| PIP upgrade error | Already handled via `python -m pip` |
| Wrong tag like `v%VER%` | Fixed with `build/release_tag.py` |
| Cards truncated | Parser now preserves multi-line HTML (using CSV reader) |

---

## 🧩 Credits

Built by [**Sebastian Morsch**](https://github.com/Sebastian0211-vs)  
Deck powered by [`genanki`](https://github.com/kerrickstaley/genanki)

---

## 📜 License

MIT License © 2025 — Open-source, share freely and improve together.
