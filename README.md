# All Civilian Agency FAR Class Deviations Matrix

A per-agency tracker of every FAR Part 52 provision and clause, stamped with each civilian agency's class-deviation effective date issued under the Revolutionary FAR Overhaul (RFO).

The Federal Acquisition Regulation is undergoing a top-to-bottom rewrite — the *Revolutionary FAR Overhaul* — driven by Executive Order 14275 (April 2025) and OMB memo M-25-26. Each civilian executive agency has issued (and continues to issue) class deviations from the existing FAR while the rewrite is staged in. This matrix lets you look up, agency by agency, which 52.* clauses an agency has deviated from and on what date.

> DoD class deviations follow a different cadence under DFARS and are intentionally out of scope.

## What's in the repo

- `far_provisions_clauses_matrix.xlsx` — the master workbook. **34 tabs**: a README tab plus one tab per civilian agency (33 agencies).
- `RFO_Part52_All_Agencies.zip` — the master workbook plus the 33 individual per-agency workbooks (one xlsx each), zipped together for offline browsing.

**Master row count: 702** — every `52.*` provision and clause from the pre-RFO FAR Part 52, mapped against each agency's deviation memos.

## Per-agency tab schema

| Column | Description |
|---|---|
| Type | `Provision` or `Clause` |
| Number | FAR 52.x clause/provision identifier |
| Part | FAR Part the clause belongs to |
| Pre-RFO Title | Original FAR title |
| Pre-RFO Date | Original effective date |
| RFO Title | Title under the RFO; `[Reserved]` indicates the FAR Council removed the clause |
| `<Agency>` Deviation Effective Date | The agency's class-deviation effective date for this clause's parent Part. `--` (or empty) when no agency-specific deviation was found. `Reserved` rows from the blank template are left untouched. |
| Disposition | FAR Council baseline action: `No Change`, `Removed`, `Updated`, `Reserved`, etc. |
| Notes | Agency-specific commentary when the deviation memo flags something non-standard for the parent Part. `--` otherwise. |

## Filling logic (Effective Date column G)

- For each FAR Part addressed by an agency memo, the **earliest** memo's effective date is stamped on every clause in that part — but only on rows whose Disposition is something other than `No Change`.
- **Per-clause overrides:** if a memo explicitly names a 52.x clause and assigns it `Removed`, `Updated`, `Reserved`, or `Added`, that memo's date wins for that single clause.
- On `No Change` rows, only an explicit `Removed` override can stamp a date — `Reserved` / `Updated` / `Added` on a No-Change row is treated as low-confidence and skipped (open-model false-positive guard).
- Rows where the blank template's effective-date already says `Reserved` are left untouched: those are FAR Council removals the agency adopted as-is.

## Notes column

- One note per agency memo that has agency-specific commentary worth flagging (the LLM extractor's `general_notes` field).
- Placed on the first stamped row whose Part is in scope of that memo.
- Vanilla "agency adopts FAR Council model verbatim" memos produce no note.

## Agencies covered (33)

CFTC · CPSC · DHS · DOC · DOE · DOI · DOJ · DOL · DOS · DOT · ED · EPA · FEC · FMC · GSA · HHS · HUD · MCC · MSPB · NARA · NASA · NLRB · NRC · OPM · OSHRC · PBGC · SEC · SSA · Treasury · Udall Foundation · USAID · USDA · VA

> The **GSA** tab is the reference (ground-truth) filled template that ships with the blank template; it was **not** produced by this pipeline.

## Methodology and caveats

- **Master clause list source:** the WarU Provision & Clause Matrix blank template (May 2026 cut).
- **Agency deviation memos source:** [acqagent/rfo-deviations](https://github.com/acqagent/rfo-deviations) — 1,192 PDFs scraped from acquisition.gov.
- **Extraction model:** Claude Opus 4.7 (max effort) with a structured JSON schema, one bundled prompt per agency. Each agency's memos are fed to the model together so it can reconcile parts addressed, effective dates, and per-clause overrides across all of that agency's PDFs in a single pass.
- **Rollup granularity.** Effective dates roll up at the FAR Part level by default. Per-clause overrides only fire when a memo explicitly names the 52.x clause by number.
- **Small-corpus agencies.** OSHRC, NLRB, FEC, USAID, FMC have very small corpora (1–2 PDFs); their tabs may have few or no filled dates.
- **Source links can rot.** Some agency deviation PDFs are removed or replaced over time. Cross-reference with the upstream acquisition.gov guide if precision matters.
- **Verify before relying.** Effective dates are extracted by an LLM from PDF text. Spot-check edge cases against the source memos before relying on them in compliance decisions.

## Building / regenerating

The pipeline lives outside this repo at `far-deviations/scripts/process_agency.py`. It reads the corpus from [acqagent/rfo-deviations](https://github.com/acqagent/rfo-deviations) and a blank P&C template, then:

1. Pulls every PDF assigned to the requested agency from the manifest.
2. Extracts text via `pdfplumber` (cached per-agency).
3. Bundles all of that agency's PDF text into one Claude Opus 4.7 max-effort call with a JSON schema that captures effective dates, parts addressed, and per-clause overrides.
4. Stamps the extracted dates and notes into a copy of the blank template.

The 33 agency workbooks are then merged into `far_provisions_clauses_matrix.xlsx` by `build_master.py` (one tab per agency plus a README tab).

## License

The underlying provisions, clauses, and agency deviation memoranda are works of the United States Government and are in the public domain under [17 U.S.C. § 105](https://www.copyright.gov/title17/92chap1.html#105). The matrix layout, code, and README in this repo are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — attribution requested but not required for the underlying federal documents.

## Citation

If you use this matrix in research, please cite as:

> AcqAgent. *All Civilian Agency FAR Class Deviations Matrix*, version 2026-05-03. https://github.com/acqagent/all-civ-agency-far-cds-matrix
