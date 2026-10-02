# Climate Profile Generator — Technical Specification & Build Plan

**Repo:** `github.com/ahaomar/climate-profile-generator`
**Owner:** Omar Farooq (@ahaomar)
**Status:** Phase 0 complete (approved mockup committed as baseline)
**Last updated:** 2 Oct 2026

---

## 1. What we are building

A portable **AI skill pack**: a folder that drops into Claude, Codex, Harness, Muse, or Dots agents once. After that, one sentence —

> *"Build a climate risk profile for Burkina Faso, focus on drought and agriculture."*

— produces a finished, cited 3–6 page climate brief with charts, delivered as **PDF + Word**.

## 2. Non-negotiable principles

| # | Principle | Meaning in practice |
|---|-----------|---------------------|
| P1 | Zero API keys | Only keyless public sources. No sign-ups, ever. |
| P2 | Free-tier friendly | Core features run on free tiers of every target AI tool. |
| P3 | Portable | Markdown instructions + standard-library Python. Fonts travel inside the pack. |
| P4 | Cited output | Every number in a brief carries source name + URL. |
| P5 | Honest data | If a source fails, the brief says so — never invents a number. |

## 3. Architecture

```
climate-profile-generator/
├── SKILL.md                  ← AI instructions (auto-trigger + pipeline)
├── scripts/
│   ├── fetch_climate.py      ← data layer (stdlib-only)
│   ├── make_charts.py        ← charts (matplotlib; SVG fallback)
│   └── render_pdf.py         ← UN-blue PDF layout (this mockup's design)
├── references/
│   ├── report-template.md    ← brief structure + writing rules
│   └── data-sources.md       ← endpoints, fields, citation formats
├── fonts/                    ← Roboto Condensed (OFL license, ships with pack)
│   ├── RobotoCondensed-Regular.ttf
│   ├── RobotoCondensed-Bold.ttf
│   └── RobotoCondensed-Italic.ttf
├── examples/                 ← approved mockup + end-to-end demo
├── docs/                     ← this document
└── README.md                 ← install + usage guide
```

**Design decisions already locked (approved mockup):**

- Typography: Roboto Condensed everywhere (headings Bold, body Regular, 11pt/16.5 leading). Fonts ship in `fonts/` and are embedded in PDFs.
- Brand: UN blue `#009EDB` masthead band, dark blue `#03679B` for headings/stats/charts, single hue family.
- Layout: full-width masthead page 1, slim header bar on later pages, 3 stat cards ("Key Findings"), numbered sections, chart + caption kept together, Sources annex with footnotes.
- Footer: `Built by Omar Farooq | github.com/ahaomar/climate-profile-generator` + `Generated <date, time> | Page X of Y`.

## 4. Data sources (all keyless, verified 2 Oct 2026)

| Source | What it provides | Endpoint type | Status |
|--------|------------------|---------------|--------|
| NASA POWER | Monthly/decadal temperature & precipitation per coordinate | REST, no key | ✅ verified live |
| World Bank API | Context indicators (population, GDP, land use) | REST, no key | ✅ verified live |
| World Bank CCKP | Climate projections, hazard data | REST/download | verify in Phase 1 |
| ND-GAIN Index | Vulnerability + readiness rankings | Public CSV | verify in Phase 1 |
| UNFCCC NDC Registry | Country pledges | Public pages | links + manual summary |
| Copernicus C3S (optional stretch) | Reanalysis/projections | Open data | Phase 6 stretch, skip if heavy |

**Fallback chain:** if a source is unreachable, the brief marks that section "data unavailable at generation time" — it never fabricates (P5).

## 5. Phased build plan

> **Git rule (user requirement):** every phase ends with a commit; a new phase **never** starts unless the previous phase is committed and clean (`git status` shows nothing pending). Commit message format: `Phase N: <what was delivered>`.

---

### Phase 0 — Repo baseline ✅ (done)
- Mockup approved (layout, fonts, header, footer, credits).
- This specification committed.

### Phase 1 — Data layer (`scripts/fetch_climate.py`)
**Build:**
- `fetch_country(country_name)` → resolves country to ISO code + representative coordinates (bundled lookup table of ~195 countries; no network needed for resolution).
- Fetchers: NASA POWER monthly climatology + 40-yr annual series; World Bank context indicators; ND-GAIN score (bundled CSV snapshot + refresh attempt); NDC registry link builder.
- Output: one JSON file `output/<country>_data.json` with a `sources[]` block (URL + fetch timestamp per dataset) and `gaps[]` for anything that failed.
- Stdlib only (`urllib`, `json`, `csv`). Graceful timeouts (10 s), retry once.
**Accept:** `python3 scripts/fetch_climate.py "Burkina Faso"` produces populated JSON; disconnecting the network produces clean gaps, not a crash.
**Commit:** `Phase 1: data layer - NASA POWER + World Bank + ND-GAIN fetchers with gap reporting`

