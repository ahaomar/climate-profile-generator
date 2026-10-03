#!/usr/bin/env python3
"""climate-profile-generator / Phase 1: data layer.

Fetches public, keyless climate + context data for one country and writes
a single JSON file the report pipeline consumes.

Usage:
    python3 scripts/fetch_climate.py "Burkina Faso"

Output:
    output/<iso3>_data.json   containing datasets + sources[] + gaps[]

Principles (see docs/TECHNICAL_SPEC.md): stdlib only, zero API keys,
never fabricate - anything unavailable is recorded in gaps[].
"""
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TIMEOUT = 15
RETRIES = 2
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

NASA_BASE = "https://power.larc.nasa.gov/api/temporal"
WB_BASE = "https://api.worldbank.org/v2"

# Representative coordinates (capital city) - ISO3 lookup.
COUNTRY_TABLE = {
    "afghanistan": ("AFG", 69.2, 34.5), "albania": ("ALB", 19.8, 41.3),
    "algeria": ("DZA", 3.1, 36.8), "angola": ("AGO", 13.2, -8.8),
    "argentina": ("ARG", -58.4, -34.6), "armenia": ("ARM", 44.5, 40.2),
    "australia": ("AUS", 149.1, -35.3), "austria": ("AUT", 16.4, 48.2),
    "azerbaijan": ("AZE", 49.9, 40.4), "bangladesh": ("BGD", 90.4, 23.8),
    "belarus": ("BLR", 27.6, 53.9), "belgium": ("BEL", 4.4, 50.9),
    "benin": ("BEN", 2.6, 6.5), "bolivia": ("BOL", -68.1, -16.5),
    "bosnia and herzegovina": ("BIH", 18.4, 43.9), "botswana": ("BWA", 25.9, -24.6),
    "brazil": ("BRA", -47.9, -15.8), "bulgaria": ("BGR", 23.3, 42.7),
    "burkina faso": ("BFA", -1.5, 12.4), "burundi": ("BDI", 29.4, -3.4),
    "cabo verde": ("CPV", -23.5, 14.9), "cambodia": ("KHM", 104.9, 11.6),
    "cameroon": ("CMR", 11.5, 3.9), "canada": ("CAN", -75.7, 45.4),
    "central african republic": ("CAF", 18.6, 4.4), "chad": ("TCD", 15.1, 12.1),
    "chile": ("CHL", -70.7, -33.5), "china": ("CHN", 116.4, 39.9),
    "colombia": ("COL", -74.1, 4.7), "comoros": ("COM", 43.3, -11.7),
    "congo, democratic republic": ("COD", 23.6, -4.3),
    "congo, republic": ("COG", 15.3, -4.3), "costa rica": ("CRI", -84.1, 9.9),
    "croatia": ("HRV", 16.0, 45.8), "cuba": ("CUB", -82.4, 23.1),
    "cyprus": ("CYP", 33.4, 35.2), "czech republic": ("CZE", 14.4, 50.1),
    "czechia": ("CZE", 14.4, 50.1), "denmark": ("DNK", 12.6, 55.7),
    "djibouti": ("DJI", 43.1, 11.6), "dominican republic": ("DOM", -69.9, 18.5),
    "ecuador": ("ECU", -78.5, -0.2), "egypt": ("EGY", 31.2, 30.0),
    "el salvador": ("SLV", -89.2, 13.7), "eritrea": ("ERI", 38.9, 15.3),
    "estonia": ("EST", 24.7, 59.4), "ethiopia": ("ETH", 38.7, 9.0),
    "fiji": ("FJI", 178.4, -18.1), "finland": ("FIN", 24.9, 60.2),
    "france": ("FRA", 2.3, 48.9), "gabon": ("GAB", 9.5, 0.4),
    "gambia": ("GMB", -16.6, 13.5), "georgia": ("GEO", 44.8, 41.7),
    "germany": ("DEU", 13.4, 52.5), "ghana": ("GHA", -0.2, 5.6),
    "greece": ("GRC", 23.7, 38.0), "guatemala": ("GTM", -90.5, 14.6),
    "guinea": ("GIN", -13.7, 9.5), "guinea-bissau": ("GNB", -15.6, 11.9),
    "guyana": ("GUY", -58.2, 6.8), "haiti": ("HTI", -72.3, 18.5),
    "honduras": ("HND", -87.2, 14.1), "hungary": ("HUN", 19.0, 47.5),
    "iceland": ("ISL", -21.9, 64.1), "india": ("IND", 77.2, 28.6),
    "indonesia": ("IDN", 106.8, -6.2), "iran": ("IRN", 51.4, 35.7),
    "iraq": ("IRQ", 44.4, 33.3), "ireland": ("IRL", -6.3, 53.3),
    "israel": ("ISR", 35.2, 31.8), "italy": ("ITA", 12.5, 41.9),
    "jamaica": ("JAM", -76.8, 18.0), "japan": ("JPN", 139.7, 35.7),
    "jordan": ("JOR", 35.9, 31.9), "kazakhstan": ("KAZ", 71.4, 51.1),
    "kenya": ("KEN", 36.8, -1.3), "kiribati": ("KIR", 173.0, 1.3),
    "kosovo": ("XKX", 21.2, 42.7), "kuwait": ("KWT", 47.5, 29.4),
    "kyrgyzstan": ("KGZ", 74.6, 42.9), "laos": ("LAO", 102.6, 18.0),
    "latvia": ("LVA", 24.1, 56.9), "lebanon": ("LBN", 35.5, 33.9),
    "lesotho": ("LSO", 27.5, -29.3), "liberia": ("LBR", -10.8, 6.3),
    "libya": ("LBY", 13.2, 32.9), "lithuania": ("LTU", 25.3, 54.7),
    "madagascar": ("MDG", 47.5, -18.9), "malawi": ("MWI", 33.8, -13.9),
    "malaysia": ("MYS", 101.7, 3.1), "mali": ("MLI", -8.0, 12.6),
    "mauritania": ("MRT", -15.9, 18.1), "mauritius": ("MUS", 57.5, -20.2),
    "mexico": ("MEX", -99.1, 19.4), "moldova": ("MDA", 28.9, 47.0),
    "mongolia": ("MNG", 106.9, 47.9), "montenegro": ("MNE", 19.3, 42.4),
    "morocco": ("MAR", -6.8, 34.0), "mozambique": ("MOZ", 32.6, -25.9),
    "myanmar": ("MMR", 96.2, 16.8), "namibia": ("NAM", 17.1, -22.6),
    "nepal": ("NPL", 85.3, 27.7), "netherlands": ("NLD", 4.9, 52.4),
    "new zealand": ("NZL", 174.8, -41.3), "nicaragua": ("NIC", -86.3, 12.1),
    "niger": ("NER", 2.1, 13.5), "nigeria": ("NGA", 7.5, 9.1),
    "north macedonia": ("MKD", 21.4, 42.0), "norway": ("NOR", 10.7, 59.9),
    "oman": ("OMN", 58.4, 23.6), "pakistan": ("PAK", 73.1, 33.7),
    "palestine": ("PSE", 35.2, 31.9), "panama": ("PAN", -79.5, 9.0),
    "papua new guinea": ("PNG", 147.2, -9.4), "paraguay": ("PRY", -57.6, -25.3),
    "peru": ("PER", -77.0, -12.0), "philippines": ("PHL", 121.0, 14.6),
    "poland": ("POL", 21.0, 52.2), "portugal": ("PRT", -9.1, 38.7),
    "qatar": ("QAT", 51.5, 25.3), "romania": ("ROU", 26.1, 44.4),
    "russia": ("RUS", 37.6, 55.8), "rwanda": ("RWA", 30.1, -1.9),
    "saudi arabia": ("SAU", 46.7, 24.7), "senegal": ("SEN", -17.4, 14.7),
    "serbia": ("SRB", 20.5, 44.8), "sierra leone": ("SLE", -13.2, 8.5),
    "singapore": ("SGP", 103.8, 1.4), "slovakia": ("SVK", 17.1, 48.1),
    "slovenia": ("SVN", 14.5, 46.1), "somalia": ("SOM", 45.3, 2.0),
    "south africa": ("ZAF", 28.0, -26.2), "south sudan": ("SSD", 31.6, 4.9),
    "south korea": ("KOR", 127.0, 37.5), "spain": ("ESP", -3.7, 40.4),
    "sri lanka": ("LKA", 79.9, 6.9), "sudan": ("SDN", 32.5, 15.5),
    "suriname": ("SUR", -55.2, 5.9), "sweden": ("SWE", 18.1, 59.3),
    "switzerland": ("CHE", 7.4, 46.9), "syria": ("SYR", 38.3, 33.5),
    "tajikistan": ("TJK", 68.8, 38.6), "tanzania": ("TZA", 39.3, -6.8),
    "thailand": ("THA", 100.5, 13.8), "timor-leste": ("TLS", 125.6, -8.6),
    "togo": ("TGO", 1.2, 6.1), "trinidad and tobago": ("TTO", -61.5, 10.7),
    "tunisia": ("TUN", 10.2, 36.8), "turkey": ("TUR", 32.9, 39.9),
    "turkmenistan": ("TKM", 58.4, 37.9), "uganda": ("UGA", 32.6, 0.3),
    "ukraine": ("UKR", 30.5, 50.5), "united arab emirates": ("ARE", 54.4, 24.5),
    "united kingdom": ("GBR", -0.1, 51.5), "united states": ("USA", -77.0, 38.9),
    "uruguay": ("URY", -56.2, -34.9), "uzbekistan": ("UZB", 69.3, 41.3),
    "vanuatu": ("VUT", 168.3, -17.7), "venezuela": ("VEN", -66.9, 10.5),
    "vietnam": ("VNM", 105.8, 21.0), "yemen": ("YEM", 44.2, 15.4),
    "zambia": ("ZMB", 28.3, -15.4), "zimbabwe": ("ZWE", 31.0, -17.8),
}

