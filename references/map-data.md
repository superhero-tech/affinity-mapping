# Affinity map data contract

Read this in Phase 5 before writing `affinity/map.json`. The JSON is the normalized, machine-readable projection of the approved Markdown artifacts. Do not add claims, quotes, participants, or relationships while creating it.

## Required structure

```json
{
  "focus_question": "What stops new customers from finishing setup?",
  "description": "Optional one-line scope note.",
  "language": "en",
  "status": "draft",
  "participants": [
    {
      "id": "A",
      "label": "Participant A",
      "source": "interviews/transcripts/A.md"
    },
    {
      "id": "B",
      "label": "Participant B",
      "source": "interviews/transcripts/B.md"
    }
  ],
  "nuggets": [
    {
      "id": "A01",
      "observation": "Refreshes the screen because the import has no visible status.",
      "quote": "I sat there refreshing the page. I had no idea if it had worked.",
      "participant_id": "A",
      "source": "interviews/transcripts/A.md"
    },
    {
      "id": "B07",
      "observation": "Waits because no completion message appears.",
      "quote": "I waited because I expected a confirmation to show up.",
      "participant_id": "B",
      "source": "interviews/transcripts/B.md"
    }
  ],
  "themes": [
    {
      "id": "T01",
      "label": "Cannot tell whether an action succeeded",
      "nugget_ids": ["A01", "B07"]
    }
  ],
  "opportunities": [
    {
      "id": "O01",
      "statement": "I want to know whether the thing I just did actually worked.",
      "theme_id": "T01",
      "nugget_ids": ["A01", "B07"],
      "more_than_one_way": true,
      "segment_note": "Strongest among first-time users."
    }
  ],
  "divergences": [
    {
      "type": "Exception",
      "summary": "One participant always checks a separate report and never waits for status here.",
      "nugget_ids": ["C03"]
    },
    {
      "type": "Missing signal",
      "summary": "Nobody spontaneously mentioned setup duration.",
      "nugget_ids": []
    }
  ]
}
```

The example demonstrates shape only. Never copy its participants, observations, or quotes into a real project.

## Integrity rules

- Copy every `quote` verbatim from `affinity/nuggets.md`; never shorten or polish it for the visualization.
- Keep participant, nugget, theme, and opportunity IDs stable across Markdown, JSON, and any later OST.
- Assign each nugget to at most one theme. Keep unclustered nuggets in `nuggets` but out of every theme; surface the important ones as divergences.
- Give every theme at least two nuggets. A singleton is a signal, not a theme.
- Link an opportunity only to nuggets in its own theme.
- Set `more_than_one_way` to `true` only after applying the opportunity-vs-solution test. The renderer rejects disguised solutions.
- Use `status: "draft"` until the user reviews the interpretation. After approval, change it to `reviewed` and render again.
- Put file paths in `source`; do not use machine-specific absolute paths unless the user's source files are outside the project.

## Interface language

The renderer includes English (`en`) and Polish (`pl`) labels. For another language, add a complete `ui` object with these keys:

`title`, `nuggets`, `themes`, `opportunities`, `participants`, `evidence_path`, `transcript`, `nugget`, `theme`, `opportunity`, `source`, `divergences`, `counterevidence`, `signal`, `related_evidence`, `draft`, `reviewed`, `no_divergence`.

## Preview and visual checks

For generated HTML artifacts, use the host app's built-in/in-app browser as the primary preview and for visual/interaction checks. Open a visible browser tab through the host's supported capability and verify that it loaded; a file link, editor tab, or queued open request alone is not a confirmed preview. Use Chrome or another external browser only when the in-app browser is unavailable, cannot display the artifact, or lacks a required inspection capability; briefly explain that fallback and keep the in-app preview primary when possible. Honor an explicit user browser choice. If the host blocks access by policy, report the limitation rather than bypassing it through another browser or route.

## Rendering

Run from the user's project, using the actual path to this skill:

```bash
python3 <affinity-mapping-skill>/scripts/render_affinity_map.py affinity/map.json affinity/map.html
```

The renderer uses only the Python standard library. It validates IDs and relationships, escapes transcript content, and emits one self-contained HTML file with inline CSS and JavaScript. It does not make network requests.
