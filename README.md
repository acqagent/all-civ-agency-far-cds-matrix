# All Civilian Agency FAR Class Deviations Matrix

A per-agency, per-clause matrix of every FAR Part 52 provision and clause cross-referenced against the **civilian agency class deviations** issued under the Revolutionary FAR Overhaul (RFO).

The Federal Acquisition Regulation is undergoing a top-to-bottom rewrite — the *Revolutionary FAR Overhaul* — driven by Executive Order 14275 (April 2025) and OMB memo M-25-26. Each civilian executive agency has issued (and continues to issue) class deviations from the existing FAR while the rewrite is staged in. This matrix lets you see, at a glance, which agency has deviated from which FAR Part, and what status each individual provision/clause has under the RFO.

> DoD class deviations follow a different cadence under DFARS and are intentionally out of scope.

## What's in the workbook

`far_provisions_clauses_matrix.xlsx` — one tab per civilian agency (34 tabs) plus a README tab.

**Master row count: 867** — every `52.*` provision and clause from the pre-RFO FAR Part 52 plus the RFO additions, including Alternates.

| Status | Count | Meaning |
|---|---:|---|
| Retained | 684 | Still in post-RFO FAR Part 52 |
| Removed by RFO | 173 | Pre-RFO entry retired by the RFO |
| Added by RFO | 10 | New entries introduced by the RFO (90-series + new Alternates) |

## Per-agency tab schema

| Column | Description |
|---|---|
| FAR Part | Derived from the clause number (e.g., 52.203-3 → Part 3, 52.252-1 → Part 52) |
| Number | Clause/provision number, including Alternate variants |
| Title | As published in the FAR |
| Type | `Provision` or `Clause` (yellow fill = provision, blue fill = clause) |
| RFO Status | `Retained` / `Removed by RFO` / `Added by RFO` (red fill = removed, green fill = added) |
| Effective Date (52.103) | Clause's effective date as published in FAR Part 52. Per FAR 52.103(a), `(DEVIATION)` is appended when the agency has issued a class deviation that covers this clause's parent Part. |
| Prescription FAR Ref | The FAR section that prescribes the clause's use (e.g., `3.202`) |
| `<Agency>` Deviation Date | The agency's class-deviation date for the parent FAR Part |
| Disposition | `Updated` if the agency has issued a class deviation for that Part |
| Source / Notes | Source PDF and scope language from the agency's deviation memo |
| Prescription Text | Full long-form prescription guidance |

Rows are gray-shaded when the agency has **not** issued a class deviation for that FAR Part.

## Agencies covered (34)

CFTC · CPSC · DHS · DOC · DOE · DOI · DOJ · DOL · DOS · DOT · ED · EPA · FEC · FMC · GSA · HHS · HUD · MCC · MSPB · NARA · NASA · NLRB · NRC · OPM · OSHRC · PBGC · Peace Corps · SEC · SSA · Treasury · Udall Foundation · USAID · USDA · VA

## Methodology and caveats

- **Master list source:** the WarU Provision & Clause Matrix, version 2026-04-29.
- **Agency deviation dates source:** [acqagent/rfo-deviations](https://github.com/acqagent/rfo-deviations) — extracted from the deviation PDFs linked from the [acquisition.gov FAR Overhaul deviation guide](https://www.acquisition.gov/far-overhaul/far-part-deviation-guide).
- **Rollup granularity.** Agency deviation dates are rolled up at the FAR Part level. A removed clause inside a deviated Part inherits the Part's deviation date because adopting the RFO Part deviation effectively retires the removed clause. Per-clause deviation dates would require parsing individual agency PDFs and are not yet captured here.
- **Source links can rot.** Some agency deviation PDFs are removed or replaced over time. Cross-reference with the upstream guide if precision matters.

## Building / regenerating

`build_matrix.py` is the generator. It expects three local inputs:

1. `WarU Provision & Clause Matrix (042922026).xlsx` (master 52.* list)
2. `far_class_deviations-2026-04-27.xlsx` (raw scrape, from [acqagent/rfo-deviations](https://github.com/acqagent/rfo-deviations))
3. `far_class_deviations_hhs_format.xlsx` (per-agency Part-level rollup)

Edit the path constants at the top of `build_matrix.py` to point at where you keep those files locally, then run:

```
python build_matrix.py
```

## License

The underlying provisions, clauses, and agency deviation memoranda are works of the United States Government and are in the public domain under [17 U.S.C. § 105](https://www.copyright.gov/title17/92chap1.html#105). The matrix layout, code, and README in this repo are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — attribution requested but not required for the underlying federal documents.

## Citation

If you use this matrix in research, please cite as:

> AcqAgent. *All Civilian Agency FAR Class Deviations Matrix*, version 2026-04-30. https://github.com/acqagent/all-civ-agency-far-cds-matrix
