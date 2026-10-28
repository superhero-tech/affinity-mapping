# Affinity Mapping

An agent skill for synthesizing interview transcripts into evidence-backed themes and user needs, with an interactive, self-contained HTML evidence map.

## Use

Install this repository as the `affinity-mapping` folder in your agent’s skills directory (for Codex: `~/.codex/skills/affinity-mapping`). Read [SKILL.md](SKILL.md) for the full workflow.

The skill includes its instructions, references, CSS assets, and a Python renderer. The renderer requires Python 3.9+ and uses only the standard library:

```bash
python3 <skill-directory>/scripts/render_affinity_map.py affinity/map.json affinity/map.html
```

It produces an evidence ledger, themes, opportunities, normalized JSON, and an interactive HTML map. See [the data contract](references/map-data.md) for the JSON format.

## Source

This is a standalone copy of [Superhero.tech’s affinity-mapping skill](https://github.com/superhero-tech/superhero-skills/tree/2781117afb57690b87e5b6b3076deed6d19d3333/plugins/product-discovery/skills/product-discovery/affinity-mapping), copied from commit `2781117afb57690b87e5b6b3076deed6d19d3333`. The original remains in `superhero-skills`.

The skill files are copied unchanged. The optional `supersprint` companion mentioned in the instructions is available in the original repository and is not bundled here; it is not needed for affinity mapping.

## License

[MIT](LICENSE), copyright 2026 Superhero.tech.
