#!/usr/bin/env python3
"""
Syria Economic Dashboard — Automated Data Update Script

Equivalent to the scpr_scrape_data.ipynb notebook, designed to run
headlessly in GitHub Actions (or locally).

Steps:
  1. Scrape SCPR bulletins page for English PDF links
  2. Download any new PDFs (skip already-cached ones)
  3. Extract CPI + wage data from all bulletins
  4. Export data/cpi_data.json

Exit codes:
  0 — success (data may or may not have changed)
  1 — fatal error
"""

import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import unquote, urljoin

import pdfplumber
import requests
from bs4 import BeautifulSoup

# ── paths ──────────────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data", "scpr_bulletins_cpi")
JSON_PATH = os.path.join(ROOT_DIR, "data", "cpi_data.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ── constants ──────────────────────────────────────────────────────────
BASE_URL = "https://scpr-syria.org/publications/bulletins/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

GOVERNORATE_MAP = {
    1: "Damascus", 2: "Rural Damascus", 5: "Homs", 6: "Hama",
    7: "Tartous", 8: "Lattakia", 9: "Idleb", 10: "Aleppo",
    11: "Ar-Raqqa", 14: "Deir-ez-Zor", 17: "Al-Hasakeh",
    20: "As-Sweida", 23: "Dar'a", 24: "Quneitra", 25: "SYRIA",
}

COMMODITY_ALIASES = {"Clothing and Shoes": "Clothing and footwear"}

MONTH_NAME_TO_NUM = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "septemer": 9, "october": 10,
    "november": 11, "december": 12,
}

WAGE_ALIASES = {
    "professor": "Public: Professor",
    "university professor": "Public: Professor",
    "university-educated": None,
    "university educated": None,
    "university grad": None,
    "4th band": "Public: 4th Band",
    "4th grade": "Public: 4th Band",
    "basic education": "Public: 4th Band",
    "preparatory": "Public: 4th Band",
    "company director": "Private: Company Director",
    "company manager": "Private: Company Director",
    "shop worker": "Private: Shop Worker",
}


# ═══════════════════════════════════════════════════════════════════════
#  1. SCRAPING — discover & download PDF bulletins
# ═══════════════════════════════════════════════════════════════════════

