# Climate Profile Generator

One sentence in → a finished, cited climate risk brief out.

An AI skill pack that turns a request like

> *"Build a climate risk profile for Burkina Faso, focus on drought and agriculture."*

into a professional 2–6 page **PDF + Word** brief — real data, charts, every
number cited — in about two minutes. Built for UN/international staff,
consultants, and researchers. **Not UN-branded**: the design is a deliberate
"Corporate Navy" identity (`#24356B` / `#1F3A7A`), so outputs read as an
independent professional product.

![look](examples/mockup_climate_profile.pdf)

## What you get

Per country: `Climate_Profile_<Country>.pdf` (canonical share format, fonts
embedded) + `.docx` (editable; Word substitutes a similar font if Roboto
Condensed isn't installed). Contents: Key Findings stat cards, observed
trends, seasonal rainfall, socio-economic context, ND-GAIN vulnerability
standing, NDC/national response, and a cited Sources annex with retrieval
timestamps.

Data comes from keyless public sources only: NASA POWER, World Bank Open
Data, ND-GAIN Country Index, UNFCCC NDC Registry. If a source is down, the
brief says so — it never invents numbers.

## Quick start (inside an AI agent with this skill)

```
1. python3 scripts/fetch_climate.py "Burkina Faso"     # data → output/BFA_data.json
2. python3 scripts/make_charts.py output/BFA_data.json # charts → output/charts/
3. Write the brief JSON (schema: scripts/render_pdf.py docstring,
   writing rules: SKILL.md + references/report-template.md)
4. python3 scripts/render_pdf.py  --brief output/BFA_brief.json -o output/Climate_Profile_BurkinaFaso.pdf
5. python3 scripts/render_docx.py --brief output/BFA_brief.json -o output/Climate_Profile_BurkinaFaso.docx
```

Steps 1–2 and 4–5 are commands; step 3 is the AI's writing job, governed by
`SKILL.md` so tone, citations, and gap-handling stay consistent.

## Install per AI tool

The pack is a plain folder — nothing to compile.

| Tool | Install |
|------|---------|
| Claude Code / ZCode | `mkdir -p ~/.claude/skills && cp -r . ~/.claude/skills/country-climate-profile` (ZCode: `~/.zcode/skills/`) |
| Codex CLI | Add to `AGENTS.md`: `Use ~/skills/country-climate-profile/SKILL.md as the climate-profile skill.` |
| Harness / Muse / Dots | Point the agent's skill/instruction folder at this directory, or paste `SKILL.md` into the custom-instructions slot and keep `scripts/`, `fonts/`, `references/` alongside it. |

Requirements: Python 3.10+, `reportlab`, `pillow`, `pymupdf` (PDF),
`python-docx` (Word), `matplotlib` (optional — charts fall back to
dependency-free SVG without it). No API keys. No network beyond the public
data sources.

## Repo layout

```
SKILL.md                  the AI's instructions (trigger, pipeline, writing rules)
scripts/fetch_climate.py  data layer (NASA POWER + World Bank + ND-GAIN, gap reporting)
scripts/make_charts.py    chart engine (matplotlib; SVG fallback)
scripts/render_pdf.py     Corporate Navy PDF renderer (fonts embedded, Page X of Y)
scripts/render_docx.py    Word renderer (graceful font fallback)
references/               report template + data-source field maps
fonts/                    Roboto Condensed (OFL) — ships with the pack
examples/                 approved mockup + Burkina Faso & Senegal demos
docs/TECHNICAL_SPEC.md    architecture, phased build history, principles
```

## Honest-data guarantees

- Every figure is cited (source + URL + retrieval timestamp).
- A missing dataset becomes a visible "unavailable" note, never a guess.
- Climate values represent a single representative grid point; the brief
  states this. (MERRA-2 trends at some Sahelian points run flat — we report
  what the source says.)

## Credits & licenses

- Built by **Omar Farooq** — [github.com/ahaomar](https://github.com/ahaomar)
- Code: MIT (see `LICENSE`). Fonts: Roboto Condensed under the SIL Open Font
  License. Data: NASA POWER (public domain), World Bank Open Data (CC BY 4.0),
  ND-GAIN (open use), UNFCCC NDC Registry (public).
- Consultancy Radar is a planned companion tool (on hold).
