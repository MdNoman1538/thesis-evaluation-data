---
name: Why Gemini was chosen
description: Real reason for the Gemini selection — qualitative evaluation by three domain experts, not purely empirical from testBench
type: project
originSessionId: bbbadae9-84a4-47b2-bba0-361434859e37
---
The 20-model comparison in `testBench/exports/stimuli_all_models_*` files (Apr 1–4) ruled out failing models structurally, but the **final choice of Gemini was made on the basis of qualitative evaluation by three people, not on automated metrics**:

1. **Dr. Georgi Georgiev** — the user's supervisor (University of Oulu)
2. **Mengru** — collaborator the app was originally built for; she was using it for her own research
3. **A professor at Politecnico di Milano** — assisted the project from the Italian side

These three reviewers found Gemini's outputs "most satisfactory" compared to OpenAI/Claude/Grok candidates.

**Why:** This is the actual decision basis. The thesis can lean on the testBench artefacts to show *that* a wide comparison was conducted, but the rationale paragraph should acknowledge the human-evaluation step rather than imply a purely empirical metric drove the choice.

**How to apply:** When writing the model-selection subsection of the thesis (likely in Chapter 3 Implementation, or a methodology subsection), present the testBench logs as evidence of breadth, then state explicitly that final selection was via expert qualitative evaluation by the three named reviewers. Do *not* fabricate quantitative scores or rubrics that weren't actually run.

**Open question for user when ready to write:** Mengru's full name, role, institution; and the Politecnico di Milano professor's name — both will likely need to be acknowledged either in the foreword or in the "Author's Contributions" section of the introduction.