def scrape_bulletin_links():
    """Return list of {'url', 'text', 'is_pdf'} for CPI bulletin links."""
    print("Fetching main bulletins page …")
    resp = requests.get(BASE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cpi_section = soup.find("div", {"id": "1726482685031-986b6d76-980c"})
    if cpi_section is None:
        all_tabs = soup.find_all(
            "div", class_=re.compile(r"tab-pane|tab-content|wpb_tab_content|vc_tta-panel")
        )
        for tab in all_tabs:
            tab_text = tab.get_text(strip=True)[:200]
            if any(kw in tab_text.lower() for kw in ["consumer price", "cpi", "inflation"]):
                cpi_section = tab
                break
    if cpi_section is None:
        cpi_section = soup

    bulletin_links = []
    for a_tag in cpi_section.find_all("a", href=True):
        href = a_tag["href"]
        link_text = a_tag.get_text(strip=True)
        is_relevant = (
            href.endswith(".pdf")
            or "bulletin" in href.lower()
            or "cpi" in href.lower()
            or "consumer" in href.lower()
            or "inflation" in href.lower()
            or any(kw in link_text.lower() for kw in ["price", "cpi", "inflation", "bulletin"])
        )
        if is_relevant and href not in [l["url"] for l in bulletin_links]:
            bulletin_links.append({
                "url": urljoin(BASE_URL, href),
                "text": link_text,
                "is_pdf": href.endswith(".pdf"),
            })
    print(f"  Found {len(bulletin_links)} relevant links")
    return bulletin_links


def collect_pdf_urls(bulletin_links):
    """Resolve bulletin page links into direct English-PDF URLs."""
    pdf_urls = []
    for link in bulletin_links:
        if link["is_pdf"]:
            url_lower = link["url"].lower()
            if "-en" in url_lower or "-eng" in url_lower or "eng-" in url_lower:
                pdf_urls.append({"url": link["url"], "title": link["text"]})
        else:
            if link["url"].rstrip("/") == BASE_URL.rstrip("/"):
                continue
            if link["url"].rstrip("/").endswith("#1726482685031-986b6d76-980c"):
                continue
            try:
                page_resp = requests.get(link["url"], headers=HEADERS, timeout=30)
                page_resp.raise_for_status()
                page_soup = BeautifulSoup(page_resp.text, "html.parser")
                for a in page_soup.find_all("a", href=True):
                    h = a["href"]
                    if h.endswith(".pdf"):
                        h_lower = h.lower()
                        if ("-en" in h_lower or "-eng" in h_lower or "eng-" in h_lower) and "-ar" not in h_lower:
                            full_url = urljoin(link["url"], h)
                            if full_url not in [p["url"] for p in pdf_urls]:
                                pdf_urls.append({"url": full_url, "title": link["text"]})
                time.sleep(1)
            except Exception as e:
                print(f"  ⚠ Error visiting {link['url']}: {e}")
    print(f"  Total English PDFs found: {len(pdf_urls)}")
    return pdf_urls


def download_pdfs(pdf_urls):
    """Download PDFs that are not already cached. Returns list of local paths."""
    downloaded = []
    new_count = 0
    for i, pdf in enumerate(pdf_urls):
        filename = unquote(pdf["url"].split("/")[-1])
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            downloaded.append(filepath)
            continue
        try:
            print(f"  [{i+1}/{len(pdf_urls)}] Downloading {filename} …")
            r = requests.get(pdf["url"], headers=HEADERS, timeout=60)
            r.raise_for_status()
            if b"%PDF" in r.content[:8] or "pdf" in r.headers.get("Content-Type", ""):
                with open(filepath, "wb") as f:
                    f.write(r.content)
                downloaded.append(filepath)
                new_count += 1
            time.sleep(1.5)
        except Exception as e:
            print(f"  ⚠ Download failed: {e}")
    print(f"  {new_count} new PDFs downloaded, {len(downloaded)} total on disk")
    return downloaded


# ═══════════════════════════════════════════════════════════════════════
#  2. CPI EXTRACTION
# ═══════════════════════════════════════════════════════════════════════

def normalise_commodity(label):
    label = " ".join(label.split())
    return COMMODITY_ALIASES.get(label, label)


def extract_date_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:5]:
            text = page.extract_text() or ""
            m = re.search(
                r"Issue\s*\(?\s*\d+\s*\)?\s*[–\-—]\s*([A-Za-z]+)\s+(\d{4})", text
            )
            if m:
                month_num = MONTH_NAME_TO_NUM.get(m.group(1).lower())
                if month_num:
                    return datetime(int(m.group(2)), month_num, 1)
    fname = os.path.basename(pdf_path)
    m = re.search(r"Issue-(\d+)-(\d{4})", fname)
    if m:
        return datetime(int(m.group(2)), int(m.group(1)), 1)
    return None


def extract_all_cpi_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in reversed(pdf.pages):
            text = page.extract_text() or ""
            if "all commodities" not in text.lower():
                continue
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                header = table[0]
                if not any(c and "SYRIA" in str(c).upper() for c in header):
                    continue
                pct_check = False
                for row in table:
                    if row[0] and "all commodities" in str(row[0]).lower():
                        if any("%" in str(c or "") for c in row):
                            pct_check = True
                        break
                if pct_check:
                    continue
                result = {}
                for row in table:
                    raw_label = str(row[0] or "").strip()
                    if not raw_label:
                        continue
                    label = normalise_commodity(raw_label)
                    gov_values = {}
                    for idx, name in GOVERNORATE_MAP.items():
                        raw = str(row[idx] or "").replace(",", "").strip()
                        try:
                            gov_values[name] = int(raw)
                        except ValueError:
                            pass
                    if gov_values:
                        result[label] = gov_values
                if "All commodities" in result and "SYRIA" in result["All commodities"]:
                    return result
    return None


def _parse_pct(val):
    if not val:
        return None
    clean = val.replace("%", "").replace("\n", "").strip()
    if clean.endswith("-"):
        clean = "-" + clean[:-1]
    try:
        return float(clean)
    except ValueError:
        return None


