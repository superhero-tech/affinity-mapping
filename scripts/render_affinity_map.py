#!/usr/bin/env python3
"""Render a self-contained affinity evidence map from normalized JSON."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_UI = {
    "en": {
        "title": "Evidence map",
        "nuggets": "nuggets",
        "themes": "themes",
        "opportunities": "opportunities",
        "participants": "participants",
        "evidence_path": "Evidence path",
        "transcript": "Transcript",
        "nugget": "Nugget",
        "theme": "Theme",
        "opportunity": "Opportunity",
        "source": "Source",
        "divergences": "Divergences and exceptions",
        "counterevidence": "What does not fit the dominant story",
        "signal": "Signal",
        "related_evidence": "Related evidence",
        "draft": "Draft — human review required",
        "reviewed": "Human-reviewed",
        "no_divergence": "No divergence recorded",
    },
    "pl": {
        "title": "Mapa dowodów",
        "nuggets": "Nuggety",
        "themes": "Tematy",
        "opportunities": "Szanse",
        "participants": "Rozmówcy",
        "evidence_path": "Ścieżka dowodu",
        "transcript": "Transkrypt",
        "nugget": "Nugget",
        "theme": "Temat",
        "opportunity": "Szansa",
        "source": "Źródło",
        "divergences": "Rozbieżności i wyjątki",
        "counterevidence": "Co nie pasuje do dominującej historii",
        "signal": "Sygnał",
        "related_evidence": "Powiązane dowody",
        "draft": "Wersja robocza — wymaga oceny człowieka",
        "reviewed": "Zatwierdzone przez człowieka",
        "no_divergence": "Nie zapisano rozbieżności",
    },
}

REQUIRED_UI_KEYS = set(DEFAULT_UI["en"])


def fail(message: str) -> None:
    raise ValueError(message)


def expect_list(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key)
    if not isinstance(value, list):
        fail(f"{key} must be a list")
    if any(not isinstance(item, dict) for item in value):
        fail(f"every item in {key} must be an object")
    return value


def expect_text(item: dict[str, Any], key: str, context: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"{context}.{key} must be a non-empty string")
    return value.strip()


def unique_index(items: list[dict[str, Any]], collection: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for position, item in enumerate(items):
        item_id = expect_text(item, "id", f"{collection}[{position}]")
        if item_id in result:
            fail(f"duplicate {collection} id: {item_id}")
        result[item_id] = item
    return result


def string_ids(value: Any, context: str, *, minimum: int = 0) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        fail(f"{context} must be a list of non-empty strings")
    result = [item.strip() for item in value]
    if len(result) < minimum:
        fail(f"{context} must contain at least {minimum} item(s)")
    if len(result) != len(set(result)):
        fail(f"{context} contains duplicate ids")
    return result


def validate(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        fail("map data must be a JSON object")
    focus_question = expect_text(data, "focus_question", "root")
    language = data.get("language", "en")
    if not isinstance(language, str) or not language.strip():
        fail("root.language must be a non-empty language code")
    language = language.lower().split("-")[0]
    status = data.get("status", "draft")
    if status not in {"draft", "reviewed"}:
        fail("root.status must be 'draft' or 'reviewed'")

    participants = expect_list(data, "participants")
    nuggets = expect_list(data, "nuggets")
    themes = expect_list(data, "themes")
    opportunities = expect_list(data, "opportunities")
    divergences = expect_list(data, "divergences")
    if not participants:
        fail("participants must not be empty")
    if not nuggets:
        fail("nuggets must not be empty")
    if not themes:
        fail("themes must not be empty")

    participant_by_id = unique_index(participants, "participants")
    nugget_by_id = unique_index(nuggets, "nuggets")
    theme_by_id = unique_index(themes, "themes")
    opportunity_by_id = unique_index(opportunities, "opportunities")

    for participant_id, participant in participant_by_id.items():
        expect_text(participant, "label", f"participants.{participant_id}")
        expect_text(participant, "source", f"participants.{participant_id}")

    for nugget_id, nugget in nugget_by_id.items():
        expect_text(nugget, "observation", f"nuggets.{nugget_id}")
        expect_text(nugget, "quote", f"nuggets.{nugget_id}")
        participant_id = expect_text(nugget, "participant_id", f"nuggets.{nugget_id}")
        if participant_id not in participant_by_id:
            fail(f"nuggets.{nugget_id}.participant_id references unknown participant: {participant_id}")
        if "source" in nugget:
            expect_text(nugget, "source", f"nuggets.{nugget_id}")

    nugget_theme: dict[str, str] = {}
    for theme_id, theme in theme_by_id.items():
        expect_text(theme, "label", f"themes.{theme_id}")
        nugget_ids = string_ids(theme.get("nugget_ids"), f"themes.{theme_id}.nugget_ids", minimum=2)
        for nugget_id in nugget_ids:
            if nugget_id not in nugget_by_id:
                fail(f"themes.{theme_id}.nugget_ids references unknown nugget: {nugget_id}")
            if nugget_id in nugget_theme:
                fail(f"nugget {nugget_id} belongs to more than one theme")
            nugget_theme[nugget_id] = theme_id

    for opportunity_id, opportunity in opportunity_by_id.items():
        expect_text(opportunity, "statement", f"opportunities.{opportunity_id}")
        theme_id = expect_text(opportunity, "theme_id", f"opportunities.{opportunity_id}")
        if theme_id not in theme_by_id:
            fail(f"opportunities.{opportunity_id}.theme_id references unknown theme: {theme_id}")
        nugget_ids = string_ids(
            opportunity.get("nugget_ids"), f"opportunities.{opportunity_id}.nugget_ids", minimum=1
        )
        for nugget_id in nugget_ids:
            if nugget_id not in nugget_by_id:
                fail(f"opportunities.{opportunity_id}.nugget_ids references unknown nugget: {nugget_id}")
            if nugget_theme.get(nugget_id) != theme_id:
                fail(
                    f"opportunities.{opportunity_id} references nugget {nugget_id} "
                    f"outside theme {theme_id}"
                )
        if opportunity.get("more_than_one_way") is not True:
            fail(f"opportunities.{opportunity_id}.more_than_one_way must be true")
        if "segment_note" in opportunity:
            expect_text(opportunity, "segment_note", f"opportunities.{opportunity_id}")

    for position, divergence in enumerate(divergences):
        expect_text(divergence, "type", f"divergences[{position}]")
        expect_text(divergence, "summary", f"divergences[{position}]")
        nugget_ids = string_ids(divergence.get("nugget_ids", []), f"divergences[{position}].nugget_ids")
        for nugget_id in nugget_ids:
            if nugget_id not in nugget_by_id:
                fail(f"divergences[{position}].nugget_ids references unknown nugget: {nugget_id}")

    ui_overrides = data.get("ui", {})
    if not isinstance(ui_overrides, dict) or any(not isinstance(key, str) for key in ui_overrides):
        fail("root.ui must be an object of string overrides")
    if any(not isinstance(value, str) or not value.strip() for value in ui_overrides.values()):
        fail("every root.ui value must be a non-empty string")
    if language not in DEFAULT_UI and not REQUIRED_UI_KEYS.issubset(ui_overrides):
        missing = ", ".join(sorted(REQUIRED_UI_KEYS - set(ui_overrides)))
        fail(f"unsupported language '{language}'; provide all root.ui labels. Missing: {missing}")

    return {
        **data,
        "focus_question": focus_question,
        "language": language,
        "status": status,
        "participants": participants,
        "nuggets": nuggets,
        "themes": themes,
        "opportunities": opportunities,
        "divergences": divergences,
        "participant_by_id": participant_by_id,
        "nugget_by_id": nugget_by_id,
        "theme_by_id": theme_by_id,
        "opportunity_by_id": opportunity_by_id,
        "nugget_theme": nugget_theme,
    }


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def safe_json(value: Any) -> str:
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render(data: dict[str, Any]) -> str:
    language = data["language"]
    ui = {**DEFAULT_UI.get(language, DEFAULT_UI["en"]), **data.get("ui", {})}
    participant_by_id = data["participant_by_id"]
    nugget_by_id = data["nugget_by_id"]
    theme_by_id = data["theme_by_id"]
    opportunities_by_theme: dict[str, list[dict[str, Any]]] = {theme_id: [] for theme_id in theme_by_id}
    opportunities_by_nugget: dict[str, list[dict[str, Any]]] = {nugget_id: [] for nugget_id in nugget_by_id}
    for opportunity in data["opportunities"]:
        opportunities_by_theme[opportunity["theme_id"]].append(opportunity)
        for nugget_id in opportunity["nugget_ids"]:
            opportunities_by_nugget[nugget_id].append(opportunity)

    theme_sections: list[str] = []
    trace_records: dict[str, dict[str, str]] = {}
    first_nugget_id = data["themes"][0]["nugget_ids"][0]
    for theme in data["themes"]:
        theme_id = theme["id"]
        nugget_ids = theme["nugget_ids"]
        coverage = sorted({nugget_by_id[nugget_id]["participant_id"] for nugget_id in nugget_ids})
        note_buttons: list[str] = []
        for nugget_id in nugget_ids:
            nugget = nugget_by_id[nugget_id]
            participant = participant_by_id[nugget["participant_id"]]
            linked_opportunities = opportunities_by_nugget[nugget_id]
            opportunity_text = " · ".join(
                f'{opportunity["id"]} — {opportunity["statement"]}' for opportunity in linked_opportunities
            ) or "—"
            source = nugget.get("source", participant["source"])
            trace_records[nugget_id] = {
                "quote": nugget["quote"],
                "source": f'{participant["id"]} · {participant["label"]} · {source}',
                "observation": f'{nugget_id} · {nugget["observation"]}',
                "theme": f'{theme_id} · {theme["label"]}',
                "opportunity": opportunity_text,
            }
            note_buttons.append(
                '<button type="button" class="note" data-nugget="{id}" aria-pressed="{pressed}">'
                '<strong>{id}</strong><span>{observation}</span></button>'.format(
                    id=esc(nugget_id),
                    pressed="true" if nugget_id == first_nugget_id else "false",
                    observation=esc(nugget["observation"]),
                )
            )

        opportunity_items = "".join(
            '<li><span>{id}</span><q>{statement}</q>{segment}</li>'.format(
                id=esc(opportunity["id"]),
                statement=esc(opportunity["statement"]),
                segment=(
                    f'<small>{esc(opportunity["segment_note"])}</small>'
                    if opportunity.get("segment_note")
                    else ""
                ),
            )
            for opportunity in opportunities_by_theme[theme_id]
        )
        if not opportunity_items:
            opportunity_items = "<li>—</li>"
        theme_sections.append(
            '<section class="theme" aria-labelledby="theme-{id}">'
            '<header><span>{id} · {coverage}</span><h2 id="theme-{id}">{label}</h2></header>'
            '<div class="notes">{notes}</div>'
            '<div class="opportunity-list"><h3>{opportunities}</h3><ul>{items}</ul></div>'
            "</section>".format(
                id=esc(theme_id),
                coverage=esc(", ".join(coverage)),
                label=esc(theme["label"]),
                notes="".join(note_buttons),
                opportunities=esc(ui["opportunities"]),
                items=opportunity_items,
            )
        )

    divergence_rows = "".join(
        "<tr><td>{type}</td><td>{summary}</td><td>{evidence}</td></tr>".format(
            type=esc(divergence["type"]),
            summary=esc(divergence["summary"]),
            evidence=esc(", ".join(divergence.get("nugget_ids", [])) or "—"),
        )
        for divergence in data["divergences"]
    )
    if not divergence_rows:
        divergence_rows = f'<tr><td colspan="3">{esc(ui["no_divergence"])}</td></tr>'

    first = trace_records[first_nugget_id]
    status_label = ui[data["status"]]
    page_title = f'{ui["title"]} — {data["focus_question"]}'
    body = "".join(theme_sections)
    embedded_data = safe_json(trace_records)

    template = """<!doctype html>
