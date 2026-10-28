---
name: affinity-mapping
description: Synthesize interview transcripts into evidenced themes and user needs, then render an interactive HTML evidence map. Use when synthesizing interviews, affinity mapping, or preparing opportunities for discovery.
metadata:
  ready_to_publish: "true"
---

# Affinity Mapping: from transcripts to themes and opportunities

Turn raw user interviews into **structured themes and opportunities** (needs/pains/desires), ready to drop into an Opportunity Solution Tree. Every conclusion stays **evidenced** - it traces back to a verbatim quote and its source. Finish with a self-contained, interactive `affinity/map.html` that makes the evidence trail inspectable.

Respond and produce all artifacts in the user's conversation language.

Before extraction, read `references/writing-quality.md`. Apply it to all agent-authored observations, labels, opportunities, and summaries; preserve source quotes verbatim. Titles and previews must describe the actual person, situation, and need on their own. Check clarity again after shortening, before saving JSON, HTML, or a handoff; this skill owns that quality without depending on a separate editor.

## Core rule: TWO-STEP synthesis (and why it matters)

The most common mistake (human and AI alike) is to dump all transcripts in at once and write themes immediately. That loses nuance, smooths over outliers, and - with AI - burns context and produces hallucinated quotes.

Work in two steps, **and step 1 is sacred**:
1. **Per-transcript extraction** - read ONE interview, extract atomic observations (nuggets), write them to a file, move to the next. Never hold all transcripts in your head at once.
2. **Cross-interview clustering** - work ONLY from the nuggets file (small); do not return to the transcripts.

This is a quality rule and a token-economy rule at the same time: after extraction the raw transcripts leave the context, and clustering happens on a handful of one-line nuggets.

## Phase 0 - Setup

1. Establish a **focus question** - one question that disciplines the sort (e.g. "What stops new customers from finishing setup?"). The same data can be sorted 10 different ways; the question picks the right one. Write it at the top of the artifact.
2. Identify the transcripts (folder/files). Count them. Do not read their contents yet.

## Phase 1 - Per-transcript extraction (one at a time!)

For **each** transcript separately: read it, extract atomic nuggets, append them to `affinity/nuggets.md`. Then the next one. Do not read the next transcript before you have saved the nuggets from the previous one.

**Nugget = one observation + verbatim quote + source.** Format (one per line, ID for traceability):

```
- [A01] Could not tell whether the import had finished | "I sat there refreshing the page, I had no idea if it had worked" | Ana
- [A02] States price as the reason for stopping | "it was too expensive, that was the end of it" | Ana
```

Nugget rules (this is data quality - "garbage in, garbage out"):
- **Atomic** - one thought. A note with two thoughts = split it into two.
- **Evidence, not conclusion** - capture WHAT the user said/did, not your interpretation. "I didn't know what was selling" - NOT "has a control problem".
- **Quote is VERBATIM** - copied from the source, not paraphrased, not invented. If there is no verbatim quote, it is not a nugget. A hallucinated quote sounds smooth and is the most dangerous kind.
- **Source always** - persona/interviewee ID. Without a source a nugget is useless (it cannot be audited).
- IDs per interviewee (A=Ana, B=Ben...) make tracing easier.

Capture observations across the full spectrum: statements, behaviors, emotions, moments of pain, contradictions within a single interview. Do not filter for a thesis yet.

## Phase 2 - Cross-interview clustering (from the nuggets file only)

Now work **exclusively** from `affinity/nuggets.md`. The raw transcripts are no longer needed.

1. **Bottom-up, ZERO predefined buckets.** Do not start from a list of categories. Take nuggets and group those that share **meaning** (not keywords - "cost" in two nuggets can mean two different things). Themes must emerge from the data.
2. **Label a cluster ONLY once it has formed** - use a short, natural statement of the shared user behavior or problem, rather than a keyword topic or a fixed grammatical formula. Good: "Cannot tell whether an action succeeded". Bad: "Trust" / "Cost".
3. **Minimum two passes.** The first structure is a draft - go through it again, merge/split/move. A cluster of 1 nugget is a signal (set it aside), not a theme.

Write to `affinity/themes.md`:

```
## Theme: Cannot tell whether an action succeeded
Nuggets: A01, A05, B07, C03
```

## Phase 3 - Divergence pass (mandatory)

