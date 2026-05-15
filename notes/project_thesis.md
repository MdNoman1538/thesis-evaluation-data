---
name: Thesis project
description: Master's thesis "Semantic Stimuli Generation with LLMs" — scaffold, references, and open TODOs
type: project
originSessionId: bbbadae9-84a4-47b2-bba0-361434859e37
---
**Title:** Semantic Stimuli Generation with Large Language Models: A System for Augmenting Design Creativity
**Working folder:** `/Users/noman/Documents/Thesis/thesis writing/`
**Template:** University of Oulu `dithesis.cls` (classic BibTeX, NOT biber)
**Build recipe (LaTeX Workshop):** `pdflatex → bibtex → pdflatex × 2`
**Bibliography:** `citations.bib` — 42 entries; planned to be overwritten by Better BibTeX export from Zotero (user must pin citation keys first so `\cite{...}` keys keep matching).

**Chapter structure (in `Chapters/`):**
- `abstract.tex`, `foreword.tex`, `abbreviations.tex`
- `introduction.tex` — includes the "Author's Contributions and the Role of AI" section the Oulu guideline mandates
- `relatedwork.tex` — six themed sections
- `implementation.tex` — describes ImagenAndDescriptionV1 from actual code
- `experiments.tex` — evaluation strategy, has TODO markers for corpus
- `summary.tex` — discussion / limitations / future work / conclusion
- `appendices.tex` — three appendix slots
- `tiivistelma.tex` — Finnish abstract, currently NOT included from `main.tex`

**Why:** Topic is AI-controlled stimuli generation to help designers avoid fixation; the user's app is the central artifact, and the thesis must align with Oulu's guideline (including the AI-use disclosure section).

**How to apply:** Preserve class-specific macros (`\header{...}`, `\biblanguage`, `\signature`, the `abstract` environment). Don't switch to biber. Don't touch `dithesis.cls`, `di.sty`, `di_eng.bst`, `di_fin.bst`, `Figures/`.

**Open TODOs left for the user (as of last session):**
1. Five `citations.bib` entries flagged `TODO: authors` — IdeationWeb, AIdeation, Expandora, UX2024CHI, plus one more.
2. Several `% TODO:` blocks across chapters (abstract numbers, evaluation corpus details).
3. Architecture diagram needed at `Figures/architecture.pdf`.
4. Install MacTeX (`brew install --cask mactex`) if not already.
5. Decide on Overleaf sync via `git init` + Overleaf premium git bridge — not started.