def extract_mom_table_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in reversed(pdf.pages):
            text = page.extract_text() or ""
            if "monthly inflation" not in text.lower() and "appendix (2)" not in text.lower():
                continue
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                header = table[0]
                if not any(c and "SYRIA" in str(c).upper() for c in header):
                    continue
                has_pct = False
                for row in table:
                    if row[0] and "all commodities" in str(row[0]).lower():
                        if any("%" in str(c or "") for c in row):
                            has_pct = True
                        break
                if not has_pct:
                    continue
                result = {}
                for row in table:
                    raw_label = str(row[0] or "").strip()
                    if not raw_label:
                        continue
                    label = normalise_commodity(raw_label)
                    gov_pcts = {}
                    for idx, name in GOVERNORATE_MAP.items():
                        p = _parse_pct(str(row[idx] or ""))
                        if p is not None:
                            gov_pcts[name] = p
                    if gov_pcts:
                        result[label] = gov_pcts
                if "All commodities" in result:
                    return result
    return None


def back_calculate_previous_month(abs_cpi, mom_pct):
    result = {}
    for commodity in abs_cpi:
        if commodity not in mom_pct:
            continue
        gov_vals = {}
        for gov in abs_cpi[commodity]:
            if gov in mom_pct[commodity]:
                gov_vals[gov] = round(abs_cpi[commodity][gov] / (1 + mom_pct[commodity][gov] / 100))
        if gov_vals:
            result[commodity] = gov_vals
    return result


def extract_cpi_from_chart(pdf_path, page_idx=6):
    result = {}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_idx >= len(pdf.pages):
                return result
            page = pdf.pages[page_idx]
            text = page.extract_text() or ""
            if "cpi" not in text.lower() or "figure" not in text.lower():
                return result
            words = page.extract_words(x_tolerance=1, y_tolerance=1)
            cpi_labels = []
            for w in words:
                x0, top, txt = float(w["x0"]), float(w["top"]), w["text"].strip()
                if 85 <= x0 <= 300 and 420 <= top <= 560:
                    if txt.isdigit() and len(txt) == 3 and 600 <= int(txt) <= 999:
                        cpi_labels.append((x0, int(txt)))
            if len(cpi_labels) != 13:
                return result
            cpi_labels.sort(key=lambda c: c[0])
            bulletin_date = extract_date_from_pdf(pdf_path)
            if not bulletin_date:
                return result
            chart_months = []
            for i in range(12, -1, -1):
                m = bulletin_date.month - i
                y = bulletin_date.year
                while m <= 0:
                    m += 12
                    y -= 1
                chart_months.append(datetime(y, m, 1))
            for (_, val), dt in zip(cpi_labels, chart_months):
                result[dt] = val
    except Exception:
        pass
    return result


# ═══════════════════════════════════════════════════════════════════════
#  3. WAGE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════

def _detect_area_cols(table):
    area_cols = {}
    header_text = {}
    for row in table[: min(5, len(table))]:
        for col_idx, cell in enumerate(row):
            txt = str(cell or "").strip().lower()
            if txt:
                header_text.setdefault(col_idx, "")
                header_text[col_idx] += " " + txt
    for col_idx, txt in header_text.items():
        txt = txt.strip()
        if any(k in txt for k in ["gos", "syp", "caretaker", "former"]):
            area_cols[col_idx] = "SYP-Governed"
        elif any(k in txt for k in ["sig", "ssg", "tl-", "tl area", "tl governe"]):
            area_cols[col_idx] = "TL-Governed"
        elif "aa" in (txt.split()[0] if txt.split() else ""):
            area_cols[col_idx] = "AA"
        elif "whole of" in txt or txt == "syria":
            area_cols[col_idx] = "Whole of Syria"
    return area_cols if len(area_cols) >= 3 else None


def _find_value_cols(table, area_cols):
    seen_areas = set()
    value_cols = {}
    for col_idx, area_name in sorted(area_cols.items()):
        if area_name in seen_areas:
            continue
        seen_areas.add(area_name)
        candidates = []
        for try_col in [col_idx, col_idx + 1, col_idx - 1, col_idx + 2]:
            if try_col < 0:
                continue
            count = sum(
                1
                for row in table[2:]
                if try_col < len(row)
                and str(row[try_col] or "").replace(",", "").replace(" ", "").strip().isdigit()
            )
            if count > 0:
                candidates.append((count, try_col))
        candidates.sort(reverse=True)
        if candidates:
            value_cols[area_name] = [c[1] for c in candidates]
    return value_cols