<html lang="{{LANG}}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{PAGE_TITLE}}</title>
  <style>{{STYLE}}</style>
</head>
<body>
  <main class="page" id="affinity-map">
    <header class="masthead">
      <div><div class="eyebrow">{{TITLE}}</div><h1>{{FOCUS}}</h1><p class="focus">{{DESCRIPTION}}</p></div>
      <div class="status">{{STATUS}}</div>
    </header>
    <section class="stats" aria-label="Summary">
      <div class="stat"><strong>{{NUGGET_COUNT}}</strong><span>{{NUGGETS}}</span></div>
      <div class="stat"><strong>{{THEME_COUNT}}</strong><span>{{THEMES}}</span></div>
      <div class="stat"><strong>{{OPPORTUNITY_COUNT}}</strong><span>{{OPPORTUNITIES}}</span></div>
      <div class="stat"><strong>{{PARTICIPANT_COUNT}}</strong><span>{{PARTICIPANTS}}</span></div>
    </section>
    <section class="workspace" aria-label="Affinity map and evidence path">
      <div class="board">{{THEME_SECTIONS}}</div>
      <aside class="trace" aria-live="polite">
        <div class="trace-kicker"><svg class="card-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M3 4h14v12H3ZM6 8h8M6 12h5"/></svg>{{EVIDENCE_PATH}}</div>
        <div class="trace-path"><span>{{TRANSCRIPT}}</span><span>→</span><span>{{NUGGET}}</span><span>→</span><span>{{THEME}}</span><span>→</span><span>{{OPPORTUNITY}}</span></div>
        <blockquote id="trace-quote">{{FIRST_QUOTE}}</blockquote>
        <dl>
          <div><dt>{{SOURCE}}</dt><dd id="trace-source">{{FIRST_SOURCE}}</dd></div>
          <div><dt>{{NUGGET}}</dt><dd id="trace-observation">{{FIRST_OBSERVATION}}</dd></div>
          <div><dt>{{THEME}}</dt><dd id="trace-theme">{{FIRST_THEME}}</dd></div>
          <div><dt>{{OPPORTUNITY}}</dt><dd id="trace-opportunity">{{FIRST_OPPORTUNITY}}</dd></div>
        </dl>
      </aside>
    </section>
    <section class="divergence">
      <div class="eyebrow">{{COUNTEREVIDENCE}}</div><h2>{{DIVERGENCES}}</h2>
      <div class="table-wrap"><table><thead><tr><th>{{SIGNAL}}</th><th>{{COUNTEREVIDENCE}}</th><th>{{RELATED_EVIDENCE}}</th></tr></thead><tbody>{{DIVERGENCE_ROWS}}</tbody></table></div>
    </section>
    <footer>{{STATUS}}</footer>
  </main>
  <script type="application/json" id="affinity-map-data">{{EMBEDDED_DATA}}</script>
  <script>
    (() => {
      const root = document.getElementById("affinity-map");
      const records = JSON.parse(document.getElementById("affinity-map-data").textContent);
      const fields = {
        quote: root.querySelector("#trace-quote"), source: root.querySelector("#trace-source"),
        observation: root.querySelector("#trace-observation"), theme: root.querySelector("#trace-theme"),
        opportunity: root.querySelector("#trace-opportunity")
      };
      root.querySelectorAll("[data-nugget]").forEach((button) => {
        button.addEventListener("click", () => {
          const record = records[button.dataset.nugget];
          if (!record) return;
          root.querySelectorAll("[data-nugget]").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
          Object.entries(fields).forEach(([key, element]) => { element.textContent = record[key]; });
        });
      });
    })();
  </script>