# World Bank context indicators: code -> human label
WB_INDICATORS = {
    "SP.POP.TOTL": "Population, total",
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "SP.RUR.TOTL.ZS": "Rural population (% of total)",
    "AG.LND.ARBL.ZS": "Arable land (% of land area)",
    "SP.POP.GROW": "Population growth (annual %)",
}


def resolve_country(name):
    key = name.strip().lower()
    if key in COUNTRY_TABLE:
        return COUNTRY_TABLE[key]
    for k, v in COUNTRY_TABLE.items():
        if k in key or key in k:
            return v
    raise SystemExit(
        "Country '%s' not in bundled lookup table. Known example: "
        "'Burkina Faso'. Add it to COUNTRY_TABLE with (ISO3, lon, lat)." % name)


def fetch_json(url):
    for attempt in range(1, RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "climate-profile-generator/0.1"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
            if attempt == RETRIES:
                raise
            time.sleep(2 * attempt)


def fetch_nasa(lon, lat, start, end):
    """40-year monthly T2M + PRECTOTCORR for the representative point."""
    url = ("%s/monthly/point?parameters=T2M,PRECTOTCORR&community=AG"
           "&longitude=%s&latitude=%s&start=%s&end=%s&format=JSON"
           % (NASA_BASE, lon, lat, start, end))
    data = fetch_json(url)
    props = data["properties"]["parameter"]
    years, temps, rain_year = [], [], []
    months_t, months_r = [[] for _ in range(12)], [[] for _ in range(12)]
    for y in range(start, end + 1):
        tvals = [props["T2M"].get("%d%02d" % (y, m), -999) for m in range(1, 13)]
        rvals = [props["PRECTOTCORR"].get("%d%02d" % (y, m), -999) for m in range(1, 13)]
        if -999 in tvals or -999 in rvals:
            continue
        years.append(y)
        temps.append(sum(tvals) / 12.0)
        rain_year.append(sum(rvals) * 365.0 / 12.0)  # mm/day avg -> mm/yr
        for m in range(12):
            months_t[m].append(tvals[m])
            months_r[m].append(rvals[m])
    half = (end - start + 1) // 2
    return {
        "point": {"lon": lon, "lat": lat},
        "period": [start, end],
        "annual": {"years": years, "temp_c": [round(t, 2) for t in temps],
                   "precip_mm_yr": [round(p, 1) for p in rain_year]},
        "monthly_climatology": {
            "temp_c": [round(sum(m) / len(m), 2) for m in months_t],
            "precip_mm_day": [round(sum(m) / len(m), 2) for m in months_r]},
        # per-year monthly rainfall (mm/day), keyed "YYYYMM" -> value:
        # lets the chart engine compute a true baseline excluding recent years
        "monthly_precip_by_year": {
            str(y): [round(props["PRECTOTCORR"].get("%d%02d" % (y, m), -999), 3)
                     for m in range(1, 13)]
            for y in years},
    }


def fetch_worldbank(iso3):
    out = {}
    for code, label in WB_INDICATORS.items():
        url = ("%s/country/%s/indicator/%s?format=json&per_page=60"
               % (WB_BASE, iso3, code))
        try:
            payload = fetch_json(url)
            series = payload[1] or []
            vals = [(int(d["date"]), d["value"]) for d in series if d["value"] is not None]
            if vals:
                latest = max(vals, key=lambda x: x[0])
                out[code] = {"label": label, "year": latest[0],
                             "value": round(float(latest[1]), 2)}
        except Exception:
            continue  # recorded as gap by caller if missing
    return out


NDGAIN_ZIP = "https://gain.nd.edu/assets/647440/ndgain_countryindex_2026.zip"


def _download_bytes(url, timeout=90):
    """urllib first; curl fallback (some hosts reset urllib's TLS handshake)."""
    import subprocess
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (climate-profile-generator)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception:
        pass
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                         capture_output=True, check=True)
    return out.stdout


