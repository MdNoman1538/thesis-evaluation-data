---
name: Challenges and resolutions log (Apr 9 – May 9)
description: Chronological list of problems encountered, upgrades requested, and how each was resolved across all prior Claude sessions
type: project
originSessionId: bbbadae9-84a4-47b2-bba0-361434859e37
---
Aggregated from 14 Claude session transcripts spanning Apr 9 → May 9, 2026, across the Imagen 3 copy / Stimuli-and-image-v2 / ImagenAndDescriptionV1 / thesis-writing workspaces.

## Phase 1 — Initial deployment & throughput (Apr 9 morning)

**Problem:** App needed to run on a Windows PC (Mengru's machine).
**Resolution:** Provided requirements.txt and venv install steps.

**Problem:** Image generation was sequential and slow.
**Resolution:** Parallelized image generation into 5 concurrent calls (one per stimulus sentence). This is the pattern that survives into the current `image_generator.py`.

## Phase 2 — Cost & latency optimization (Apr 9 afternoon, Stimuli-and-image-v2 fork)

**Problem:** Sending every chat turn to the Pro model was expensive.
**Resolution proposals discussed:**
- *Model cascading* — Flash for edits, Pro for new designs (10–20× cheaper for the edit path).
- *Context caching* — cache the system prompt via `client.caches.create()` to cut input tokens 75–90%.
- *UI-driven intent* — separate "New Design" vs "Refine Current" buttons so a Flash router never needs to classify intent.

**Resolution implemented:** All three. The edit-vs-new routing landed in `gemini_client.chat()` with an `is_edit` flag; Flash cache via `_get_or_create_flash_cache()`.

**Problem:** Image generation timed out at 180 s.
**Resolution:** Split pipeline so text returns in 3–5 s (user reads suggestions), image loads async in 10–60 s. Increased image-side timeout to 300 s. Added progressive retry (3 attempts with simplified prompts).

**Problem:** User reported semantic drift / hallucination concerns when conversation history is trimmed.
**Resolution:** Confirmed concern and avoided aggressive trimming; relied on caching instead.

## Phase 3 — Persistent UI + image carousel (Apr 9 afternoon)

**Problem:** UI showed "generating…" placeholders that disrupted flow during edits.
**Resolution:** Frontend `imageHistory[]` array; the last image stays visible until a new one arrives, then replaces it. Left/right arrows navigate prior versions.

**Problem:** Generated images weren't persisted.
**Resolution:** Save every image to a session-specific folder; carousel reads from that folder.

## Phase 4 — Reliability tooling (Apr 9 → Apr 11)

**Problem:** Images failed sporadically; root cause was unclear.
**Resolution:** New `prompt_tracker.py` with SQLite logging of every attempt (success/failure with prompt). `get_failed_fragments()` finds words appearing in failures but not successes; `auto_fix_prompt()` strips historically-blocked tokens before retry.

**Problem:** Each session had to re-warm the system prompt cache.
**Resolution:** `POST /session/prewarm` called when user picks design type; runs cache creation while user is still filling the form.

## Phase 5 — Image aesthetic / NC vs VC visual coupling (Apr 9 evening → Apr 11 → Apr 28)

**Problem:** Generated images didn't carry the right aesthetic — user wanted black-and-white, 2:1 composite, monochromatic, no recognizable product silhouettes.
**Resolution:** Built the master image template — pure-white background, high-key grayscale, "task blindness" rule (no full product shapes), 2:1 panel composition with NC on left and VC on right. This template anchors `image_system_prompt.py`.

**Problem:** NC and VC images looked different in *structure* (composition/lighting/framing) instead of just along the abstraction axis.
**Resolution:** Image system prompt was rewritten as a "deterministic visual-prompt translator" — takes paired NC+VC sentences, outputs JSON with two prompts that share the *same scene skeleton* (composition, camera, lighting, background) and differ only along (1) object specificity and (2) rendering detail. The supporting elements are word-for-word identical.

**Problem:** Two images were being generated when only one was wanted (per-sentence).
**Resolution:** Identified that the prompt template described a two-panel composite while code called it once per sentence. Fixed by having the prompt describe one level only and passing the level parameter properly.

**Problem:** Contradictions inside the image system prompt (Section 2 said NC+VC have same realistic rendering, Section 5 still had NC use abstract physics language).
**Resolution:** Aligned all sections to unified realistic rendering with the two-axes split.

**Problem:** Per-image timeout was a guess.
**Resolution:** Recorded actual generation times for 10 sessions; set timeout to 1.5× the average successful generation time. Eventually `GEMINI_HARD_TIMEOUT_S` in current config.

## Phase 6 — Geography / model availability (Apr 28 onwards) ⚠️ load-bearing

**Problem (load-bearing):** Image generation suddenly failed with `400 FAILED_PRECONDITION: Image generation is not available in your country.` on `gemini-3.1-pro-preview` and `imagen-3.0-generate-002`.
**Cause:** Geographic restriction — these models are not served in every country. Mengru / the Politecnico di Milano collaborator are in Italy; Md Noman is in Finland. Different model availability per country.
**Resolution:** Built a model-fallback chain that tries multiple models in order. The current chain in `config.py`:
- Text: `gemini-3.1-pro-preview` → `gemini-3-pro-preview` → `gemini-3-flash-preview` → `gemini-2.5-pro` → `gemini-2.5-flash`
- Image: `gemini-3-pro-image-preview` → `gemini-3.1-flash-image-preview` → `gemini-2.5-flash-image` → `imagen-4.0-generate-001`

**This is the actual technical reason the system has fallback chains — it's not generic resilience, it's geography.** The thesis Implementation chapter's "engineering challenges" section should explain this.

## Phase 7 — Per-call vs per-batch model selection (May 6–7)

**Problem:** When the first image failed and the system fell back to a different model, subsequent images for the same batch *also* re-tried the failing model first instead of staying on the working one.
**Resolution:** Pre-flight model probe — when the user clicks Generate, the system runs a fast/low-quality test generation on each candidate model in the chain to pick a working text model and a working image model *up front*. The chosen models are then locked for the rest of the batch. This is what `gemini_client.select_text_model()` and the parallel image-model probe in `routes.py /generate-images` do.

**Problem:** Same: "do not retry failed models again and again."
**Resolution:** Same pre-flight + lock-in pattern.

## Phase 8 — Stimulus methodological refinements (May 7–8)

**Problem:** The locked five-aspect template wasn't enough — across NC/MC/VC, the *number of words per noun phrase* drifted, breaking the "only abstraction differs" invariant.
**Resolution:** Added **Rule 8: Strict Word-Count Parity via Noun Length Matching** to the system prompt. For every noun slot N1–N25, the noun phrase must have the same number of words across the three conditions. Hyphenated compounds allowed when needed. ±2 word tolerance per paragraph maximum.

**Resolution mechanics added:**
- **Step 3b** internal noun table with target word count per slot.
- **Step 11** final word-count verification — paragraph-level word counts must be within ±2.

**Problem:** When a noun changes NC → MC → VC, sometimes it pointed to a different design concern — breaking semantic alignment.
**Resolution:** Added the rule that NC, MC, VC nouns at the same slot must point to the *same* underlying design concern, just at different abstraction levels. Verification step asks: "Does NC Sentence 3 make the designer think about the same sub-problem as VC Sentence 3?"

## Phase 9 — Concreteness measurement upgrades (May 8)

**Problem:** Brysbaert concreteness lookup didn't recognize many words (incomplete vocabulary).
**Resolution:** Loaded the **full 40,000-word Brysbaert dataset** into `semantic_analyzer/brysbaert_data.py`.

**Question:** Should Brysbaert score be normalized to 0–1, or kept as the original 1–5 scale?
**Resolution:** Keep original 1–5 score in the `.mat` output for academic reporting; UI may show normalized.

**Problem:** A single concreteness measure isn't enough.
**Resolution:** Added two methods to compute abstraction level — **WordNet hypernym depth** (ontological hierarchy) alongside the **Brysbaert Concreteness Index**. The semantic analyzer now reports both, letting NC vs VC separation be checked against two independent measures.

## Phase 10 — Semantic analyzer integration (May 8)

**Problem:** The user had two separate apps — the stimulus generator and the standalone semantic analyzer — and wanted them tied together.
**Resolution:** Integrated the analyzer into the main app. After generation, a button in the UI opens the analyzer view (or runs it on a separate port) so generated stimuli can be inspected immediately. Limited to NC vs VC analysis (MC dropped from this view per the user's request: "I will only need nc vs vc analysis").

## Phase 11 — Thesis scaffolding (May 8 evening)

(Already documented in `reference_prior_session.md`.) LaTeX template setup, citations.bib, chapter skeletons.

---

## Cross-cutting upgrades that survived into the current system

| Upgrade | Why it was needed | Where it lives now |
|---|---|---|
| Pre-flight model probe | Geographic + sporadic failures wasted minutes per batch | `gemini_client.select_text_model()`, `/generate-images` parallel probe |
| Multi-tier fallback chain | Country restrictions on Gemini 3.x models | `config.py` `*_FALLBACK`, `*_FALLBACK_2` |
| Hard timeout + recorded average | 180 s default was wrong; real distribution unknown | `GEMINI_HARD_TIMEOUT_S`, `image_gen_timings.jsonl` |
| Image system prompt as deterministic translator | NC/VC pairs diverged on composition, not just abstraction | `image_system_prompt.py` (the JSON-output version) |
| 40k Brysbaert + WordNet hypernym depth | Single index missed many words, single-method risky | `semantic_analyzer/brysbaert_data.py`, `semantic_analyzer/main.py` |
| Rule 8: Word-count parity | Noun length drift broke the "only abstraction differs" invariant | `system_prompt.py` |
| Same-design-concern noun alignment | NC/VC at same slot pointing to different sub-problems broke comparability | `system_prompt.py` |
| Session-scoped JSONL logs | Reproducibility / auditability for research use | `logger.py`, `stimuli_log.jsonl`, `image_gen_timings.jsonl` |
| Image carousel + persistence | Earlier iterations needed to remain visible across edits | `static/index.html` (front-end), `generated_images/` |
| BLUEPRINT + TECHNOLOGY docs | Fork (Stimuli-and-image-v2 / DesignStudio) needed reproduction spec | Stimuli-and-image-v2 only |

## Implications for the thesis "Implementation Notes and Challenges" section (currently TODO at `Chapters/implementation.tex:59`)

This phase log is the answer to that section. Concrete sub-sections to write:
1. **Geographic model availability** — why the fallback chain exists and how the pre-flight probe works.
2. **Word-count parity (Rule 8)** — methodological consequence: word-length drift confounds abstraction-level manipulation.
3. **Image-prompt determinism** — separating object specificity from rendering detail; shared scene skeleton.
4. **Concreteness measurement triangulation** — Brysbaert + WordNet hypernym depth, why both.
5. **Timeout and retry economics** — empirical timing vs. fixed timeouts, prompt sanitization via `prompt_tracker`.
