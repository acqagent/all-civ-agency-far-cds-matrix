"""Build a per-agency provision/clause matrix.

Master row source: WarU "Provision & Clause Matrix" (042922026).xlsx
  - Includes every 52.* entry (pre-RFO + retained + RFO additions = ~867 rows)
  - Carries P/C, prescription FAR ref, prescription text, effective date
  - "RFO" column distinguishes Removed-by-RFO vs Retained vs Added-by-RFO

Agency dates are rolled up at the FAR Part level from the existing HHS-format file
(which itself was derived from far_class_deviations-2026-04-27.xlsx in this repo).

Output:
  - far_provisions_clauses_matrix.xlsx
    One README + one tab per agency. Each tab has every 52.* entry as a row.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

REPO = Path(r"C:\Users\tijki\rfo-deviations-repo")
DOWNLOADS = Path(r"C:\Users\tijki\Downloads")
DESKTOP = Path(r"C:\Users\tijki\Desktop")

WARU_XLSX = DESKTOP / "WarU Provision & Clause Matrix (042922026).xlsx"
HHS_FORMAT_XLSX = DOWNLOADS / "far_class_deviations_hhs_format.xlsx"
OUTPUT_XLSX = DOWNLOADS / "far_provisions_clauses_matrix.xlsx"

CLAUSE_NUM_RE = re.compile(r"^52\.(\d{3})-(\d+[A-Za-z]?)$")


def part_from_number(number: str) -> int | None:
    """52.203-3 -> Part 3.  52.252-1 -> Part 52."""
    base = number.split(",")[0].strip()
    m = CLAUSE_NUM_RE.match(base)
    if not m:
        return None
    return int(m.group(1)) - 200


def clean_pc(value) -> str:
    """Normalize 'P or C' cells. Strip unicode noise; map to Provision/Clause."""
    if not value:
        return ""
    s = "".join(ch for ch in str(value) if unicodedata.category(ch)[0] != "C" and ch.isascii())
    s = s.strip().rstrip("-_*").upper()
    if s.startswith("P"):
        return "Provision"
    if s.startswith("C"):
        return "Clause"
    return ""


def rfo_status(value) -> str:
    if value is None or str(value).strip() == "":
        return "Retained"
    s = str(value).strip().upper()
    if "X" in s:
        return "Removed by RFO"
    if s == "ADD":
        return "Added by RFO"
    return s  # surface anything unexpected verbatim


def normalize_date(value) -> str:
    """Strip wrapping noise and return date as a clean string."""
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%b %Y")
    return str(value).strip()


def load_master() -> list[dict]:
    """Load 52.* rows from the WarU matrix."""
    wb = openpyxl.load_workbook(WARU_XLSX, data_only=True)
    ws = wb["Matrix"]
    # Header row is 6; data starts at row 7.
    rows: list[dict] = []
    for r in range(7, ws.max_row + 1):
        num = ws.cell(row=r, column=2).value
        if not num or not isinstance(num, str):
            continue
        num_s = num.strip()
        if num_s.startswith("See notes"):
            continue
        if not num_s.startswith("52."):
            continue
        title = ws.cell(row=r, column=3).value or ""
        date = normalize_date(ws.cell(row=r, column=4).value)
        prescription_ref = ws.cell(row=r, column=5).value or ""
        prescription_text = ws.cell(row=r, column=6).value or ""
        pc = clean_pc(ws.cell(row=r, column=7).value)
        status = rfo_status(ws.cell(row=r, column=8).value)
        rows.append(
            {
                "number": num_s,
                "title": str(title).strip(),
                "type": pc,
                "rfo_status": status,
                "effective": date,
                "prescription_ref": str(prescription_ref).strip(),
                "prescription_text": str(prescription_text).strip(),
                "part": part_from_number(num_s),
            }
        )
    return rows


def load_agency_part_dates() -> dict[str, dict[int, dict]]:
    wb = openpyxl.load_workbook(HHS_FORMAT_XLSX, data_only=True)
    out: dict[str, dict[int, dict]] = {}
    for sname in wb.sheetnames:
        if sname == "README":
            continue
        ws = wb[sname]
        headers = [c.value for c in ws[1]]
        idx = {h: i for i, h in enumerate(headers) if h is not None}
        date_col = next((h for h in headers if h and isinstance(h, str) and h.endswith("Deviation Date")), None)
        if date_col is None:
            continue
        per_part: dict[int, dict] = {}
        for row in ws.iter_rows(min_row=2, values_only=True):
            try:
                part = int(str(row[idx["Part"]]).strip())
            except (TypeError, ValueError):
                continue
            per_part[part] = {
                "date": row[idx[date_col]] or "",
                "disposition": row[idx["Disposition"]] or "",
                "notes": row[idx["Notes"]] or "",
            }
        out[sname] = per_part
    return out


HEADER_FILL = PatternFill("solid", fgColor="1F2937")
HEADER_FONT = Font(color="FFFFFF", bold=True)
PROV_FILL = PatternFill("solid", fgColor="FEF3C7")
CLAUSE_FILL = PatternFill("solid", fgColor="DBEAFE")
REMOVED_FILL = PatternFill("solid", fgColor="FEE2E2")
ADDED_FILL = PatternFill("solid", fgColor="DCFCE7")
NO_DEV_FILL = PatternFill("solid", fgColor="F3F4F6")


def write_agency_sheet(wb, agency: str, master: list[dict], part_dates: dict[int, dict]) -> None:
    ws = wb.create_sheet(agency[:31])
    headers = [
        "FAR Part",
        "Number",
        "Title",
        "Type",
        "RFO Status",
        "Pre-RFO Effective Date",
        "Prescription FAR Ref",
        f"{agency} Deviation Date",
        "Disposition",
        "Source / Notes",
        "Prescription Text",
    ]
    ws.append(headers)
    for c in ws[1]:
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 28
    ws.freeze_panes = "C2"

    for entry in master:
        part = entry["part"]
        dev = part_dates.get(part) if part is not None else None
        row = [
            part if part is not None else "",
            entry["number"],
            entry["title"],
            entry["type"],
            entry["rfo_status"],
            entry["effective"],
            entry["prescription_ref"],
            dev["date"] if dev else "",
            dev["disposition"] if dev else "",
            dev["notes"] if dev else "",
            entry["prescription_text"],
        ]
        ws.append(row)
        r = ws.max_row

        # Type colors
        type_cell = ws.cell(row=r, column=4)
        if entry["type"] == "Provision":
            type_cell.fill = PROV_FILL
        elif entry["type"] == "Clause":
            type_cell.fill = CLAUSE_FILL

        # RFO Status colors
        status_cell = ws.cell(row=r, column=5)
        if entry["rfo_status"] == "Removed by RFO":
            status_cell.fill = REMOVED_FILL
        elif entry["rfo_status"] == "Added by RFO":
            status_cell.fill = ADDED_FILL

        # Gray out rows where this agency has no deviation for that Part
        if not dev:
            for col in range(1, len(headers) + 1):
                cell = ws.cell(row=r, column=col)
                if not cell.fill.fgColor or cell.fill.fgColor.rgb in (None, "00000000"):
                    cell.fill = NO_DEV_FILL

    widths = [8, 16, 50, 11, 16, 14, 22, 22, 14, 70, 70]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for col in (3, 10, 11):
        for row_cells in ws.iter_rows(min_row=2, min_col=col, max_col=col):
            for cell in row_cells:
                cell.alignment = Alignment(wrap_text=True, vertical="top")


def write_readme(wb, master_count: int, agencies: list[str], status_counts: dict[str, int]) -> None:
    ws = wb.create_sheet("README", 0)
    lines = [
        "FAR Class Deviations - Provision/Clause Matrix",
        "",
        f"Master row count: {master_count} (every 52.* entry from WarU matrix)",
        f"Agency tabs: {len(agencies)}",
        "",
        "RFO status breakdown:",
    ] + [f"  - {k}: {v}" for k, v in status_counts.items()] + [
        "",
        "Schema (per agency tab):",
        "  - FAR Part: derived from clause number (52.203-3 -> Part 3, 52.252-1 -> Part 52)",
        "  - Number: clause/provision number, including Alternate variants where present",
        "  - Title: as published; Alternate variants carry the alternate label",
        "  - Type: Provision or Clause (yellow = provision, blue = clause)",
        "  - RFO Status: Retained / Removed by RFO / Added by RFO (red = removed, green = added)",
        "  - Pre-RFO Effective Date: as published in FAR Part 52",
        "  - Prescription FAR Ref: prescribing FAR section (e.g., 3.202)",
        "  - <Agency> Deviation Date: agency's deviation date for the parent FAR Part",
        "  - Disposition: 'Updated' if the agency has issued a class deviation for that Part",
        "  - Source / Notes: source PDF and scope, from the agency's deviation memo",
        "  - Prescription Text: full prescription guidance from FAR (long-form)",
        "",
        "Visual cues:",
        "  - Yellow Type cell = Provision",
        "  - Blue Type cell = Clause",
        "  - Red RFO Status cell = Removed by RFO",
        "  - Green RFO Status cell = Added by RFO",
        "  - Gray row = no class deviation issued for that FAR Part by this agency",
        "",
        "Sources:",
        "  - Master:    WarU Provision & Clause Matrix (042922026).xlsx (Desktop)",
        "  - Per-agency Part-level deviation dates: far_class_deviations_hhs_format.xlsx (Downloads)",
        "  - Underlying corpus: github.com/acqagent/rfo-deviations",
        "",
        "Notes:",
        "  - Agency deviation dates are rolled up at the FAR Part level. A removed clause",
        "    in a deviated Part is shown with that Part's deviation date because adopting",
        "    the RFO Part deviation effectively retires the removed clause.",
        "  - Per-clause deviation dates would require parsing each agency's deviation PDF",
        "    and are not yet captured here.",
        "",
        "Agencies:",
        "  " + ", ".join(agencies),
    ]
    for line in lines:
        ws.append([line])
    ws.column_dimensions["A"].width = 120


def main() -> None:
    print("Loading WarU master...")
    master = load_master()
    status_counts: dict[str, int] = {}
    for e in master:
        status_counts[e["rfo_status"]] = status_counts.get(e["rfo_status"], 0) + 1
    print(f"  {len(master)} entries -> {status_counts}")

    print("Loading agency Part-level deviation dates...")
    agency_part_dates = load_agency_part_dates()
    agencies = list(agency_part_dates.keys())
    print(f"  {len(agencies)} agencies")

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    write_readme(wb, len(master), agencies, status_counts)
    for agency in agencies:
        write_agency_sheet(wb, agency, master, agency_part_dates[agency])
        print(f"  wrote sheet: {agency}")

    OUTPUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUTPUT_XLSX)
    print(f"\nWrote: {OUTPUT_XLSX}")


if __name__ == "__main__":
    main()
