# Report Template — Climate Risk Brief

The brief follows this structure exactly. Section order is fixed; content is
driven by the data JSON. Length 3–6 rendered pages.

---

## Masthead (rendered by the PDF template, not body text)

- Kicker: `COUNTRY BRIEF`
- Title: `Climate Risk Profile`
- Line 2: `<Country> | <Focus> Focus` (focus from user request, default "Climate")
- Meta: `<period> trends | <Month Year> | Country Climate Profile Generator`

## Key Findings (3 stat cards + one framing sentence)

Pick the three strongest numbers available in the data:

| Card | Source field (if present) |
|------|---------------------------|
| Temperature change since start of period | `nasa_power.annual` — linear trend over full period × years elapsed |
| Rainfall change, recent decade vs baseline | `nasa_power.monthly_precip_by_year` — % difference of annual means |
| Vulnerability rank | `nd_gain.rank` / `nd_gain.rank_of` (word it: "ranked 158th of 190, 2024") |

Framing sentence template (adapt, keep neutral):
> "Every figure in this brief is cited to its source. Values represent a
> representative location; regional averages may differ."

If a card's dataset is missing, use a different available number (e.g. rural
population %) — never leave an empty card and never invent one.

## 1. Observed trends

- Temperature: start→end of period, warmest year, trend per decade if
  meaningful (state period). Chart: `chart_temperature.*` as Figure 1.
- Rainfall: total annual range, how recent decade compares to baseline
  (wetter/drier, which months changed most). Chart: `chart_rainfall.*` as
  Figure 2.
- One sentence of context only — interpretation stays minimal and neutral.

## 2. Context and exposure

From `world_bank` (whichever indicators are present): population (year),
population growth, rural share, arable land share, GDP scale. Two or three
sentences connecting these to exposure (e.g. high rural share + rain-fed
agriculture → rainfall sensitivity). No speculation beyond the connection
stated.

## 3. National response

NDC: state that the country's submission is available, give the registry
link, and (only if the host tool may browse) summarize from the registry.
Otherwise one sentence + link. Mention that adaptation priorities are
detailed in the country's NAP documents.

## Sources (annex)

Numbered list matching the superscripts used in the text. Format:

```
1. NASA POWER agroclimatology API, monthly point data (<lon>,<lat>), 1985–2024. power.larc.nasa.gov — retrieved <generated timestamp>
2. World Bank Open Data API, indicators SP.POP.TOTL, NY.GDP.MKTP.CD, SP.RUR.TOTL.ZS, AG.LND.ARBL.ZS, SP.POP.GROW. api.worldbank.org — retrieved <timestamp>
3. ND-GAIN Country Index (2024 scores). gain.nd.edu — retrieved <timestamp>
4. UNFCCC NDC Registry, <Country> submission. <ndc_registry.search_url>
```

If any dataset is in `gaps[]`, add: "*<name> was unavailable at generation
time (<reason>).*"

## Hazard glossary (for writer reference — not printed)

- **Drought-prone**: baseline wet-season rainfall < ~100 mm/month with high
  year-to-year variability.
- **Heavy-rainfall intensification**: recent-decade monthly mean exceeds
  baseline in peak months while shoulder months decline (shorter, sharper
  season).
- **Heat stress**: mean monthly temperatures > 30 °C for 4+ months.
Apply these only when the data shows them; describe, don't diagnose.