def _classify_wage(label, sector):
    label_lower = label.lower()
    for key, val in WAGE_ALIASES.items():
        if key in label_lower:
            if val is not None:
                return val
            if sector == "public":
                return "Public: University Grad"
            elif sector == "civil":
                return "Civil: University Grad"
            break
    return None


def extract_wages_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Scan all pages — script runs weekly, no rush
            for page in pdf.pages:
                try:
                    text = page.extract_text() or ""
                except Exception:
                    continue
                if "average monthly wage" not in text.lower():
                    continue
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 5:
                        continue
                    flat = " ".join(str(c or "") for row in table for c in row).lower()
                    if "public sector" not in flat:
                        continue
                    area_cols = _detect_area_cols(table)
                    if not area_cols:
                        continue
                    value_cols = _find_value_cols(table, area_cols)
                    if len(value_cols) < 3:
                        continue
                    result = {}
                    current_sector = None
                    for i in range(len(table)):
                        row = table[i]
                        label = str(row[0] or "").strip() + " " + str(row[1] or "").strip()
                        label = " ".join(label.split()).strip()
                        if i + 1 < len(table):
                            nxt = " ".join(
                                (str(table[i + 1][0] or "") + " " + str(table[i + 1][1] or "")).split()
                            ).strip()
                            if nxt and (nxt.startswith("(") or nxt.endswith(")")):
                                label = label + " " + nxt
                        label_lower = label.lower()
                        if "public sector" in label_lower:
                            current_sector = "public"
                            continue
                        elif "private sector" in label_lower:
                            current_sector = "private"
                            continue
                        elif "civil" in label_lower and (
                            "sector" in label_lower or "society" in label_lower
                        ):
                            current_sector = "civil"
                            continue
                        area_vals = {}
                        for area_name, col_candidates in value_cols.items():
                            for try_col in col_candidates:
                                if try_col < len(row):
                                    raw = str(row[try_col] or "").replace(",", "").replace(" ", "").strip()
                                    try:
                                        area_vals[area_name] = int(raw)
                                        break
                                    except ValueError:
                                        pass
                        if not area_vals:
                            continue
                        wage_cat = _classify_wage(label, current_sector)
                        if wage_cat:
                            result[wage_cat] = area_vals
                    if len(result) >= 4:
                        return result
    except Exception as e:
        print(f"  ⚠ Wage extraction error in {os.path.basename(pdf_path)}: {e}")
    return None


# ═══════════════════════════════════════════════════════════════════════
#  4. PIPELINE
# ═══════════════════════════════════════════════════════════════════════

