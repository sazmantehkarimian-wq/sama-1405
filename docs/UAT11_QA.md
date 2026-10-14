# UAT.11 consolidated QA

The canonical default Commercial Space order is management group, numeric geographic region, center name and numeric space code. Ordinary regions precede special centers; special-center records retain geographic region independently, unknown regions sort last, and the single canonical queryset prevents duplicate display. Explicit user sorts replace this default.

Authority reconciliation reproduced 225 unique Mother Properties, 501 unique Commercial Spaces, 350 active and 151 out-of-cycle records. The default queryset returned 501 distinct primary keys.

A real 21-row active Region 1 subset was exported with explicit `region, code` multi-sort to XLSX, PDF and DOCX. All formats preserve the same row sequence and this visual right-to-left column order: کد فضا، نام فضا / مرکز، منطقه، وضعیت، کاربری، مساحت، توضیحات کارشناس، امضاء. XLSX structural properties and DOCX OOXML bidi/header properties passed; the rendered PDF first page was visually inspected and contains only approved organizational identity.
