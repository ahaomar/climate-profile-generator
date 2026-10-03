# Data Sources Reference

All sources are keyless public APIs. The data layer
(`scripts/fetch_climate.py`) implements these — this document is the field
map for writing the brief, and the repair guide if an endpoint changes.

## 1. NASA POWER (observational climate)

- Endpoint: `https://power.larc.nasa.gov/api/temporal/monthly/point`
  `?parameters=T2M,PRECTOTCORR&community=AG&longitude=<lon>&latitude=<lat>&start=<yyyy>&end=<yyyy>&format=JSON`
- Units: T2M = °C (monthly mean), PRECTOTCORR = mm/day (monthly mean).
- Keys: `"YYYY01"…"YYYY12"` per month. `"YYYY13"` is NASA's own annual mean —
  use it to cross-check aggregation (must match within 0.02 °C).
- JSON location: `properties.parameter.<PARAM>.<YYYYMM>`
- Known caveat: single grid point; MERRA-2 trends at Sahelian points can run
  flatter than station networks (aerosol assimilation). State the caveat; do
  not "correct" the numbers.
- Our output fields: `datasets.nasa_power.annual.{years,temp_c,precip_mm_yr}`,
  `.monthly_climatology`, `.monthly_precip_by_year` (mm/day per month).

## 2. World Bank Open Data (context indicators)

- Endpoint: `https://api.worldbank.org/v2/country/<ISO3>/indicator/<CODE>?format=json&per_page=60`
- Payload: `[meta, [ {date, value, ...}, ... ]]`; take the newest non-null.
- Codes we use:
  | Code | Meaning |
  |------|---------|
  | SP.POP.TOTL | Population, total |
  | NY.GDP.MKTP.CD | GDP (current US$) |
  | SP.RUR.TOTL.ZS | Rural population (% of total) |
  | AG.LND.ARBL.ZS | Arable land (% of land area) |
  | SP.POP.GROW | Population growth (annual %) |
- Note: `EN.POP.RUR.ZS` is the deprecated alias — do not use.
- Format large values for humans (population in millions to 1 decimal; GDP in
  billions US$) and keep the raw value in the citation's underlying table.

## 3. ND-GAIN Country Index (vulnerability/readiness)

- Bundle ZIP: `https://gain.nd.edu/assets/647440/ndgain_countryindex_2026.zip`
  (file name carries the release year — if 404, check
  `https://gain.nd.edu/our-work/country-index/download-data/` for the current
  asset ID).
- Inside: `resources 2/gain/gain.csv` — wide format: `ISO3, Name, 1995..YYYY`.
- Interpretation: **higher score = less vulnerable / more ready**. Rank is
  computed by sorting all countries descending (rank 1 = most ready). For
  public communication prefer the inverted framing ("ranked Nth most
  vulnerable of M") when score is low — compute as `M − rank + 1`.
- Host resets raw-socket TLS sometimes; the fetcher falls back to `curl`.
- Our output: `datasets.nd_gain.{score,rank,rank_of,year}`.

## 4. UNFCCC NDC Registry (national pledges)

- Link builder: `https://unfccc.int/NDCREG?country=<ISO3>` (search page).
- We do not scrape the registry; the brief links it. If the host tool can
  browse, it may summarize the country's latest submission and cite the
  specific document URL it used.

## Citation rules

- Every dataset cited once in the Sources annex with retrieval timestamp
  (from the JSON `generated` field).
- In-text: superscript numbers matching the annex.
- A number without a retrievable source never enters the brief (P5).
