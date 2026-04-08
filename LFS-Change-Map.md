# Looking For Spots — Complete Change Map

**Date:** April 8, 2026 | **Status:** Audit complete, no changes implemented yet

This document maps every change to implement before launch, informed by the design review, accessibility audit, r/flyfishing community research, content voice guidelines, and spot-burning sensitivity analysis.

---

## A. Community-Sensitive Changes (Reddit-Readiness)

These changes address the r/flyfishing community's culture: anti-self-promotion, spot-burning paranoia, and distrust of commercial fishing apps.

### A1. Reframe the App Identity

**Current:** Title says "California Fly Fishing Conditions" — OG description says "Real-time fly fishing conditions for 62 Northern California spots."

**Problem:** "62 spots" sounds like a spot-revealing app. Anglers on r/flyfishing roast anyone who publicizes lesser-known water.

**Change:** Update OG/Twitter meta descriptions to emphasize *public gauge data* rather than *spot discovery*:
- OG description → "Real-time USGS & CDEC gauge conditions for Northern California rivers. Traffic-light system for flow status."
- Twitter description → "Public gauge data + fly shop reports for NorCal rivers. Green, yellow, or red — know before you go."
- Remove the "62 spots" count from all external-facing copy. Internally it's fine, but in share text and meta tags it triggers spot-counting anxiety.

**Files:** `norcal-flows.html` lines 9-19

### A2. Soften the Share Text

**Current:** `shareSpot()` generates: `"McCloud River is GREEN (526 cfs) right now!"`

**Problem:** Sharing a specific river name + status to a group chat is literally what r/flyfishing calls "blowing up a spot." The share feature is fine for close friends, but if this text ends up on social media, it looks like broadcasting.

**Changes:**
- Change share text to: `"NorCal river conditions — check the dashboard"` with the URL. Don't include the specific river name or status in the generated text. The link preview (OG tags) carries the brand, and the recipient can look at the dashboard themselves.
- Alternatively, keep the river name but remove the status: `"Check conditions on the McCloud River"` — this is more like sharing a weather report than spot-burning.
- Update the copied feedback from `"Copied!"` to `"Link copied — send it to your crew"` per UX copy review.

**Files:** `norcal-flows.html` line 1256-1268

### A3. Add Data Attribution Prominently

**Current:** Footer says "Data from USGS · Provisional, not verified · Not for safety decisions · Auto-refreshes every 15 min"

**Problem:** Doesn't credit all sources. If fly shops see their reports being used without clear attribution, they could ask for removal.

**Changes:**
- Update footer: "Data from USGS, CDEC, DreamFlows · Shop reports from Trout Creek Outfitters, Reno Fly Shop, The Fly Shop · Provisional — not for safety decisions"
- Add a small "About" link in footer or header that goes to a brief section explaining: "This app aggregates publicly available gauge data and published fly shop reports. No proprietary data is used."

**Files:** `norcal-flows.html` line 343

### A4. Disclaimer on Shop Reports

**Current:** Reports are displayed with source attribution but no disclaimer about data use.

**Change:** Add a small italic line at the bottom of the reports section in the detail panel: "Reports sourced from publicly available shop updates. Support these shops — they keep our rivers healthy."

**Files:** `norcal-flows.html` in `getReportsHtml()` function, line ~2185-2191

### A5. Add an About Page

**Why:** This is the single most important thing for Reddit survival. Before anyone evaluates the app, they'll ask "who made this and why?" The About page needs to answer that in a way that disarms the spot-burning accusation and signals you're a fellow angler, not a tech company.

**Tone:** First-person, casual, honest. Write it like a post on r/flyfishing, not like a startup landing page.

