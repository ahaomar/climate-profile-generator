---
name: country-climate-profile
description: >
  Generate a cited, UN-style climate risk brief (PDF + Word) for any country
  from keyless public data. Use when the user asks for a climate profile,
  climate risk brief, country climate summary, or climate context for a
  proposal - e.g. "build a climate risk profile for Burkina Faso".
---

# Country Climate Profile Generator

Produce a finished, professional climate risk brief for one country. The
brief is evidence-first: every number comes from the fetched data file and
carries a citation. You never invent a number (principle P5).

## Pipeline (run in order)

1. **Resolve inputs.** From the user's request extract: country (required),
   focus sectors/hazards (optional, default "general"), any format preference
   (default: PDF + Word). If the country name is ambiguous, pick the most
   common interpretation and state it.

2. **Fetch data.** Run:
   `python3 scripts/fetch_climate.py "<Country>"`
   This writes `output/<ISO3>_data.json` and prints the datasets fetched and
   any gaps. NEVER skip this step and NEVER hand-write data values.

3. **Render charts.** Run:
   `python3 scripts/make_charts.py output/<ISO3>_data.json`
   This writes `output/charts/chart_temperature.png` and
   `output/charts/chart_rainfall.png` (SVG fallback is automatic when
   matplotlib is unavailable; pass `--force-svg` only if PNGs fail).

4. **Write the brief** in Markdown following `references/report-template.md`
   exactly (sections, order, tone). Save as
   `output/Climate_Profile_<Country>.md`. Numbers come ONLY from the JSON:
   - temperature trend/means, rainfall climatology → `datasets.nasa_power`
   - population, GDP, rural %, arable land → `datasets.world_bank`
   - vulnerability score/rank → `datasets.nd_gain`
   - NDC link → `datasets.ndc_registry.search_url`

5. **Render documents.** Produce `.docx` and `.pdf` from the Markdown:
   - If the host tool has a document skill (docx/pdf), use it.
   - Else if `pandoc` exists: `pandoc brief.md -o brief.docx` and
     `pandoc brief.md -o brief.pdf --pdf-engine=weasyprint` (or wkhtmltopdf).
   - Else deliver the Markdown + charts and say so plainly.
   PDF layout, fonts and branding live in `scripts/render_pdf.py` (Phase 4);
   the visual standard is `examples/mockup_climate_profile.pdf`.

6. **Report to the user**: file paths, datasets used, and any gaps
   (see gap language below).

## Gap handling (principle P5)

If `gaps[]` in the JSON is non-empty, the corresponding section or number is
 OMITTED and the brief includes, in its Sources annex:
> "<dataset> was unavailable at generation time (<reason>)."

Never substitute literature values, model guesses, or "approximately" numbers
for a missing dataset. Missing data is a result, not an error to hide.

## Writing rules

- Tone: neutral, factual, institutional. No adjectives like "devastating" or
  "alarming" - let numbers carry the weight (UN editorial style).
- Short paragraphs (2-4 sentences). Every figure footnoted: superscript index
  in text, full source name + URL in the Sources annex.
- State the observation window of every trend (e.g. "1985-2024").
- **Single-point caveat**: NASA POWER values represent one grid point
  (the country's representative location), not a country average. When
  presenting temperature/rainfall trends, add one sentence: "Values represent
  a representative location; regional averages may differ."
- Projections: only cite numbers present in the data file. NASA POWER is
  observational; if the user asks for projections, point to the NDC registry
  link and national communications rather than inventing figures.
- Length: 3-6 rendered pages. Do not pad.

## Design standard (locked)

Corporate Navy palette (NOT UN blue - this is not a UN entity):
masthead `#24356B`, headings `#1F3A7A`, charts `#3D5A99` + warm grey
`#9A958C`, fills `#EEF1F8`. Font: Roboto Condensed (ships in `fonts/`,
embedded in PDFs). Masthead: "Climate Risk Profile" + country + focus line.
Footer: "Built by Omar Farooq | github.com/ahaomar/climate-profile-generator"
and "Generated <date, time> | Page X of Y". Reference rendering:
`examples/mockup_climate_profile.pdf`.
