# SAMA — Owner Physical Auction Golden Master Manifest

Date supplied by Owner: 1405-07-12 / 2026-10-04
Status: OWNER-SUPPLIED PHYSICAL AUTHORITY INPUTS

## Purpose

These files were supplied directly by the Owner to unblock the UAT.16 Auction End-to-End implementation. They are physical source/reference documents and must be preserved unchanged. Legal wording must not be invented, normalized, paraphrased, or silently corrected.

For scanned PDFs, the required process is:

`scan -> transcription -> page-by-page comparison -> human-readable diff -> frozen typed template`

Do not treat OCR output alone as authoritative text.

## Persistent package location

The complete raw package has been stored in the user's ChatGPT Library at:

`/SAMA/authority/auction/SAMA_AUCTION_GOLDEN_MASTERS_OWNER_1405-07-12.zip`

Package SHA-256:

`664e663eeef870a83115259861ee25d6eb736605daf63702970090db1d42f467`

If the execution environment cannot access the ChatGPT Library package directly, STOP only the physical-template-ingest step and request the single ZIP package from the Owner. Do not invent replacement documents.

## Raw files and SHA-256

1. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۱.۴۵(1).pdf`
   - SHA-256: `23cd5a223448cbb44f8460903397517be51787efaf846d17684c70b2d4ad2960`
   - Scanned auction conditions/forms package. Includes envelope-cover content in the scanned pages. Final business-category mapping must be derived from the actual document text and Source Pack Index, not from timestamp/filename alone.

2. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۱.۴۹(1).pdf`
   - SHA-256: `19bb899d05a575401f514b25a0c0e96d72424818fd5394687da10b8307e8491c`
   - Scanned contract/related legal reference. Classify only after inspecting the actual content.

3. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۱.۵۱(1).pdf`
   - SHA-256: `d827146ccf7b40ce72a0c20bd90b61c16bbb0e0b0c00d9f3a94450b31329b43d`
   - Café/restaurant auction pack scan. Contains auction conditions/forms and price-proposal material.

4. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۱.۵۵(1).pdf`
   - SHA-256: `4a68223e1803f85a4bbfa14e21cd044c059357305a69e5ddf8fee34260704dfb`
   - Scanned lease-contract reference; visible content includes café/restaurant usage. Preserve source wording.

5. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۱.۵۷(1).pdf`
   - SHA-256: `6d546c8fec03de22b4394e68896d5f39c23a883850254709ae2040b710fab026`
   - Sports-space auction pack scan. Contains sports-specific conditions and auction forms.

6. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۲.۰۳(1).pdf`
   - SHA-256: `47135564de689546c58f7c3985ae2fcec8657e3216460f34e588e631967cb111`
   - Scanned contract reference. Classify against the Source Pack Index and actual clauses before registering category.

7. `نمونه صورتجلسه بازگشایی پاکات(1).docx`
   - SHA-256: `2d698909a182c249a218bd75af2e770d5be91156d7d6c84f3715860e3b77b566`
   - Opening-session minutes structural/content reference.
   - Contains auction authorization, term, base rent, investment, guarantee/deposit, publication date, invitation number, meeting date/location, attendees, Envelope A/B/C review, bid amount, result and signatures.

8. `تم اصلی 01.pptx`
   - SHA-256: `ae13ed4cad9100f694351e3832e3a48e156d01ee57edd5ffd19de8387d3c36c7`
   - Role: PRESENTATION THEME MASTER.
   - Use as the preferred visual/theme basis for newly generated opening-session decks.

9. `finall report mozayede 1405.pptx`
   - SHA-256: `b2597cdf547066c4e96a586a5c38a97bb4cd42f1b91a435782e1fb13b1ccbd1c`
   - Role: REAL FILLED REGRESSION REFERENCE.
   - Contains populated slides for actual auction spaces with code, name, use, area, region, base price, contract term, optional investment amount, location, notes and images.
   - Use to validate real-world content density and field population, not as current canonical operational data.

10. `نهایی.pptx`
    - SHA-256: `acac967760f4e017c09c92879ffa396fd0fa41844557b203270f9a66ff22c8cd`
    - Role: OPENING-SESSION CONTENT/STRUCTURE REFERENCE.
    - Contains cover, general auction information, auction process, publicity/information section, and repeated per-space slides.

## Presentation role decision

Use the three PPTX files with distinct roles:

- `تم اصلی 01.pptx` = visual/theme master
- `نهایی.pptx` = content/structure reference
- `finall report mozayede 1405.pptx` = filled example and regression reference

Do not blindly clone one file for every purpose.

## Existing project/source references to reconcile

Reconcile these physical files against existing project references such as:

- `SAMA_NEXT_SOURCE_PACK_INDEX.md`
- `SAMA_Auction_Document_Field_Matrix_v1.xlsx`
- `SAMA_Auction_Documents_FieldID_Approval_v1.pdf`
- latest Owner/FROZEN rulebook and MD authority
- current official logo source

Where source references conflict, use authority precedence:

`Latest explicit Owner decision > current FINAL/FROZEN authority > older FROZEN > review/reference material > implementation inference`

## Required physical-template categories

The final template registry must explicitly cover, when supported by the physical sources:

### COMMERCIAL
- general/specific conditions
- Envelope A
- Envelope B
- Envelope C
- price proposal
- non-interference declaration
- other required auction forms
- contract reference

### CAFE
- general/specific conditions
- Envelope A/B/C/forms as applicable
- price proposal
- commitments/declarations
- contract reference

### SPORTS
- general/specific conditions
- Envelope A/B/C/forms as applicable
- price proposal
- commitments/declarations
- contract reference

### SHARED
- opening-session minutes
- commission/result documents
- presentation theme/reference
- official branding assets

## Non-negotiable rules

- Preserve originals unchanged.
- Register SHA-256 for every physical file and every generated frozen template.
- Never auto-select the legal auction winner.
- Never infer missing legal text.
- Never regenerate finalized documents in-place; corrections create a new version.
- Generated official documents must be driven by an immutable AuctionDocumentSnapshot.
- Screen, minutes, PPTX and result documents must use the same frozen session/result dataset.
- Historical imported auctions remain historical facts; do not synthesize retrospective workflow events.

See `docs/CODEX_AUCTION_UAT16_RESUME_PROMPT.md` for the execution mission.