**Content outline:**
- **The problem:** "I got tired of checking USGS, CDEC, DreamFlows, and three fly shop websites every morning just to figure out if the Lower Sac was fishable. Then doing mental math on whether 6,200 cfs means go or don't go."
- **What this is:** "A traffic light for public gauge data. Green means flows are in the optimal range. Yellow means fishable but not ideal. Red means save the gas. That's it."
- **What this is NOT:** "This isn't a spot finder. Every river on here is well-known public water with published USGS gauges. If you already fish NorCal, you already know these rivers. I'm not exposing anything — I'm just translating the numbers."
- **Data sources:** "All data comes from USGS, CDEC, DreamFlows, and published fly shop reports. Nothing proprietary. The same data you'd find if you checked 6 tabs every morning."
- **Support the shops:** "The fly shops whose reports appear here are the backbone of these fisheries. Buy your flies from them, book a guide trip, say thanks when you stop in. Links: [Trout Creek Outfitters] [Reno Fly Shop] [The Fly Shop]"
- **Contact:** Simple email link for feedback, partnership inquiries, or "if I got a threshold wrong."

**Implementation:** Add as a separate route `/about` served from an `about.html` file, or as a modal/slide-out panel triggered from a header link. Separate page is better for SEO and for linking from Reddit.

**Files:** New file `about.html` + update `start.py` to route `/about` + add "About" link to header in `norcal-flows.html`

### A6. Summarize Shop Reports in Our Own Voice

**Why (redundancy):** If any fly shop asks us to stop scraping, we need a content fallback. Summarized reports in our own words are not derivative works — they're interpretations of publicly available information, the same way a guide would relay a shop report to a client.

**Why (credibility):** Raw report snippets are long and read like marketing copy. A terse 15-25 word summary in the guide-text voice signals that we actually understand what the data means, which is exactly what r/flyfishing respects.

**How it works:**
1. Keep scraping shop reports as raw data (backend unchanged)
2. Add a summarizer layer that takes the raw snippet and outputs a condensed take
3. Display the summary with attribution: "Per The Fly Shop (Apr 7)" — the insight is attributed, the words are ours
4. Link to the original report so users can read the full version
5. This also solves any copyright concern — we're not reproducing their content

**Voice examples:**
- Raw: "The McCloud River is fishing very well right now. Flows are stable and the water clarity is excellent. We've been seeing good PMD hatches in the afternoon with fish rising in the slower pools..."
- Summarized: "McCloud fishing well at 520 cfs. PMDs afternoon, rising fish in slow water. Clarity excellent."

**Implementation phases:**
- **Phase 1 (now):** Manually write summaries for the 8 key rivers based on current shop reports. Store as static content that we update weekly alongside the Green Light Report email.
- **Phase 2 (with users):** Semi-automated — use the scraped data as input, generate draft summaries, human-review before publishing.
- **Phase 3 (with partnerships):** Reach out to shops with traffic data showing we're sending them clicks. Propose formal data-sharing: they give us a summary blurb, we give them attribution + link + "Book a guide" CTA.

**Files:**
- `start.py` — add summary field to report data model
- `norcal-flows.html` — update `getReportsHtml()` to show summary instead of raw snippet, with "Read full report →" link
- New weekly workflow: write 8 river summaries for the Green Light Report

---

## B. Accessibility Fixes (WCAG 2.1 AA)

### B1. CRITICAL — Color-Only Status Indicators

**Current:** Sidebar cards use only green/yellow/red dots and left-border colors to communicate status. Status badges ("green", "yellow", "red") show only lowercase color names.

**Change:**
- Add text labels to status badges: "Go Fish" (green), "Caution" (yellow), "Not Today" (red) — these already exist in the detail panel but not on sidebar cards.
- Add `aria-label` to `.status-dot` spans: `aria-label="Status: green - fishable"`
- Consider adding a subtle pattern or icon inside the status dot for colorblind users: checkmark (green), dash (yellow), X (red).

**Files:** `norcal-flows.html` — `renderSidebar()` function, line ~1674 (badge rendering) and `.status-dot` CSS

### B2. CRITICAL — Keyboard-Accessible River Cards

