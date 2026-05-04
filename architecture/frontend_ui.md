# Frontend UI SOP

## Framework
Vanilla HTML/CSS/JS (No complex build step required, to keep it simple and local).
Can use a library like FullCalendar (via CDN) for robust calendar rendering.

## Goal
Visualize the JSON event payload intuitively.

## Features
- Month/Week/List/Year views.
- Year view is a 12-month overview made of clickable mini-month cards; clicking a month card jumps to that month in the monthly view.
- Color coding by event type (e.g., Red for Market Closures, Orange for Public Holidays, Blue for Stock Events, Green for Macro).
- Clickable event-type filter toggles above the calendar:
  - `Market Closures`
  - `Public Holidays`
  - `Stock Events`
  - `Macro Events`
- Clicking an event shows the `description` and `related_tickers`.
- Frontend navigation should query only the local API and must not wait on direct upstream data fetches.