def fetch_ndgain(iso3):
    """ND-GAIN country index score + rank from the official ZIP bundle.

    gain.csv is wide-format: ISO3, Name, 1995..latest-year columns.
    Failure -> recorded as a gap by the caller.
    """
    import csv, io, zipfile
    data = _download_bytes(NDGAIN_ZIP)
    zf = zipfile.ZipFile(io.BytesIO(data))
    name = next((n for n in zf.namelist()
                 if n.endswith("gain/gain.csv") and "__MACOSX" not in n), None)
    if not name:
        return None
    reader = csv.DictReader(io.StringIO(zf.read(name).decode("utf-8", errors="replace")))
    row = next((x for x in reader if x.get("ISO3") == iso3), None)
    if not row:
        return None
    years = [c for c in row.keys() if c.isdigit()]
    latest_year = max(years)
    score = float(row[latest_year])
    # rank: lower GAIN score = more vulnerable = worse rank
    all_rows = list(csv.DictReader(
        io.StringIO(zf.read(name).decode("utf-8", errors="replace"))))
    scores = sorted((float(r[latest_year]) for r in all_rows
                     if r.get(latest_year) not in (None, "", "NA")), reverse=True)
    rank = scores.index(score) + 1
    return {"score": round(score, 1), "rank": rank,
            "rank_of": len(scores), "year": int(latest_year),
            "note": "higher score = less vulnerable / more ready (ND-GAIN)"}


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    name = sys.argv[1]
    iso3, lon, lat = resolve_country(name)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    result = {"country": name.title(), "iso3": iso3,
              "generated": now, "datasets": {}, "sources": [], "gaps": []}

    def source(label, url, status):
        result["sources"].append({"name": label, "url": url,
                                  "fetched": now, "status": status})

    try:
        result["datasets"]["nasa_power"] = fetch_nasa(lon, lat, 1985, 2024)
        source("NASA POWER agroclimatology (monthly point, %s,%s)" % (lon, lat),
               "%s/monthly/point?parameters=T2M,PRECTOTCORR&community=AG&longitude=%s&latitude=%s&start=1985&end=2024"
               % (NASA_BASE, lon, lat), "ok")
    except Exception as e:
        result["gaps"].append({"dataset": "nasa_power", "reason": str(e)[:200]})

    try:
        wb = fetch_worldbank(iso3)
        if wb:
            result["datasets"]["world_bank"] = wb
            missing = [c for c in WB_INDICATORS if c not in wb]
            source("World Bank Open Data (indicators: %s)" % ", ".join(WB_INDICATORS),
                   WB_BASE + "/country/%s/indicator/SP.POP.TOTL?format=json" % iso3,
                   "ok" if not missing else "partial")
            if missing:
                result["gaps"].append({"dataset": "world_bank",
                                       "reason": "no data: " + ", ".join(missing)})
        else:
            result["gaps"].append({"dataset": "world_bank", "reason": "no data returned"})
    except Exception as e:
        result["gaps"].append({"dataset": "world_bank", "reason": str(e)[:200]})

    nd = fetch_ndgain(iso3)
    if nd:
        result["datasets"]["nd_gain"] = nd
        source("ND-GAIN Country Index", "https://gain.nd.edu/our-work/country-index/",
               "ok")
    else:
        result["gaps"].append({"dataset": "nd_gain",
                               "reason": "remote snapshot unavailable; see gain.nd.edu"})

    result["datasets"]["ndc_registry"] = {
        "search_url": "https://unfccc.int/NDCREG?country=%s" % iso3,
        "note": "link only; NDC summary text is drafted by the report writer, not scraped"}

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / ("%s_data.json" % iso3)
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("wrote %s" % out_path)
    print("datasets: %s" % ", ".join(result["datasets"]))
    if result["gaps"]:
        print("gaps: %s" % "; ".join(g["dataset"] for g in result["gaps"]))
    else:
        print("gaps: none")


if __name__ == "__main__":
    main()
