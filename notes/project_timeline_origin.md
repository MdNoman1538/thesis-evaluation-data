---
name: Project timeline origin (Mar 20 – Apr 4)
description: How the project actually began — predecessor tool, kickoff meeting, structure evolution from Mengru's manual draft to the 5-sentence FBS framework
type: project
originSessionId: bbbadae9-84a4-47b2-bba0-361434859e37
---
The thesis project did not start at testBench (Apr 1). It started at a kickoff meeting on **Mar 25, 2026** with materials Mengru already had from her prior research. Reconstruction from chat record:

**Mar 20** — Md Noman shipped Mengru a stop-gap predecessor tool, `conversation-analyzer-main.zip`, with `RUN_UI_WINDOWS.md` and `APP_SUMMARY_AND_USAGE.md` install/usage docs. "After I arrive, we will make a new app." So a *predecessor app exists* and could be referenced as "previous work the candidate had built" if the thesis benefits from a brief mention.

**Mar 22** — Mengru: *"I have almost ready version of the semantic stimuli."* So the **stimulus material existed before the system did**. The thesis is a system *to operationalize* an existing research methodology, not to invent one from scratch.

**Mar 25 (kickoff meeting)** — Mengru sent two design tasks (Peanut Sheller, Amphibious Bike) with NC and VC stimuli already drafted, in two lengths (91-word "short" and longer "expanded"). Both versions structured as flowing paragraphs in 7 sentences. Her instruction: *"two conditions only should differ on abstraction level"* and *"they have same number of nouns"*. The semantic analyzer was used to *verify* this constraint; `analysis_*.mat` files in the chat are noun-count outputs. **Mar 25 5:01 PM**, Mengru posted the first locked-structure template:

> [Subject] can integrate [Element A] and [Element B] to create [Adjective] [Tools] for [Action] [Target Object]. These [Tools] allow [Users] to easily [Process Action] [Material] through a [Container]. Components like [Component 1], [Component 2], and [Component 3] can be utilized to guarantee [Target Object] is [Processed] without destroying the [Inner Core]. [Framework] provides stability, whether [Operating Method 1] or [Operating Method 2]. Built using [Material Types], it ensures [Manufacturing/Cost Requirement]. Different ways of interacting with the [Tool], like [Interaction 1] or [Interaction 2], offer [Benefit], delivering a [Adjective] experience.

This is the **proto-structure** — predates the FBS-mapped 5-sentence form by a week.

**Mar 26** — Md Noman shipped `sememtic analyzer.zip` (a spaCy-based noun-counter, separate from the stimulus generator that came later). Mengru posted a clearer structure spec:

> 1. The tool should understand design task — input of design and requirements.
> 2. Generate text feedback/stimuli with: 1 sentence overall design background, 1 sentence specific to task, 1 sentence per requirement, 2 sentences on design creativity.

Md Noman replied with a more elaborate framing — *"The Cognitive Design Engine: A Systematic Framework Integrating Double Diamond, SCAMPER, and TRIZ with Generative AI for Design Ideation"* — which **was not adopted**; Mengru's tighter brief won.

**Mar 30** — Mengru gifted Md Noman a Claude subscription via `claude.ai/gift` (this is how the work was tooled). Worth acknowledging in foreword if Claude was a meaningful part of the development workflow.

**Mar 31 11:37 AM (formal project brief, in Mengru's own words):**
> *"AI-stimuli generation system to generate 2 types of stimuli : text vs. image. Each type has two conditions: abstract vs. concrete."*

Note: project began as a **2x2 design (text/image × abstract/concrete)**. The MC (moderately concrete) condition was added later, expanding to 2x3. The thesis text should reflect this evolution honestly — early scope was 4 cells, became 6.

**Mar 31 11:44 AM, Mengru's structure:**
> *"1) one sentence about design skill. 2) 3 sentences about the design task. 3) one sentence for each requirement. 4) one sentence for design creativity (usefulness, surprise, novelty)."*

This adds up to ~9 sentences for a task with 4 requirements — matches the "9 sentences expected" in the Apr 1 testBench multi-model exports.

**Mar 31 11:47 AM, the controllability principle (already present here, refined further on Apr 2):**
> *"Text stimuli: 2 conditions should have the same sentence number, and the same structure for each sentence, the only difference is the abstraction level of the nouns. And the nouns used in the sentence keep at the same level of familiarity in daily use … often-used words … sentence should make sense and be easy to understand."*

Two operating constraints worth quoting in the methodology section: (a) only nouns vary across conditions; (b) noun familiarity must stay constant.

**Mar 31 noon** — Mengru sent foundational materials: `DesignTasks&Sitimuli8_English version.docx` and `materials.docx`. These are the **research materials her work draws on** — the thesis should reference these as the empirical anchor.

**Mar 31 10:18 PM** — first prototype delivered same day: `Design Stimulus Generator.htm`, several models tested.

**Apr 1 2:05 PM** — Mengru shared **three additional design tasks**: assistive writing device for children with fine motor disabilities; interactive educational toy for preschoolers; innovative furniture for student collaborative learning. Each had NC/MC/VC stimuli already drafted (the MC condition appears here — this is where the 2x3 design crystallized). These tasks were **not** carried into testBench (which used Peanut Sheller, Amphibious Bike, and a "social-oriented furniture" task). Possible scope-pruning decision worth confirming with the user.

**Apr 2 onwards** — switched to the 5-sentence FBS-grounded structure (Pahl-Beitz / Norman / Ulrich-Eppinger). This is the **structural pivot** that changed the methodology from a 7–9-sentence flowing-paragraph form into the rigid 5-aspect locked template.

---

## Why this matters for the thesis

1. **Author's contribution clarification.** The system is built on a methodology that pre-existed in Mengru's research practice. The contribution is implementation, automation, reproducibility tooling, and the empirical evaluation.
2. **Methodology section** can credibly trace the structure's evolution: paragraph form (Mar 25) → 9-sentence skill+task+req+creativity (Mar 31) → 5-sentence FBS-locked (Apr 2). This is an honest, well-documented design process.
3. **Scope statement in Introduction** should acknowledge: original brief was 2x2 (text/image × NC/VC), expanded to 2x3 with MC added. The Apr 1 batch of additional design tasks (writing device, educational toy, furniture) was either deferred or pruned — clarify with user.
4. **References to add to bib:** Pahl & Beitz (2007); Norman, *The Design of Everyday Things* (2013); Ulrich & Eppinger, *Product Design and Development* (2015); Gero (1990) Function-Behavior-Structure framework; **and** Mengru Wang's prior published work that contains the original NC/VC stimuli (ask user for citation).

## Secrets exposed in chat — flag for rotation
- Mengru's Gemini API key (Apr 2 1:21 PM)
- Md Noman's OpenAI API key (Mar 26 7:17 PM)
- Both appear in plaintext in the chat history. Treat as compromised; rotate in the respective consoles.
