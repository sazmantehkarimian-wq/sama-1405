# UAT.10 Mother Property authority trace

Authority verification on the 6 Mehr package yields 225 unique Mother Property identifiers, 501 unique Commercial Spaces, 350 active and 151 out-of-cycle spaces, with no duplicate canonical identifiers.

Trace contract:

1. `املاک_مادر_به‌روزشده_6مهر.xlsx` / `املاک مادر` supplies the identifier and authoritative property attributes.
2. Every source cell remains in `RawCell`; canonical `MotherProperty.source_row` retains its source-row reference.
3. `فضاهای مرتبط` supplies explicit Mother Property ↔ Commercial Space links. The importer creates `MotherPropertySpaceLink` with source file, sheet, row, evidence and confirmation. Missing endpoints become discrepancies; numeric similarity is never used.
4. The list, dossier, cross-links and exports query these canonical records and evidence links directly.

Representative automated tests use distinct `P-0001` and `MP-000001` values to prove that numeric similarity does not merge identifiers, and follow an explicit evidence link through list, dossier and Commercial Space return link.