LLMs (and humans) drift toward the dominant narrative and smooth over exceptions. Deliberately make the opposite move:
- Which nuggets fit **NO** major theme? (the long tail - the best insight often lives there)
- Where do interviewees **differ** or **contradict each other**? (segment dependence)
- Where does one user's statement **clash** with behavior - their own or someone else's?
- What would you expect to see that is **missing** from the data?

Append a `## Divergence / exceptions` section to `themes.md`. Keep discrepancies visible - they are material.

## Phase 4 - Opportunities + traceability

Convert themes into Torres-style **opportunities** (the bridge to the OST). Detailed criteria and examples: `references/torres-opportunities.md` - read it before formulating.

In short:
- **Opportunity = need/pain/desire, NOT a solution.** In the customer's voice ("I want / I don't know / I'm afraid / I'm trying..."). Test: would the customer actually say this?
- **The "more than one way?" test** - if it can only be addressed one way, it is a solution in disguise. Ask "why?" and step up to the underlying need.

Final artifact `affinity/opportunities.md` - each opportunity with the full trail theme -> nuggets -> quotes -> source:

```
## Opportunity: "I don't know whether the thing I just did actually worked"
- Theme: Cannot tell whether an action succeeded
- More than one way? YES (confirmation screen, status log, email receipt, progress indicator...)
- Evidence:
  - A01 "I sat there refreshing the page..." (Ana)
  - B07 "..." (Ben)
- For whom / divergence: strong among first-time users; Chris is the opposite (checks a separate report, so he never notices)
```

Before presenting the synthesis, run the language and fidelity review in `references/writing-quality.md` on the Markdown artifacts. Resolve wording there before projecting it into JSON and HTML.

At the end, show the user the themes and opportunities and **ask before treating them as final** - naming themes and interpreting them belongs to the human; AI accelerates extraction and clustering, it does not take over judgment. Render the first map with `status: "draft"`; approval changes the status, not the underlying evidence.

The synthesized opportunities can feed the included `supersprint` skill for a full discovery cycle and growing tree. If an `ost-builder` skill is separately available and the user specifically wants a Teresa Torres Opportunity Solution Tree, it can also use these opportunities; do not require that optional skill.

## Phase 5 - Interactive evidence map (required)

Read `references/map-data.md` and `references/html-style.md`; use the packaged default HTML style. Build `affinity/map.json` strictly from `nuggets.md`, `themes.md`, and `opportunities.md`; this phase reformats the synthesis and must not reinterpret it.

The map must make four relationships visible:

1. Focus question -> themes.
2. Theme -> clustered nuggets.
3. Selected nugget -> verbatim quote + participant + source.
4. Theme + evidence -> opportunities, with divergences kept in a separate visible section.

Write the normalized data contract exactly as described in the reference, then render it with the bundled script:

```bash
python3 <this-skill-directory>/scripts/render_affinity_map.py affinity/map.json affinity/map.html
```

Treat these as the complete output set:

- `affinity/nuggets.md` - atomic evidence ledger.
- `affinity/themes.md` - clusters plus divergences.
- `affinity/opportunities.md` - interpreted needs with traceability.
- `affinity/map.json` - canonical machine-readable relationships.
- `affinity/map.html` - self-contained review view with no network dependencies.

After rendering:

1. Open `affinity/map.html` in the host app's built-in/in-app browser first, following the preview order in `references/map-data.md`; Chrome or another external browser is a fallback, not the default.
2. Verify that selecting at least one nugget updates its quote, source, theme, and linked opportunity.
3. Check the layout at desktop and narrow/mobile width; fix clipping or horizontal page overflow.
4. Report links to all five artifacts. Label the map as a draft until the user approves the synthesis.
5. If the host supports publishing HTML as an artifact, offer it as an optional next step. Keep the local HTML as the portable source of truth and do not publish without the user's approval.

## Guardrails
- Process transcripts one at a time - Phase 1 reads one and writes to disk before touching the next.
- Treat quotes as copies from the source - never invented, never a paraphrase presented as verbatim.
- Let labels emerge after clustering - start with zero predefined categories.
- Name clusters as natural statements of shared user behavior or problems, not features or keywords.
- Keep opportunities separate from solutions - if there is only one way to address it, dig deeper.
- Keep divergence visible - resist trading it away for a neat, coherent story.
- Never introduce or rewrite evidence while producing JSON or HTML - visualization is a projection, not a new synthesis pass.
- Keep the HTML self-contained - inline its data, CSS, and JavaScript; do not add CDNs, fetch calls, analytics, or external fonts.
- Keep the Markdown artifacts even when the HTML preview works - they remain the auditable, diffable record.