### Phase 2 — Charts (`scripts/make_charts.py`)
**Build:**
- Chart 1: 40-year temperature trend + linear trend line + "°C/decade" annotation.
- Chart 2: monthly rainfall, recent decade vs baseline.
- Optional per-focus charts (hazard bar, seasonality) driven by the user's stated focus.
- Roboto Condensed loaded from `../fonts`; palette locked to `#03679B`/grey family.
- matplotlib if present; otherwise dependency-free SVG fallback (simple line/bar renderer, same palette).
**Accept:** charts regenerate from the Phase 1 JSON alone; SVG fallback verified by forcing it.
**Commit:** `Phase 2: chart engine with font consistency and SVG fallback`

### Phase 3 — Brain (`SKILL.md` + `references/`)
**Build:**
- `SKILL.md`: trigger conditions (country + climate keywords), pipeline steps, tone rules (neutral, UN editorial style), how to weave `data.json` numbers into the template, gap-handling language, citation format.
- `references/report-template.md`: the 6-section structure approved in the mockup (Key Findings → Observed trends → Projections → Hazard exposure → Sector impacts → National response → Sources annex), with writing guidance per section and a hazard-threshold glossary.
- `references/data-sources.md`: endpoint documentation + citation strings.
**Accept:** a fresh AI session given only this folder can turn a Phase 1 JSON into a complete markdown brief without extra guidance.
**Commit:** `Phase 3: SKILL.md instructions, report template and data-source reference`

### Phase 4 — PDF renderer (`scripts/render_pdf.py`)
**Build:**
- Port the approved mockup layout into a parameterized renderer: any country, any data, focus line variable.
- Two-pass build for real "Page X of Y"; embedded fonts; UN-blue masthead; footer credits + generation timestamp.
- Roboto Condensed embedded; mockup banner removed in real runs.
**Accept:** real Burkina Faso PDF from live Phase 1 data matches the approved mockup style; page footers show correct totals; fonts embedded (font.check passes).
**Commit:** `Phase 4: PDF renderer - approved UN-blue layout, embedded fonts, live data`

### Phase 5 — Word renderer (`scripts/render_docx.py`)
**Build:**
- Same content → `.docx` (python-docx or the host tool's document skill).
- Declare Roboto Condensed with graceful fallback chain (falls back to Calibri if not installed) — Word cannot embed fonts from scripts, so this is the documented, accepted behavior.
- Keep structure parallel to the PDF (heading styles, stat table, embedded chart PNGs, sources list).
**Accept:** docx opens cleanly in Word/Pages/LibreOffice; content identical to PDF; fallback verified.
**Commit:** `Phase 5: Word renderer with font fallback chain`

### Phase 6 — End-to-end demo + quality gates
**Build:**
- Full pipeline run: sentence in → `Climate_Profile_BurkinaFaso.pdf` + `.docx` out, saved to `examples/`.
- One more country as a regression test (e.g., Senegal or Bangladesh) to prove it's parameterized.
- QA checklist run: fonts embedded, no overflow, citations valid URLs, page totals correct.
**Accept:** both countries produce complete, cited, on-brand briefs without manual fixes.
**Commit:** `Phase 6: end-to-end demos - Burkina Faso + regression country, QA passed`

### Phase 7 — Install guide + portability packaging
**Build:**
- `README.md`: what it is, 3-step install per tool (Claude `~/.claude/skills` / ZCode `~/.zcode/skills`, Codex via `AGENTS.md` pointer, Harness/Muse/Dots: mount folder or paste SKILL.md), copy-paste usage examples, troubleshooting.
- License files (MIT for code, OFL note for fonts, data-source attributions).
- Optional: package as a ZCode plugin for one-click marketplace install (separate follow-on repo if needed).
**Accept:** a colleague can install and run it on a fresh machine following only the README.
**Commit:** `Phase 7: README install guide, licenses, packaging`

---

## 6. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Source API changes/goes down | Gap reporting (P5); ND-GAIN shipped as bundled CSV snapshot |
| Word font substitution on devices without Roboto Condensed | Accepted & documented; fallback chain; PDF is the canonical share format |
| AI tool without matplotlib (SVG fallback needed) | Phase 2 fallback renderer; charts degrade, never disappear |
| Very long documents overflowing layout | Two-pass pagination already proven in mockup; charts scale to width |

## 7. Out of scope (v1)
- Consultancy Radar (on hold — separate repo later).
- Multi-language output (structure designed so FR/AR templates can slot in later).
- MCP server / live dashboards (upgrade path only).
