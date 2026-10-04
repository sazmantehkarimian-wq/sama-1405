# Contract circulation reconciliation

The repository authority `authority/reference/MD قراردادها — FINAL FROZEN.md` and the Owner's integrated post-UAT.8 directive govern this implementation. The named standalone package was not copied as a runtime or datastore.

- Imported `Contract` rows remain historical facts.
- `ContractCirculation` is a separate operational aggregate beginning no earlier than 1405/07/01.
- No signature roles or SLA thresholds are invented; signature steps are supplied from approved configuration/work instructions.
- Current custody is derived from the sole open transfer event. Return closes that event and repeated round trips append new records.
- Required signatures and a separate final approval are gates for conversion to a linked, non-historical official contract.