**Current:** River cards already have `tabindex="0"` and `role="button"` (line 1690). Good — this was partially addressed.

**Remaining change:** Add `onkeydown` handler so Enter/Space triggers `selectRiver()`:
```javascript
onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();selectRiver('${id}')}"
```

**Files:** `norcal-flows.html` line 1690

### B3. Fix 4 Failing Contrast Ratios

| Element | Current | Fix | CSS location |
|---------|---------|-----|-------------|
| Detail disclaimer / footer text | `#94a3b8` on white (2.7:1) | Change to `#64748b` (4.6:1) | Lines 165, 226 |
| Yellow status text | `#a16207` on `#fefce8` (3.8:1) | Change to `#92400e` (5.2:1) | Line 93 |
| Email placeholder | `#64748b` on `#1e293b` (3.1:1) | Lighten to `#a1a1aa` (4.5:1) | Line 180 |
| Card distance text | `#94a3b8` on white (2.7:1) | Change to `#64748b` | Line 95 |

**Files:** `norcal-flows.html` CSS section

### B4. Focus Trap for Reports Modal

**Current:** Tab key escapes the modal into background content.

**Change:** Add focus trap logic when `reports-modal` is visible:
- On open: store last focused element, focus the first focusable element in modal.
- On Tab at last element: loop to first element.
- On Shift+Tab at first element: loop to last.
- On close: return focus to the trigger button.
- On Escape key: close modal.

**Files:** `norcal-flows.html` — `openReportsModal()` and `closeReportsModal()` functions

### B5. Semantic List Structure for River Cards

**Current:** River cards are `<div>` elements inside a `<div class="river-list">`.

**Change:** Wrap river list in `<ul>`, each card in `<li>`. Maintain existing visual styles with `list-style: none`.

**Files:** `norcal-flows.html` line 320 and `renderSidebar()` function

### B6. Email Form Label

**Current:** Email input uses only placeholder text, no `<label>`.

**Change:** Add visually hidden label: `<label for="signup-email" class="sr-only">Email address</label>` and add `id="signup-email"` to the input. Add `.sr-only` CSS class for screen-reader-only visibility.

**Files:** `norcal-flows.html` — `renderDetailPanel()` email signup section, line ~2021-2025

### B7. Announce Filter/Sort Changes

**Current:** Sort and filter controls trigger `renderSidebar()` but don't announce the update to screen readers.

**Change:** After `renderSidebar()` completes, update the `#river-count` element (which already has `aria-live="polite"`) with the new count. Currently this only updates on data fetch — make it update on every render.

**Files:** `norcal-flows.html` — end of `renderSidebar()` function

### B8. Map Marker Shapes

**Current:** All map markers are `CircleMarker` — differentiated only by fill color.

**Change:** Use different Leaflet marker shapes per status: circle (green), triangle/diamond (yellow), square (red). This can be done with `L.divIcon` and simple SVG shapes, or with different `CircleMarker` radii + stroke patterns as a simpler approach.

**Files:** `norcal-flows.html` — `updateMarkers()` function, line ~1576

---

## C. Design System Cleanup

### C1. CSS Custom Properties (Design Tokens)

**Current:** 28 unique hex colors, 12 spacing values, 11 font sizes, 6 border-radius values — all hardcoded inline.

**Change:** Add `:root` variables at the top of the `<style>` block using the token system from the design review:
```css
:root {
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-success: #22c55e;
  --color-warning: #eab308;
  --color-danger: #ef4444;
  --color-text: #1e293b;
  --color-text-secondary: #64748b;
  --color-text-muted: #94a3b8; /* will become #64748b after contrast fix */
  --color-bg: #f8fafc;
  --color-bg-card: #ffffff;
  --color-border: #e2e8f0;
  --text-xs: 11px;
  --text-sm: 12px;
  --text-base: 13px;
  --text-lg: 16px;
  --text-xl: 20px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.15);
}
```
Then find-and-replace all hardcoded values throughout the CSS. This is the single biggest maintainability win.

