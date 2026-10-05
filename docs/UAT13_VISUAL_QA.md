# UAT.13 Clean Visual Rebuild QA

Baseline: `v5.0.0-uat.11`. UAT.12 visual direction is rejected and preserved only in Git history/safety references. Status remains **UAT REMEDIATION IN PROGRESS**.

## Functional carry-forward

Retained and reimplemented independently of rejected composition: shared picker close/focus behavior; output-only blank rows in definitions, snapshots, preview, XLSX/PDF/DOCX; Mother Properties report entry; canonical region and Special Center scopes; explicit print plumbing.

## Human-like visual review

The Chromium matrix produced 78 screen captures at 1366×768, 1600×900 and 1920×1080. Reviewed Dashboard, Regions landing, Region 14, Special Centers, one Special Center, Mother list/dossier, Commercial list/dossier, contracts, circulation, auction picker, reports and print view. Checks passed for horizontal shell, balanced header identity, compact controls, readable tables, RTL, coherent toolbar placement, absence of sidebar/right rail, non-empty landing content, compact center grid, drillable KPI hierarchy and dossier density.

The dedicated print screenshot was reviewed: navigation, account menu, interactive controls, UI footer and SMK credit are absent; official logo and three organizational lines, page context, KPI summary and supporting data remain. Generated XLSX/PDF/DOCX were also inspected with five output-only blank rows; XLSX RTL and DOCX bidi were verified programmatically and the PDF was rendered visually.

## Owner rejection regression checklist

- no region sidebar or right rail;
- no narrow Special Centers text column;
- no dead-end or unexplained KPI;
- no giant action controls or detached print action;
- no page-specific palette;
- no visually empty Regions landing;
- no application chrome or SMK credit in official print/output.

Owner Human UAT remains required before acceptance.