</body>
</html>
"""
    assets = Path(__file__).resolve().parents[1] / "assets"
    style = (assets / "html-style.css").read_text(encoding="utf-8") + "\n" + (assets / "affinity-layout.css").read_text(encoding="utf-8")
    replacements = {
        "STYLE": style,
        "LANG": esc(language),
        "PAGE_TITLE": esc(page_title),
        "TITLE": esc(ui["title"]),
        "FOCUS": esc(data["focus_question"]),
        "DESCRIPTION": esc(data.get("description", "")),
        "STATUS": esc(status_label),
        "NUGGET_COUNT": str(len(data["nuggets"])),
        "THEME_COUNT": str(len(data["themes"])),
        "OPPORTUNITY_COUNT": str(len(data["opportunities"])),
        "PARTICIPANT_COUNT": str(len(data["participants"])),
        "NUGGETS": esc(ui["nuggets"]),
        "THEMES": esc(ui["themes"]),
        "OPPORTUNITIES": esc(ui["opportunities"]),
        "PARTICIPANTS": esc(ui["participants"]),
        "THEME_SECTIONS": body,
        "EVIDENCE_PATH": esc(ui["evidence_path"]),
        "TRANSCRIPT": esc(ui["transcript"]),
        "NUGGET": esc(ui["nugget"]),
        "THEME": esc(ui["theme"]),
        "OPPORTUNITY": esc(ui["opportunity"]),
        "SOURCE": esc(ui["source"]),
        "FIRST_QUOTE": esc(first["quote"]),
        "FIRST_SOURCE": esc(first["source"]),
        "FIRST_OBSERVATION": esc(first["observation"]),
        "FIRST_THEME": esc(first["theme"]),
        "FIRST_OPPORTUNITY": esc(first["opportunity"]),
        "COUNTEREVIDENCE": esc(ui["counterevidence"]),
        "DIVERGENCES": esc(ui["divergences"]),
        "SIGNAL": esc(ui["signal"]),
        "RELATED_EVIDENCE": esc(ui["related_evidence"]),
        "DIVERGENCE_ROWS": divergence_rows,
        "EMBEDDED_DATA": embedded_data,
    }
    return re.sub(r"\{\{([A-Z_]+)\}\}", lambda match: replacements[match.group(1)], template)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="normalized affinity map JSON")
    parser.add_argument("output", type=Path, nargs="?", default=Path("affinity/map.html"))
    parser.add_argument("--validate-only", action="store_true", help="validate without rendering")
    args = parser.parse_args()
    try:
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        data = validate(raw)
        if args.validate_only:
            print(f"OK: {args.input}")
            return 0
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(render(data), encoding="utf-8")
        print(f"Rendered {args.output}")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