def run():
    # ── Scrape & download ──
    links = scrape_bulletin_links()
    pdf_urls = collect_pdf_urls(links)
    download_pdfs(pdf_urls)

    # ── Discover local PDFs ──
    pdf_files = sorted(
        f for f in os.listdir(DATA_DIR)
        if f.lower().startswith("monthly") and f.endswith(".pdf")
    )
    print(f"\n{len(pdf_files)} PDF bulletins on disk")

    # ── Extract CPI ──
    records = []
    back_calc_candidates = []

    for fname in pdf_files:
        pdf_path = os.path.join(DATA_DIR, fname)
        bulletin_date = extract_date_from_pdf(pdf_path)
        if bulletin_date is None:
            print(f"  ⚠ Skipping {fname}: cannot determine date")
            continue
        all_cpi = extract_all_cpi_from_pdf(pdf_path)
        if all_cpi is not None:
            records.append({
                "date": bulletin_date,
                "cpi": all_cpi["All commodities"]["SYRIA"],
                "governorates": all_cpi["All commodities"],
                "commodities": all_cpi,
                "file": fname,
            })
            mom_pct = extract_mom_table_from_pdf(pdf_path)
            if mom_pct:
                back_calc_candidates.append((pdf_path, bulletin_date, all_cpi, mom_pct))
        else:
            print(f"  ⚠ No CPI table in {fname}")

    records.sort(key=lambda r: r["date"])

    # ── Back-calculate missing months ──
    existing_dates = {r["date"] for r in records}
    for pdf_path, bulletin_date, abs_cpi, mom_pct in back_calc_candidates:
        prev_date = datetime(
            bulletin_date.year - (1 if bulletin_date.month == 1 else 0),
            12 if bulletin_date.month == 1 else bulletin_date.month - 1,
            1,
        )
        if prev_date not in existing_dates:
            prev_cpi = back_calculate_previous_month(abs_cpi, mom_pct)
            if "All commodities" in prev_cpi and "SYRIA" in prev_cpi["All commodities"]:
                records.append({
                    "date": prev_date,
                    "cpi": prev_cpi["All commodities"]["SYRIA"],
                    "governorates": prev_cpi["All commodities"],
                    "commodities": prev_cpi,
                    "file": f"[back-calculated from {os.path.basename(pdf_path)}]",
                })
                existing_dates.add(prev_date)
                print(f"  ✓ Back-calculated {prev_date.strftime('%B %Y')}")

    records.sort(key=lambda r: r["date"])

    # ── Chart-extracted gap fill ──
    existing_dates = {r["date"] for r in records}
    for fname in pdf_files:
        pdf_path = os.path.join(DATA_DIR, fname)
        for dt, cpi_val in extract_cpi_from_chart(pdf_path).items():
            if dt not in existing_dates:
                records.append({
                    "date": dt,
                    "cpi": cpi_val,
                    "governorates": {"SYRIA": cpi_val},
                    "commodities": {"All commodities": {"SYRIA": cpi_val}},
                    "file": f"[chart-extracted from {fname}]",
                })
                existing_dates.add(dt)
                print(f"  ✓ Chart-extracted {dt.strftime('%B %Y')} = {cpi_val}")

    records.sort(key=lambda r: r["date"])
    all_commodities = sorted({c for r in records for c in r["commodities"]})

    # ── Extract wages ──
    wage_records = []
    for fname in pdf_files:
        pdf_path = os.path.join(DATA_DIR, fname)
        bulletin_date = extract_date_from_pdf(pdf_path)
        if bulletin_date is None:
            continue
        wages = extract_wages_from_pdf(pdf_path)
        if wages is not None:
            wage_records.append({"date": bulletin_date, "wages": wages, "file": fname})

    wage_records.sort(key=lambda r: r["date"])
    all_wage_cats = sorted({c for r in wage_records for c in r["wages"]})
    all_areas = sorted({a for r in wage_records for v in r["wages"].values() for a in v})

    print(f"\n✓ {len(records)} CPI months, {len(wage_records)} wage months")
    if records:
        print(
            f"  CPI range: {records[0]['date'].strftime('%b %Y')} — "
            f"{records[-1]['date'].strftime('%b %Y')}"
        )

    # ── Export JSON ──
    all_govs = sorted({g for r in records for g in r["governorates"] if g != "SYRIA"})
    all_commodities_export = sorted(
        {c for r in records for c in r["commodities"] if c != "All commodities"}
    )
    gov_list = ["SYRIA"] + all_govs
    commodity_list = ["All commodities"] + all_commodities_export

    export_data = {
        "base_year": 2021,
        "source": "Syrian Center for Policy Research (SCPR)",
        "source_url": "https://scpr-syria.org/publications/bulletins/",
        "governorates": gov_list,
        "commodities": commodity_list,
        "records": [
            {
                "date": r["date"].strftime("%Y-%m-%d"),
                **{
                    commodity: {gov: r["commodities"].get(commodity, {}).get(gov) for gov in gov_list}
                    for commodity in commodity_list
                },
            }
            for r in records
        ],
        "wage_categories": sorted(all_wage_cats),
        "control_areas": sorted(all_areas),
        "wage_records": [
            {
                "date": wr["date"].strftime("%Y-%m-%d"),
                **{cat: wr["wages"].get(cat, {}) for cat in all_wage_cats},
            }
            for wr in wage_records
        ],
    }

    # ── Check if data actually changed ──
    new_json = json.dumps(export_data, indent=2)
    old_hash = None
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            old_hash = hashlib.md5(f.read().encode()).hexdigest()

    new_hash = hashlib.md5(new_json.encode()).hexdigest()

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        f.write(new_json)

    if old_hash == new_hash:
        print("\n✓ No data changes — JSON is identical")
    else:
        print(f"\n★ Data updated — {JSON_PATH}")
        print(
            f"  {len(records)} CPI records × {len(gov_list)} regions × "
            f"{len(commodity_list)} commodities"
        )
        print(
            f"  {len(wage_records)} wage records × {len(all_wage_cats)} categories × "
            f"{len(all_areas)} areas"
        )


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"\n✗ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