**Files:** `norcal-flows.html` lines 33-282

### C2. Unify Border Radius

**Current:** Mixed values: 6px (buttons), 8px (inner cards), 10px (sections), 12px (river cards), 16px (modal, mobile detail).

**Change:** Standardize to 3 tokens: `--radius-sm: 6px`, `--radius-md: 10px`, `--radius-lg: 16px`. Map:
- Buttons → `--radius-sm`
- Inner cards, stat boxes, weather items → `--radius-md`
- River cards, sections, modals → `--radius-lg`

### C3. Reduce Type Scale

**Current:** 11 distinct font sizes (10px–20px).

**Change:** Reduce to 5-step scale: 11px, 12px, 13px, 16px, 20px. Eliminate 10px, 14px, 15px, 18px outliers by mapping to nearest step.

### C4. Consolidate Action Colors

**Current:** `#2563eb` (blue-600) for primary actions, `#0ea5e9` (sky-500) for share/subscribe — divergent.

**Change:** Use `#2563eb` for all primary actions OR formally adopt sky-500 as a secondary action color with a dedicated token `--color-secondary: #0ea5e9`. Either way, document the decision. Recommendation: keep sky-500 as secondary since the share/subscribe actions are visually distinct from navigation actions.

---

## D. UX Copy Updates

### D1. Status Labels

| Current | Change to |
|---------|-----------|
| "Fishable With Caveats" (yellow badge, detail panel) | "Fish With Caution" (shorter, fits badge) |
| "Don't Go" (red badge, detail panel) | "Not Today" (softer, still clear) |
| "Go Fish" (green) | Keep as-is |

**Files:** `norcal-flows.html` line 1793

### D2. Status Reasons (Auto-Generated)

| Current | Change to |
|---------|-----------|
| "No flow data available" | "No current readings — check back soon" |
| "Optimal range (526 cfs)" | "Conditions are ideal (526 cfs)" |
| "Below optimal — low flows" | "Flows are low — wadeable but fewer fish holding" |
| "Above optimal — high water" | "Flows are high — fish deep runs and seams" |
| "Too low" / "Too high" | "Too low to fish" / "Too high — stay safe" |
| "Water too warm — do not fish" | "Water too warm (68°F+) — protect the fish, stay home" |

**Files:** `norcal-flows.html` `calculateStatus()` function, lines 1294-1328

### D3. Header Copy

| Element | Current | Change to |
|---------|---------|-----------|
| Refresh button | "Refresh" | "Check Now" |
| Shop Reports button | "Shop Reports" | "Fly Shop Reports" |
| Loading text | "Loading river conditions..." | "Checking 62 rivers..." |
| Refresh loading text | "Loading..." | "Checking..." |

**Files:** `norcal-flows.html` lines 293-295 (HTML), line 1411 (JS loading state)

### D4. Empty States

| State | Current | Add |
|-------|---------|-----|
| No favorites | Nothing shown | "No saved spots yet. Tap the star on any river to add it here." |
| No reports for river | Nothing shown | "No recent shop reports for this river. Check back — shops update weekly." |
| Reports modal empty filter | Nothing | "No reports from this shop recently. Try 'All' to see everything." |

**Files:** `norcal-flows.html` — `renderSidebar()` (favorites empty state), `getReportsHtml()` (no reports), `renderReportsList()` (empty filter)

### D5. Email Signup Copy

| Element | Current | Change to |
|---------|---------|-----------|
| Subscribe button | "Subscribe" | "Get the Report" |
| Error message | "Something went wrong." | "Couldn't subscribe — try again in a moment." |
| Success message | Keep as-is | Keep as-is |

**Files:** `norcal-flows.html` line 2023 (button), `handleSubscribe()` line 1290 (error)

### D6. Share Copy

