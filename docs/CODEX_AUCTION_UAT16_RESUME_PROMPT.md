# SAMA — UAT.16 AUCTION END-TO-END RESUME
## Owner Physical Golden Masters Ingest + Complete Auction Lifecycle + Documents + Opening Session + PPT + Contract Handoff

Repository:
`sazmantehkarimian-wq/sama-1405`

Working branch:
`clean/sama-next`

Last released baseline:
`v5.0.0-uat.15`

PR:
`#2` — MUST REMAIN OPEN / UNMERGED

Official status:
`UAT REMEDIATION IN PROGRESS`

Current mission state:
UAT.16 was correctly BLOCKED because physical Golden Master documents were not available inside the active Authority tree. The Owner has now supplied the missing physical scans/DOCX/PPTX references. Resume the existing UAT.16 foundation; DO NOT start the project or auction subsystem over from scratch.

Read first:

- `authority/auction/OWNER_PHYSICAL_GOLDEN_MASTER_MANIFEST_1405-07-12.md`
- latest Owner/FROZEN MD/rulebook
- existing `SAMA_NEXT_SOURCE_PACK_INDEX.md`
- `SAMA_Auction_Document_Field_Matrix_v1.xlsx`
- `SAMA_Auction_Documents_FieldID_Approval_v1.pdf`
- existing auction models/services/tests
- UAT.15 reporting/document infrastructure

The complete raw Owner package is stored in the user's ChatGPT Library at:

`/SAMA/authority/auction/SAMA_AUCTION_GOLDEN_MASTERS_OWNER_1405-07-12.zip`

Package SHA-256:
`664e663eeef870a83115259861ee25d6eb736605daf63702970090db1d42f467`

If your execution environment cannot access ChatGPT Library, request exactly this ONE ZIP from Owner and continue. Do not ask for ten separate files. Do not invent substitutes.

---

# 0. EXECUTION CONTRACT

Use the complete autonomous loop:

`UNDERSTAND -> INSPECT -> IDENTIFY ROOT CAUSE -> RECONCILE AUTHORITY -> PLAN -> IMPLEMENT -> TEST -> REVIEW -> FIX -> RETEST -> VERIFY -> PACKAGE -> DELIVER`

Do not stop after scaffolding.
Do not produce demo-only screens.
Do not leave fake buttons.
Do not call something PASS merely because unit tests pass.
Do not invent legal text.
Do not guess missing relationships or values.
Do not silently mutate canonical historical data.

This mission is complete only when the end-to-end auction workflow actually works in browser and generated outputs have been structurally and visually verified.

---

# 1. PRESERVE ACCEPTED PRODUCT BASELINE

Do NOT redesign the global application.

The UAT.13/UAT.14/UAT.15 visual system is temporarily frozen.

Do not reopen:
- palette
- global header
- horizontal navigation
- dossier architecture
- typography system
- global spacing/density
- button system
- table system
- report engine visual language

UI changes are allowed only where required for the auction operational workflow.

Continue using:
- true RTL Persian
- local/offline Vazirmatn
- compact professional controls
- no permanent vertical sidebar
- no dark navy visual language
- official product name only `سما` in the application
- official outputs without software name or SMK credit

---

# 2. DO NOT LOSE THE EXISTING UAT.16 FOUNDATION

A blocked UAT.16 foundation was previously implemented and reportedly included:

- explicit entry sources `AUTOMATIC`, `MANAGER_ORDER`, `COMMISSION_ORDER`
- versioned Template and Document Snapshot models
- AuctionPeriod/AuctionLot fields for entry source/reference/pack/appraisal/base amount/snapshot/hash/contract handoff
- manual entry preserving the independent Rule Engine result
- fail-closed manual entry without valid path/reason/reference
- Preflight
- immutable Freeze with Snapshot + SHA-256

First inspect whether the foundation commit/report is available locally/remotely (reported short commit: `0095f0c`).

If it exists and is a valid descendant of UAT.15, continue from it.
If it does not exist on the remote branch but changes exist locally, preserve/reconcile them.
If unavailable, re-implement ONLY the missing foundation pieces from the blocked report without discarding UAT.15.

Never reset away useful foundation work merely because the release was blocked.

---

# 3. OWNER PHYSICAL AUTHORITY INGEST — FIRST HARD GATE

The Owner has now supplied physical source documents.

Ingest them into a controlled Authority location, for example:

`authority/auction/templates/owner-1405-07-12/`

Preserve raw files byte-for-byte.

Create:
- `MANIFEST.json` or equivalent
- `SHA256SUMS.txt`
- human-readable `README.md`
- template classification table

For every file record:
- original filename
- normalized internal filename
- SHA-256
- byte size
- MIME/type
- page count / slide count
- business category
- role
- authority level
- source date
- fixed-text status
- editable-field status
- transcription status
- visual-diff status
- template-registry key/version

Verify package hash before ingest.

Do not rename raw originals destructively.
A normalized copy/index may be created, but original filename/hash must remain traceable.

---

# 4. PHYSICAL SOURCE FILES — REQUIRED HASHES

Verify the following Owner-supplied hashes exactly:

1. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۱.۴۵(1).pdf`
`23cd5a223448cbb44f8460903397517be51787efaf846d17684c70b2d4ad2960`

2. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۱.۴۹(1).pdf`
`19bb899d05a575401f514b25a0c0e96d72424818fd5394687da10b8307e8491c`

3. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۱.۵۱(1).pdf`
`d827146ccf7b40ce72a0c20bd90b61c16bbb0e0b0c00d9f3a94450b31329b43d`

4. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۱.۵۵(1).pdf`
`4a68223e1803f85a4bbfa14e21cd044c059357305a69e5ddf8fee34260704dfb`

5. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۱.۵۷(1).pdf`
`6d546c8fec03de22b4394e68896d5f39c23a883850254709ae2040b710fab026`

6. `CamScanner ۲۰۲۶-۱۰-۰۴ ۱۲.۰۳(1).pdf`
`47135564de689546c58f7c3985ae2fcec8657e3216460f34e588e631967cb111`

7. `نمونه صورتجلسه بازگشایی پاکات(1).docx`
`2d698909a182c249a218bd75af2e770d5be91156d7d6c84f3715860e3b77b566`

8. `تم اصلی 01.pptx`
`ae13ed4cad9100f694351e3832e3a48e156d01ee57edd5ffd19de8387d3c36c7`

9. `finall report mozayede 1405.pptx`
`b2597cdf547066c4e96a586a5c38a97bb4cd42f1b91a435782e1fb13b1ccbd1c`

10. `نهایی.pptx`
`acac967760f4e017c09c92879ffa396fd0fa41844557b203270f9a66ff22c8cd`

Any mismatch is a hard ingest failure.

---

# 5. LEGAL-TEXT TRANSCRIPTION RULE

The scanned PDFs are images, not permission to rewrite legal wording.

Required process:

1. extract/transcribe text
2. preserve page mapping
3. compare typed text page-by-page against scan
4. produce a human-readable diff
5. mark unresolved/illegible fragments explicitly
6. freeze a typed template only after comparison

Do NOT:
- normalize language
- modernize spelling
- paraphrase
- merge clauses
- silently correct numbers/dates
- invent missing words

OCR may assist transcription, but OCR output alone is NOT authoritative.

If a word/number remains genuinely unreadable, keep the final document template blocked at that exact location rather than guessing.

---

# 6. DOCUMENT CATEGORY MAPPING

Classify physical sources by actual content and reconcile them against Source Pack Index.

Required final categories:

## COMMERCIAL
- general/specific auction conditions
- Envelope A
- Envelope B
- Envelope C
- price proposal form
- non-interference declaration
- other required forms
- contract source/reference

## CAFE / RESTAURANT
- general/specific conditions
- Envelope A/B/C forms as applicable
- price proposal
- commitments/declarations
- contract source/reference

## SPORTS
- general/specific conditions
- Envelope A/B/C forms as applicable
- price proposal
- commitments/declarations
- contract source/reference

## SHARED
- opening-session minutes
- commission/result forms
- PPT theme
- PPT structure/content reference
- filled PPT regression reference
- official logo/identity

Do not classify uncertain scans based only on CamScanner timestamp.

---

# 7. POWERPOINT AUTHORITY ROLES

Use the three Owner-supplied PPTX files with three distinct roles:

### `تم اصلی 01.pptx`
Role: `PRESENTATION_THEME_MASTER`
- preferred visual basis for newly generated opening-session decks
- organizational look
- editable slide structure

### `نهایی.pptx`
Role: `OPENING_SESSION_CONTENT_STRUCTURE_REFERENCE`
- cover
- general auction information
- process
- publicity/information
- repeated per-space slide structure

### `finall report mozayede 1405.pptx`
Role: `REAL_FILLED_REGRESSION_REFERENCE`
- actual populated examples
- code/name/use/area/region/base price/contract term
- optional investment amount
- location/notes/images
- use for content-density and field-population regression, NOT as current canonical operational data

Do not blindly clone one deck for every role.

---

# 8. TEMPLATE REGISTRY

Complete the versioned `DocumentTemplate` registry.

Minimum metadata:
- `template_key`
- `category`: COMMERCIAL / CAFE / SPORTS / SHARED
- `document_type`
- `version`
- `effective_from`
- `effective_to`
- `authority_source`
- `source_sha256`
- `typed_template_sha256`
- `fixed_text_hash`
- `active`
- `editable_fields`
- `placeholder_registry_version`
- `notes`

Historical generated documents must retain exact template version/hash used.

Changing today’s template must never mutate old finalized documents.

---

# 9. COMPLETE AUCTION LIFECYCLE

Implement the entire operational lifecycle:

`ENTRY -> PERIOD -> LOT -> READINESS -> HUMAN REVIEW -> FREEZE -> DOCUMENT SNAPSHOT -> DOCUMENT PACK -> PARTICIPANTS -> ENVELOPE RECEIPT -> OPENING SESSION -> PROPOSALS -> COMMISSION DECISION -> RESULT/WINNER -> FINAL MINUTES -> NOTIFICATION/FOLLOW-UP -> CONTRACT HANDOFF -> CONTRACT CIRCULATION -> SIGNED OFFICIAL CONTRACT`

Do not stop at candidate readiness.

---

# 10. AUCTION ENTRY — THREE DISTINCT SOURCES

Owner-approved top-level entry paths are:

1. `AUTOMATIC`
2. `MANAGER_ORDER`
3. `COMMISSION_ORDER`

Preserve them distinctly.

Each entry must retain:
- entry source
- rule result
- rule version
- reason codes
- human-readable reason
- authority/reference
- manual reason
- entered_by
- entered_at
- override indicator
- immutable evaluation snapshot

Manual inclusion must NOT erase an automatic `NOT_CANDIDATE` or `REVIEW_REQUIRED` result.

UI must be able to show:
`ورود دستی با وجود نتیجه غیرکاندیدا`
plus reason/reference.

---

# 11. AUTOMATIC RULE ENGINE

Automatic evaluation must be deterministic and explainable.

Return controlled status:
- `CANDIDATE`
- `NOT_CANDIDATE`
- `REVIEW_REQUIRED`

Return:
- readiness
- rule version
- reason codes
- human-readable Persian explanation
- exact input snapshot
- evaluated_at

The Rule Engine may decide candidacy/readiness/warnings.
It MUST NOT choose the legal winner.

---

# 12. MANUAL ENTRY UX

Authorized user must be able to add one or multiple Commercial Space codes using the corrected shared picker.

Support:
- exact code
- Persian/Latin digits
- multi-select
- name/center/region search
- all 501 canonical spaces

Require:
- manual path
- reason
- authority/reference

Fail closed if mandatory evidence is absent.

Prevent duplicate inclusion in same AuctionPeriod.

---

# 13. HISTORICAL VS NEW OPERATIONAL AUCTIONS

Historical imported auctions remain facts only.

Do not invent retrospective:
- participants
- envelopes
- opening events
- signatures
- generated docs
- commission decisions
- contract handoffs

unless source evidence actually exists.

New workflow applies prospectively under Owner-approved operational rules.

---

# 14. AUCTION PERIOD STATE MACHINE

Use explicit controlled states, reconciled with existing models.

Conceptual states:
- DRAFT
- PREPARING
- READY_FOR_APPROVAL
- APPROVED
- DOCUMENTS_READY
- RECEIVING_PROPOSALS
- OPENING_SESSION
- DECISION_PENDING
- RESULT_APPROVED
- CONTRACT_HANDOFF
- CLOSED
- CANCELLED

Store:
- identity/title
- planned dates
- sale/receipt window where relevant
- opening date/time/location
- created/approved/frozen/closed/cancelled metadata
- cancellation reason

Use Jalali-facing dates.

---

# 15. AUCTION LOT STATE MACHINE

Each space/Lot has an independent state.

Conceptual states:
- SELECTED
- NEEDS_REVIEW
- READY
- FROZEN
- DOCUMENTS_READY
- OPEN_FOR_PROPOSALS
- OPENED
- DECISION_PENDING
- AWARDED
- NO_WINNER
- REPEAT_REQUIRED
- CANCELLED
- CONTRACT_HANDOFF
- COMPLETED

Invalid transitions must fail closed.

---

# 16. READINESS CHECKLIST

Before `READY`, evaluate:
- canonical Commercial Space exists
- current business status
- entry authority
- pack type
- appraisal basis
- appraisal validity
- base amount
- contract timing/state where relevant
- transaction threshold classification
- required approval/reference
- required source documents
- dates
- required master data
- missing critical fields

Every failed item must show:
- reason
- source
- required action

Unknown must not silently become false or true.

---

# 17. THREE PACK TYPES

Every AuctionLot must explicitly use one pack:
- COMMERCIAL
- CAFE
- SPORTS

If canonical usage does not safely determine the pack, require human confirmation.

Never silently guess pack type from fuzzy text.

---

# 18. APPRAISAL BASIS BINDING

Auction Lot must bind to a SPECIFIC appraisal record.

Store:
- appraisal id
- amount
- date
- validity state
- rule version
- source/provenance

At Freeze, snapshot these values.

Do not later query “latest appraisal” and silently change base price.

---

# 19. FREEZE

Before official documents:

Authorized user reviews final Lot list and confirms Freeze.

Freeze must create an immutable logical snapshot of:
- AuctionPeriod
- Lot list
- canonical space identity
- center/region/address/use/area
- appraisal basis
- base price
- investment amount if applicable
- automatic rule evaluation
- manual entry evidence
- pack type
- dates
- current approved signatory/committee settings
- template versions

Store:
- snapshot JSON
- snapshot SHA-256
- frozen_by
- frozen_at

After Freeze, source model changes must not rewrite the auction package.

---

# 20. AUCTION DOCUMENT SNAPSHOT — SINGLE SOURCE OF TRUTH

Create/use `AuctionDocumentSnapshot` as the ONLY data source for generated official auction documents.

Generators must not independently query current arbitrary models for values after Freeze.

Field provenance should identify source where practical.

Critical invariant:

`UI session data = Minutes = PPTX = Result report`

for the same frozen session/result snapshot.

---

# 21. PLACEHOLDER REGISTRY

Create a central approved placeholder registry.

Examples:
- organization_name
- management_name
- department_name
- auction_id
- auction_title
- space_code
- space_name
- center_name
- region
- address
- usage
- area
- appraisal_date
- base_price_rial
- base_price_words
- investment_amount_rial
- investment_amount_words
- contract_term
- sale_start/end
- opening_date
- opening_time
- opening_location
- invitation/reference
- guarantee_amount
- participant fields
- bid amount
- commission decision
- winner fields

Unknown placeholder => generation failure.

No arbitrary ad-hoc template variables.

---

# 22. MONEY RULES

All amounts:
- numeric in DB
- thousands separators in UI/output
- explicit currency
- important values also Persian words

Never confuse Rial and Toman.

Template declares expected currency.

Investment amount is optional where source/template permits it; absence must not be converted to zero.

---

# 23. PREFLIGHT

Before final document generation show a preflight with:
- complete
- warning/review
- blocking missing

Distinguish:
- SYSTEM-MISSING DATA
- INTENTIONALLY BLANK PRINT FIELD

Missing mandatory field blocks final generation.

Do not fabricate values merely to make a file generate.

---

# 24. TWO-STAGE PREVIEW

Before final lock:

## Data preview
Show field, value, source/provenance.

## Visual preview
Render actual output.

Only after human confirmation:
`تأیید و تولید نسخه نهایی`

Finalized output becomes immutable.

Correction creates new version with reason and `supersedes` reference.

---

# 25. GENERATE OFFICIAL PACKS

For each FROZEN/READY Lot generate the correct physical pack from Owner-approved templates.

Expected documents where supported by authority:
- general/specific conditions
- Envelope A cover/forms
- Envelope B cover/forms
- Envelope C / price proposal
- non-interference declaration
- other category-specific required forms

Generate PDF and editable DOCX where business process requires an editable document.

Preserve official wording and layout.

---

# 26. ENVELOPES A/B/C

Model envelopes explicitly per participant/proposal.

Store:
- A received
- B received
- C received
- received_at
- delivered_by
- received_by
- receipt/reference
- completeness
- issues
- notes
- supporting documents

Do not reduce envelope state to one free-text field.

Opening is auditable and non-reversible without a correction event.

---

# 27. PARTICIPANTS

Support natural/legal persons according to templates.

Possible fields where required:
- type
- name
- national/registration identity
- representative
- contact
- address
- postal code
- bank/IBAN
- tax/economic information
- documents
- status

Do not force a field not required by the actual authoritative pack.

---

# 28. PARTICIPANT DOCUMENT CHECKLIST

Build checklist from actual category template, not generic assumptions.

Potential evidence includes:
- guarantee/deposit
- signed auction papers/sample contract
- corporate registration/official gazette
- relevant résumé/work history
- VAT/tax certificate
- identity documents
- non-interference declaration
- other category-specific requirements

Commercial/Cafe/Sports may differ.

---

# 29. PROPOSALS

Proposal must belong to:
`AuctionLot + Participant`

Store:
- offered amount
- received_at
- envelope statuses
- proposal document
- validation state
- rejection reason
- commission notes

No orphan proposal records.

---

# 30. OPENING SESSION ENTITY

Create/complete `AuctionOpeningSession`.

Store:
- AuctionPeriod
- date/time/location
- identity/reference
- attendees
- committee members
- secretary
- state
- notes
- opened_at/closed_at
- created_by
- approved_by

Use versioned Master Data for committee/signatories.

Historical session retains attendee snapshot.

---

# 31. OPENING SESSION WORKSPACE

One practical meeting-day workspace must allow rapid use.

Show:
- period
- current Lot
- space identity
- base appraisal/price
- participants
- Envelope A/B/C state
- proposal amounts
- missing docs/issues
- commission notes
- result status
- next allowed action

Fast Lot switching.

Do not require many unrelated browser pages during the meeting.

---

# 32. OPENING MINUTES

Use the Owner-supplied DOCX as strong structural/content reference.

Generate opening minutes from the SAME session snapshot.

Include authoritative fields such as:
- authorization/reference
- term
- base price
- investment amount where applicable
- guarantee/deposit
- publication date
- invitation number
- session date/location
- attendees
- Envelope A review
- Envelope B checklist/results
- Envelope C proposal amounts
- final result wording/placeholders
- signatures

Do not invent legal prose.

---

# 33. POWERPOINT GENERATION

Generate the opening-session PPTX offline.

Use:
- Theme Master: `تم اصلی 01.pptx`
- Content structure: `نهایی.pptx`
- Filled regression: `finall report mozayede 1405.pptx`

Generated deck must remain editable where practical.

No rasterized screenshot-only deck.

Use real text boxes/tables.

No Internet or cloud dependency.

---

# 34. POWERPOINT CONTENT

At minimum:

1. Cover
2. General auction information
3. Auction process / key dates and counts
4. Publicity/information section where relevant
5. Repeated slide(s) per Lot with:
   - space code
   - space/center name
   - use
   - area
   - region
   - base price
   - contract term
   - investment amount if applicable
   - location
   - notes
   - image where available
6. Participant/envelope/bid review slide(s) where appropriate
7. Result/decision slide after decision

Do not overload slides.

---

# 35. POWERPOINT DATA CONSISTENCY

Automated invariant:

For every Lot/session:
- code matches DB/snapshot
- base price matches minutes
- proposal amounts match minutes
- session date/time/location match
- winner/result matches approved decision

PPT and minutes must never build their values through separate query logic.

---

# 36. PPT IMAGE POLICY

Use authoritative/available space images.

If no approved image exists:
- show a clean placeholder
- do not fetch arbitrary web images
- do not fabricate imagery

Historical example images in filled PPT are references, not canonical replacements for current data.

---

# 37. HUMAN WINNER DECISION

SAMA MUST NOT automatically select the legal winner.

Authorized human/commission records result.

Controlled outcomes:
- WINNER
- NO_WINNER
- REPEAT
- CANCELLED
- DISQUALIFIED
- additional states only if authority requires them

For winner store:
- participant
- selected proposal
- winning amount
- decision reference
- decision date
- reason/notes
- approved_by

Validate winner and proposal belong to same Lot.

Amount mismatch requires explicit permitted override with reason; never silent.

---

# 38. RESULT DOCUMENT

Generate final result/minutes from approved snapshot.

Freeze:
- document hash
- template version
- snapshot hash
- generated_at/by
- approved_at/by

Never overwrite a final file.

Correction = new version.

---

# 39. POST-AWARD FOLLOW-UP

Track:
- notification date/reference
- winner obligations
- deadline
- guarantee/document completion
- contract preparation readiness
- default/failure reason
- next action

Alerts only when actionable.

---

# 40. CONTRACT HANDOFF

A successful approved Award must provide:
`ایجاد پرونده قرارداد از نتیجه مزایده`

Prepopulate:
- Commercial Space
- winner/beneficiary
- auction identity
- result reference
- winning amount
- commission decision
- appraisal reference
- generated document references

Do not retype known data.

---

# 41. CONTRACT HANDOFF IS NOT AN OFFICIAL CONTRACT

Preserve accepted rule:

`Auction Award -> Contract Case -> Contract Circulation -> Required Signatures/Approvals -> Official Contract`

Circulation != official Contract.

No official contract before mandatory signatures + final approval.

Use existing Contract workflow; do not create a second parallel contract engine.

---

# 42. IDEMPOTENCY / DUPLICATE PROTECTION

One Award must not accidentally create multiple contract cases.

Use explicit relationship and safe retry/idempotency.

Also prevent:
- duplicate Lot in same period
- incompatible duplicate open-period inclusion
- envelope opened twice
- Lot finalized twice
- result approved twice

Use DB constraints/short transactions compatible with SQLite.

---

# 43. AUCTION DOSSIER IN COMMERCIAL SPACE

The `مزایده و کمیسیون` dossier section must show read-focused history:
- historical auction facts
- new AuctionPeriod/Lot
- entry source
- Rule evaluation
- manual authority
- readiness
- Freeze
- generated documents
- participants/envelopes
- opening session
- decision
- winner
- contract handoff

Editing stays in specialist Auction workspace.

---

# 44. AUCTION SPECIALIST WORKSPACE

Complete the current limited auction area into a practical workflow.

Suggested horizontal tabs/stages:
- کاندیدهای خودکار
- ورود دستی
- دوره‌های مزایده
- آماده‌سازی و کنترل
- اسناد مزایده
- دریافت پاکت‌ها
- جلسه بازگشایی
- نتایج
- در انتظار قرارداد
- بایگانی

No permanent vertical sidebar.

Show current state + next permitted action clearly.

---

# 45. REPORTING

Use UAT.15 `ReportDataset` infrastructure.

Auction report fields include:
- period
- Lot
- space code
- region
- center
- pack type
- entry source
- automatic/manual
- readiness
- state
- participant
- proposal
- winner
- amount
- session date
- result
- contract handoff state

Search/filter/sort/export.

Screen = PDF = XLSX = DOCX dataset for same filters.

---

# 46. KPI

Only useful actionable KPIs:
- automatic candidates
- manual entries
- needs review
- ready
- documents incomplete
- awaiting envelopes
- opening pending
- decision pending
- awarded
- awaiting contract
- closed/cancelled

Every KPI drillable.
Count == underlying list count.

---

# 47. OFFICIAL DOCUMENT BRANDING

Official Auction outputs must contain only approved organizational identity:

`سازمان فرهنگی هنری شهرداری تهران`
`مدیریت اقتصادی و املاک`
`اداره املاک و مستغلات`

plus approved official logo.

Never include:
- سما
- SMK
- localhost/URL
- account name
- navigation
- debug data

---

# 48. OFFICIAL DOCUMENT STORAGE

Store generated official document bytes under server media/document storage, not DB.

Metadata:
- entity
- document type
- category
- template version
- filename
- MIME
- SHA-256
- snapshot hash
- generated_by/at
- approved_by/at
- version
- supersedes

---

# 49. FILE NAMING

Use deterministic Persian-friendly names, e.g.:

`مزایده_1405_دوره_03_کدفضا_347_پاکت_الف.pdf`

Avoid ambiguous names like `document1.pdf`.

Sanitize filesystem-invalid characters.

---

# 50. BATCH GENERATION

For multi-Lot AuctionPeriod support:
- generate one Lot pack
- generate all ready packs

Per-Lot result:
- success
- blocked
- missing data
- template error

Do not fail entire batch silently.

Optionally produce period ZIP + manifest when practical.

---

# 51. BATCH MANIFEST

Batch manifest should include:
- period
- Lots
- document filenames
- template versions
- source template hashes
- output hashes
- snapshot hashes
- generation timestamp

No secrets.

---

# 52. AUDIT

Audit at minimum:
- automatic evaluation
- manual entry
- Lot add/remove/archive
- pack classification
- readiness decisions
- Freeze
- snapshot creation
- document generation
- participant changes
- envelope receipt/opening
- proposal changes
- session opening/closing
- decision/result
- winner selection
- overrides
- contract handoff

Store actor/time/before/after/reason as applicable.

No normal hard delete of real operational data.

---

# 53. MASTER DATA

Use versioned Master Data for:
- organization identity
- officials/signatories
- committee members
- effective dates
- thresholds
- template versions
- other approved shared settings

Historical documents must retain names/settings effective at generation time.

Changing today’s official must not rewrite old documents.

---

# 54. TIMELINE

Add meaningful auction milestones to Commercial Space Timeline:
- candidate evaluation
- manual inclusion
- period inclusion
- Freeze
- document generation
- opening session
- result
- award
- contract handoff

Avoid noisy low-value events.

---

# 55. ALERTS

Only actionable alerts, e.g.:
- missing required document
- proposal deadline approaching
- opening session upcoming
- decision pending
- winner action deadline
- contract handoff overdue

Every alert needs subject/reason/date/status/action link.

---

# 56. DATA QUALITY / FAIL-CLOSED

Never silently choose:
- pack category
- appraisal
- base amount
- investment amount
- session attendees
- winner
- proposal
- authority reference
- missing identity
- missing legal wording

Ambiguous critical value => REVIEW_REQUIRED/BLOCKED.

---

# 57. PERFORMANCE

Avoid N+1 on:
- periods
- Lots
- participants
- proposals
- documents
- dossier history

Use select_related/prefetch_related.

Keep SQLite transactions short.

---

# 58. MIGRATIONS

Schema changes must be:
- minimal
- additive preferred
- no loss of historical records
- tested from a copy of UAT.15 DB

Run upgrade migration test.

Authority canonical counts MUST remain unchanged:
- 225 Mother Properties
- 501 Commercial Spaces
- 350 Active
- 151 Out-of-Cycle

Do not mutate Authority Excels.

---

# 59. AUTOMATED TESTS — AUTHORITY INGEST

Test:
- package SHA
- all 10 file hashes
- manifest completeness
- category registry
- PPT role mapping
- template version uniqueness
- unknown placeholder failure
- fixed-text hash protection

---

# 60. AUTOMATED TESTS — RULE / ENTRY

Test:
- automatic CANDIDATE
- NOT_CANDIDATE
- REVIEW_REQUIRED
- manager order
- commission order
- manual reason/reference required
- manual entry preserves automatic result
- duplicate prevention
- rule snapshot/version

---

# 61. AUTOMATED TESTS — FREEZE / SNAPSHOT

Test:
- readiness blocks missing required input
- Freeze succeeds only after review
- Snapshot hash stable
- post-Freeze source changes do not change frozen values
- correction/version flow works

---

# 62. AUTOMATED TESTS — THREE PACKS

Create test Lots:
- COMMERCIAL
- CAFE
- SPORTS

Verify correct template selection and category-specific requirements.

Ensure no cross-pack document leakage.

---

# 63. AUTOMATED TESTS — DOCUMENTS

Verify generated documents:
- known values inserted correctly
- fixed legal text unchanged
- unknown placeholders fail
- official branding only
- no SAMA
- no SMK
- no URL
- correct template version/hash recorded

---

# 64. AUTOMATED TESTS — SESSION CONSISTENCY

Create participants/proposals/envelopes/session.

Verify same values in:
- DB/session dataset
- opening minutes
- PPTX
- result report

Especially:
- code
- base price
- bid amount
- date/time/location
- winner/result

---

# 65. AUTOMATED TESTS — WINNER

Reject:
- winner not a participant
- proposal from another Lot
- mismatch without approved override

Accept valid human-approved winner.

Ensure SAMA never auto-selects winner.

---

# 66. AUTOMATED TESTS — CONTRACT HANDOFF

Test:
`Award -> ContractCase -> ContractCirculation`

Verify prefill.
Verify idempotency.
Verify no official Contract before required signatures/final approval.

---

# 67. PPTX QA

Programmatically inspect generated PPTX:
- opens successfully
- expected slide count
- real editable text
- Persian text present
- codes correct
- amounts correct
- session data correct
- no external links
- no Internet dependency

Render if environment supports and visually inspect.

Compare key slides to Theme/Structure/Filled references.

---

# 68. PDF/DOCX QA

Generate and visually inspect:
- commercial pack
- cafe pack
- sports pack
- opening minutes
- final result

Check:
- true RTL
- Persian shaping
- exact values
- legal text preservation
- borders
- page breaks
- signature areas
- logo
- no clipping

---

# 69. REAL BROWSER QA — FULL JOURNEY

At 1366×768, 1600×900, 1920×1080 test:

1. create AuctionPeriod
2. automatic candidate entry
3. MANAGER_ORDER entry
4. COMMISSION_ORDER entry
5. choose/confirm pack type
6. resolve readiness
7. preflight
8. Freeze
9. data preview
10. visual preview
11. generate packs
12. add participants
13. receive A/B/C
14. open session
15. open envelopes
16. record proposal(s)
17. generate minutes
18. generate PPTX
19. record human commission decision
20. generate result
21. create Contract handoff
22. open Contract Circulation

Every visible action must work.

No fake buttons/placeholders masquerading as features.

---

# 70. OWNER ACCEPTANCE DEMO DATA

Prepare one clearly marked UAT operational AuctionPeriod with at least:
- one Commercial Lot
- one Cafe Lot
- one Sports Lot

Demonstrate complete flow.

Do not modify Authority facts.

Mark UAT operational data so it can be cleaned safely without touching canonical imports.

---

# 71. GOLDEN MASTER VISUAL COMPARISON

For every generated document/template derived from scanned source:
- compare page count where fixed
- compare legal text
- compare required fields
- compare header/logo
- compare tables/forms
- compare signature areas
- compare blank handwritten areas
- compare RTL/order

Record visual QA evidence.

Do not call PASS just because a file opens.

---

# 72. RELEASE GATES

Run at minimum:

- `pytest -q`
- focused auction tests
- browser tests
- `python manage.py makemigrations --check --dry-run`
- `python manage.py migrate --noinput`
- `python manage.py check --deploy`
- authority verify/inspect
- DB integrity/FK check
- upgrade-from-UAT15 migration test
- PDF QA
- DOCX QA
- PPTX QA
- Windows runtime smoke
- release asset independent download/hash verification

Expected local HTTP/SSL deploy warnings may remain documented for UAT, but no unexplained errors.

---

# 73. RELEASE

Only after all gates pass create NEW prerelease:

`v5.0.0-uat.16`

Do not overwrite UAT.15.
Do not merge PR #2.
Do not claim Production/LAN Ready.
Do not create Golden Master yet.

Status remains:
`UAT REMEDIATION IN PROGRESS`
until explicit Owner Human UAT acceptance.

---

# 74. FINAL REPORT FORMAT

Return exactly a concise evidence report covering:

## Authority ingest
- package hash
- all source files + hashes
- classification
- missing/unresolved items
- transcription/diff status

## UAT.16 foundation
- preserved/reused pieces
- new migrations/models/services

## Entry
- automatic
- manager order
- commission order

## Rule Engine
- result semantics
- explainability
- snapshots

## Period / Lot
- state machines
- readiness
- Freeze

## Documents
- Commercial
- Cafe
- Sports
- template versions
- fixed-text verification
- preview/final lock

## Participants / Envelopes
- implementation status

## Opening Session
- workflow
- minutes

## PowerPoint
- theme master
- structure reference
- regression reference
- generator
- editability
- consistency checks

## Result
- human winner
- result docs

## Contract handoff
- prefill
- circulation
- idempotency

## Reporting / KPI
- filter/search/export
- drilldown consistency

## QA
- pytest total
- focused tests
- browser evidence
- PDF/DOCX/PPTX visual QA
- migration/upgrade evidence

## Windows
- tag
- runtime commit
- ZIP
- size
- SHA-256
- workflow URL

## PR #2
`OPEN / UNMERGED`

## Status
`UAT REMEDIATION IN PROGRESS — pending Owner Human UAT`

---

# FINAL NON-NEGOTIABLE PRINCIPLE

One approved value must have one authoritative frozen meaning.

For the same Auction Session/Lot:

`Database / UI / Minutes / PowerPoint / Result / Contract Handoff`

must all derive from the same approved snapshot.

Never maintain six independent copies of the truth.
