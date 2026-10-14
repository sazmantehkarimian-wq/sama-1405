# UAT.13 Visual Specification — clean rebuild from UAT.11

Status: implementation specification; UAT remediation remains in progress.

## Shell and identity

A single horizontal desktop shell is retained. The right brand unit contains the untouched organizational logo and a centered three-line Vazirmatn identity: `سما` (ExtraBold), management (SemiBold), administration (Regular). Navigation stays geometrically centered; account actions remain at left. No vertical navigation or region rail is permitted.

## Shared page composition

Every screen follows: shell → page header with title/context and one compact toolbar → optional context/filter bar → primary content → secondary content → subtle UI footer. Print/export controls are grouped in the toolbar. Content width, gutters, section rhythm, and surfaces are token-controlled.

## Palette and domain identity

Only the approved neutral, plum, green, terracotta, amber, teal and slate families in `tokens.css` are allowed. Each family exposes soft, border, accent, hover, selected and strong tones. A page gets one semantic domain accent, used only for title markers, selected tabs, focus, primary action, and a restrained card edge—not whole-page tinting.

## Components

- Controls: XS 28px, SM 32px, primary MD 36px; content-sized, visible focus, no unjustified full width.
- Cards: compact padding, clear heading/body split, border-led hierarchy; no decorative card wall.
- KPIs: asymmetric management grid, full-card link, number/title/definition, subtle domain edge. Count and drill-down share one queryset definition.
- Tables: 34px rows, 36px sticky headers, fine borders, aligned numbers, compact row actions, restrained hover.
- Dossiers: typographic identity band, inline metadata, five quick facts, compact tabs, then read-only domain sections.
- Filters/forms: short primary row, collapsed advanced controls, shared searchable pickers.
- Empty states: one concise line and optional small action; distinguish missing authority, missing operation, missing relation and filtered zero.
- Regions landing: centered 22-tile grid plus equal-language Special Centers entry and overall summary. Never a side rail.
- Region/center workspace: breadcrumb context, compact toolbar, drillable KPI grid and horizontal domain tabs. Switching is top-level, never a tall rail.
- Report builder: two-column workbench grouping dataset/filter controls and adjacent column-order controls; preview/save/export remain explicit.

## Print

Dedicated print CSS removes shell, footer credit, controls, selectors and pagination. It inserts official organizational identity, retains page title/context/filter summary and tables, repeats table headers, avoids splitting rows/cards, and uses sensible A4 margins. Official generated files continue to exclude software identity and SMK credit.

## Review gates

At 1366×768, 1600×900 and 1920×1080 review balance, density, RTL, hierarchy, header collision, toolbar cohesion, tables, empty states and absence of a region rail. Reject tall side navigation, narrow center columns, unexplained/non-clickable KPIs, giant buttons, floating print controls, large unused areas, arbitrary colors, or raw page print.

## Approved palette inventory

The implementation maps directly to the Authority anchors: dashboard `#9B3B4A/#FDF6F7`, Mother Properties `#3E7FC4/#F5FAFF`, active spaces `#2E5D31/#F6F9F4`, contracts `#C89400/#FFFAEC`, appraisals `#67406A/#F7F4F8`, auctions `#F0731F/#FFF8F1`, utilities `#1F8A77/#E2F3EE`, commission/workflow `#3E5A68/#F4F7F9`, reports `#5A6F9B/#F5F6FA`, and administration `#6F7783/#F7F7F7`. Derived border/hover/selected tones use only anchors from those same approved families.