| Element | Current | Change to |
|---------|---------|-----------|
| Button label | "🔗 Share" | "Share Spot" (remove emoji, use text) |
| Copied feedback | "Copied!" | "Link copied — send it to your crew" |

**Files:** `norcal-flows.html` line 1977 (button), line 1269 (feedback)

---

## E. Missing Assets

### E1. OG Preview Image (`og-preview.png`)

**Status:** Referenced in meta tags (line 13) but doesn't exist. Share links on social media will show no image.

**Action:** Create a 1200x630px image with:
- Dark background (#0f172a)
- "Looking For Spots" title + 🎣 emoji
- Tagline: "NorCal Fly Fishing Conditions"
- 3 colored dots (green/yellow/red) as visual shorthand for the traffic light system
- Clean, minimal — no screenshots of the app

### E2. PWA Icons (`icon-192.png`, `icon-512.png`)

**Status:** Referenced in `manifest.json` and `<link rel="apple-touch-icon">` (line 26) but don't exist. PWA install will fail.

**Action:** Create simple icons:
- 192x192 and 512x512 PNG
- Dark background with a stylized fish hook or casting line
- Keep it simple — single color on dark background

### E3. Favicon

**Status:** No `<link rel="icon">` tag exists. Browser tabs show a generic icon.

**Action:** Add a 32x32 favicon. Can be the same design as the PWA icon, scaled down.

---

## F. Loading & First Impression

### F1. Skeleton Loading State

**Current:** Shows "Loading river conditions..." text on a white overlay.

**Change:** Replace with a branded skeleton screen:
- Pulse-animate 3-4 placeholder river cards (gray boxes with the traffic-light border colors pulsing)
- Change text to "Checking 62 rivers..."
- Show the sidebar structure immediately so users understand the layout before data loads

**Files:** `norcal-flows.html` CSS for `.loading-overlay` / `.loading-spinner` + JS in `fetchAllData()`

### F2. Best Bet Banner Enhancement

**Current:** Blends into the card list. Easy to miss.

**Change:** Increase contrast: slightly larger font for the river name, add a subtle green glow or border animation on initial load, use bolder gradient background.

**Files:** `norcal-flows.html` CSS `.best-bet-banner` lines 64-69

---

## G. Mobile-Specific Fixes

### G1. Replace Emoji Nav Icons with SVGs

**Current:** Mobile bottom nav uses 📋🗺️⭐ which render differently on every OS.

**Change:** Replace with inline SVG icons from Lucide or Heroicons CDN. Add visible small text labels below each icon ("List", "Map", "Spots").

**Files:** `norcal-flows.html` lines 338-341 (nav HTML), line 244-247 (nav CSS)

### G2. Header Emoji Icons

**Current:** "📍 Near Me" and "🎣" in the title use emoji.

**Change:** Replace 📍 with an inline SVG location pin. Keep 🎣 in the title — it's brand identity and renders consistently enough at that size. But test on Windows/Android to confirm.

**Files:** `norcal-flows.html` line 288 (title), line 294 (Near Me button)

---

## H. Backend Hardening

### H1. Error-Specific Subscribe Messages

**Current:** Generic "Something went wrong" error from subscribe endpoint.

**Change:** Return specific errors: "Invalid email format", "Already subscribed", "Server error — try again later". The frontend already handles these; the backend just needs to return the right message for each case. (Partially done — "Already subscribed" returns 409 with message, but "Invalid email" doesn't explain why.)

**Files:** `start.py` `_handle_subscribe()` lines 843-900

### H2. Rate Limit Subscribe Endpoint

**Current:** No rate limiting on POST /api/subscribe. Could be abused.

**Change:** Add simple in-memory rate limiting: max 5 subscribe attempts per IP per hour. Store a dict of `{ip: [timestamps]}` and check before processing.

**Files:** `start.py` — add rate limit dict and check in `_handle_subscribe()`

### H3. Data Redundancy Documentation

**Current:** If USGS API changes format or DreamFlows blocks scraping, data breaks silently.

**Change:** Add monitoring: if a data source returns zero results for 2 consecutive fetch cycles, log a warning and set a flag that the frontend can check via `/api/status`. The frontend could show a small banner: "Some data sources are delayed — conditions may be stale."

**Files:** `start.py` `background_refresh()` function

---

## I. Content Voice Alignment

### I1. River Notes Tone

**Current:** Notes vary in tone — some are terse ("Optimal 300–800 cfs"), some are verbose ("One of the last unimpaired streams in the Sacramento Valley").

**Change:** Standardize to the terse, guide-text style we defined:
- Lead with the key fact (optimal flow range)
- One sentence on access/character
- No tourism marketing language
- Example: "Optimal 300–800 cfs. Walk-and-wade tailwater below Whiskeytown. Wild trout, some steelhead."

**Files:** `norcal-flows.html` — all `notes` fields in RIVERS config (lines 386-789)

### I2. Hatch Data Format

**Current:** Hatch entries are already terse and good. No changes needed. Just confirm consistency — some entries use `#` for hook sizes, some don't.

**Change:** Audit all 32 rivers × 12 months to ensure hook sizes always use `#` notation and pattern names are consistent.

**Files:** `norcal-flows.html` HATCH_DATA object (lines 794-1243)

---

## Implementation Order

| Priority | Change | Effort | Section |
|----------|--------|--------|---------|
| 1 | **Write the About page** | 1-2 hrs | A5 |
| 2 | Update meta descriptions (community-safe) | 10 min | A1 |
| 3 | Soften share text | 15 min | A2 |
| 4 | Fix 4 contrast ratios | 15 min | B3 |
| 5 | Add keyboard handler to river cards | 10 min | B2 |
| 6 | Add text labels to status badges on cards | 30 min | B1 |
| 7 | Update status labels and reasons copy | 30 min | D1, D2 |
| 8 | **Write 8 river summaries (first batch)** | 1 hr | A6 |
| 9 | Create OG preview image | 30 min | E1 |
| 10 | Create PWA icons + favicon | 30 min | E2, E3 |
| 11 | Extract CSS custom properties | 2-3 hrs | C1 |
| 12 | Add focus trap to reports modal | 45 min | B4 |
| 13 | Replace emoji nav with SVGs | 1 hr | G1 |
| 14 | Add empty states | 30 min | D4 |
| 15 | Improve loading skeleton | 30 min | F1 |
| 16 | Update footer attribution | 10 min | A3 |
| 17 | Add shop reports disclaimer | 5 min | A4 |
| 18 | Remaining UX copy updates | 30 min | D3, D5, D6 |
| 19 | Semantic list structure | 20 min | B5 |
| 20 | Email form label | 5 min | B6 |
| 21 | Filter/sort announcements | 15 min | B7 |
| 22 | Map marker shapes | 1 hr | B8 |
| 23 | Best Bet banner polish | 15 min | F2 |
| 24 | River notes tone pass | 1 hr | I1 |
| 25 | Subscribe rate limiting | 30 min | H2 |
| 26 | Data source monitoring | 45 min | H3 |

**Total estimated effort:** ~14-16 hours

**Before Reddit launch (items 1-7, ~3 hours):** The About page is now #1 — it's the first link anyone on Reddit will click. Then the meta descriptions, share text, contrast fixes, keyboard access, badge labels, and status copy.

**This week (items 8-17, ~7 hours):** First batch of river summaries in your own voice, OG image, PWA icons, CSS tokens, modal focus trap, SVG nav, empty states, loading skeleton, footer attribution.

**Phase in (items 18-26, ~5 hours):** Remaining copy polish, semantic HTML, map markers, notes tone pass, backend hardening.

**Ongoing weekly (after launch):** Update the 8 river summaries each week alongside the Green Light Report. As you build traffic, use the click-through data to approach shops for formal partnerships (Phase 3 of A6).
