# Looking For Spots — Design Review

**Date:** April 7, 2026 | **Reviewer:** Claude (Design Plugin) | **Stage:** Post-MVP, Pre-Monetization

---

## 1. Design Critique

### Overall Impression

Strong information-dense dashboard that delivers on its core promise — "where should I fish today?" The traffic-light system is immediately scannable, and the three-panel layout (sidebar + map + detail) is a well-proven pattern for geo data apps. The biggest opportunity is visual polish and spacing refinement to move from "dev tool" to "premium product" before introducing a paid tier.

### Usability

| Finding | Severity | Recommendation |
|---------|----------|----------------|
| No empty state guidance when app first loads — user sees "Loading..." with no context | 🟡 Moderate | Add a skeleton UI or a branded splash with "Checking 62 rivers..." progress text |
| "Shop Reports" button looks identical to other header buttons — users may miss it | 🟡 Moderate | Differentiate with an icon (e.g., 📰) or move it into the detail panel where context is relevant |
| Distance filter is hidden until geolocation triggers — users don't know it exists | 🟡 Moderate | Show the filter always, disabled with tooltip "Enable location to filter by distance" |
| Share button in detail panel competes with the river name on small screens | 🟢 Minor | Move share below the status bar or into a button row with favorite |
| Mobile bottom nav uses emoji icons (📋🗺️⭐) which render inconsistently cross-platform | 🟡 Moderate | Replace with inline SVG icons for consistent rendering |

### Visual Hierarchy

- **What draws the eye first:** The green/yellow/red status dots and left-border colors — this is correct and effective
- **Reading flow:** River name → status badge → CFS value → trend arrow — good left-to-right scan
- **Emphasis concern:** The "Best Bet" banner blends into the card list. Increase contrast: larger font, bolder gradient, or a subtle animation on load

### Consistency

| Element | Issue | Recommendation |
|---------|-------|----------------|
| Border radius | Mixed values: 6px (buttons), 8px (inner cards), 10px (sections), 12px (river cards), 16px (modal, mobile detail) | Standardize to 3 tokens: `sm: 6px`, `md: 10px`, `lg: 16px` |
| Font sizes | 11 distinct sizes used (10px–20px) | Reduce to a 5-step type scale: 11, 12, 13, 16, 20 |
| Color usage | `#2563eb` (blue-600) used for interactive + active state + links — all correct. But `#0ea5e9` (sky-500) introduced for share/subscribe diverges from primary blue | Consolidate: use `#2563eb` everywhere for primary actions, or formally adopt sky-500 as a secondary action color |
| Spacing | Mostly 8px/12px/14px/16px/20px — close to a consistent 4px grid but with some 14px values breaking the pattern | Snap to strict 4px grid: 8, 12, 16, 20, 24 |

### What Works Well

- Traffic-light color coding is instantly intuitive — no learning curve
- Card hover states with transform + shadow feel responsive and polished
- Weather, hatch calendar, and reports sections in the detail panel use distinct gradient backgrounds — easy to visually segment
- Mobile responsive breakpoints handle the three-panel → single-panel transition well
- "Best Bet" feature is a killer UX idea — surfaces the one thing the user cares about most

### Priority Recommendations

1. **Unify the border-radius and type scale** — Creates visual cohesion and makes the app feel "designed" rather than "built." 2 hours of CSS cleanup.
2. **Improve the loading/empty state** — First impression matters. A branded skeleton screen with the traffic-light colors pulsing would feel premium. 1 hour.
3. **Replace emoji icons with SVGs** — Emojis render differently on every OS. The mobile nav (📋🗺️⭐) and header (📍🎣) need consistent iconography. Use Lucide or Heroicons via CDN. 2 hours.

---

## 2. Accessibility Audit (WCAG 2.1 AA)

**Issues found:** 12 | **Critical:** 2 | **Major:** 5 | **Minor:** 5

### Perceivable

| # | Issue | WCAG | Severity | Recommendation |
|---|-------|------|----------|----------------|
| 1 | Status communicated only by color (green/yellow/red dots and borders) | 1.4.1 Use of Color | 🔴 Critical | Add text labels or pattern fills. The status badges ("Go Fish", "Don't Go") help but are only in the detail panel — sidebar cards rely on color alone |
| 2 | `#94a3b8` text on `#f8fafc` background = 2.7:1 contrast ratio (multiple locations: detail-type, card-distance, disclaimers) | 1.4.3 Contrast | 🟡 Major | Darken to `#64748b` (4.6:1) or `#475569` (7:1) |
| 3 | `#a16207` on `#fefce8` (yellow status) = 3.8:1 — fails AA for normal text | 1.4.3 Contrast | 🟡 Major | Darken to `#92400e` (5.2:1) |
| 4 | Email signup: `#94a3b8` placeholder on `#1e293b` background = 3.1:1 | 1.4.3 Contrast | 🟢 Minor | Lighten placeholder to `#a1a1aa` or use a visible label instead |
| 5 | Map markers use color alone for status (CircleMarker fill) | 1.4.1 Use of Color | 🟡 Major | Add distinct shapes or patterns per status: circle (green), triangle (yellow), square (red) |

### Operable

| # | Issue | WCAG | Severity | Recommendation |
|---|-------|------|----------|----------------|
| 6 | River cards use `onclick` via JS but are `<div>` elements, not `<button>` or `<a>` | 2.1.1 Keyboard | 🔴 Critical | Add `role="button"` and `tabindex="0"` to `.river-card`, and handle `keydown` Enter/Space |
| 7 | Reports modal has no focus trap — tab key escapes into background content | 2.4.3 Focus Order | 🟡 Major | Trap focus within modal when open; return focus to trigger button on close |
| 8 | Mobile nav buttons use emoji as sole label (📋🗺️⭐) — no visible text label | 2.4.6 Headings and Labels | 🟢 Minor | `title` attributes exist which helps, but add `aria-label` for screen readers and visible small text below icons |

### Understandable

| # | Issue | WCAG | Severity | Recommendation |
|---|-------|------|----------|----------------|
| 9 | Email form has no visible `<label>` — only placeholder text | 3.3.2 Labels | 🟡 Major | Add a visually hidden `<label for="email">` or use `aria-label` on the input |
| 10 | Error messages from subscribe endpoint are generic ("Something went wrong") | 3.3.1 Error Identification | 🟢 Minor | Surface specific errors: "Invalid email format" vs "Already subscribed" |

### Robust

| # | Issue | WCAG | Severity | Recommendation |
|---|-------|------|----------|----------------|
| 11 | `#river-count` has `aria-live="polite"` — good. But sidebar river cards lack semantic structure | 4.1.2 Name, Role, Value | 🟢 Minor | Wrap river list in `<ul>`, each card in `<li>` for screen readers |
| 12 | Sort and filter controls trigger `renderSidebar()` on change but don't announce the update | 4.1.3 Status Messages | 🟢 Minor | Update `#river-count` after filtering so the aria-live region announces the change |

### Color Contrast Check

| Element | Foreground | Background | Ratio | Required | Pass? |
|---------|-----------|------------|-------|----------|-------|
| Body text | #1e293b | #f8fafc | 14.5:1 | 4.5:1 | ✅ |
| Card stats | #64748b | #ffffff | 4.6:1 | 4.5:1 | ✅ |
| Detail disclaimer | #94a3b8 | #ffffff | 2.7:1 | 4.5:1 | ❌ |
| Yellow status text | #a16207 | #fefce8 | 3.8:1 | 4.5:1 | ❌ |
| Green status text | #15803d | #f0fdf4 | 5.1:1 | 4.5:1 | ✅ |
| Red status text | #dc2626 | #fef2f2 | 4.8:1 | 4.5:1 | ✅ |
| Email placeholder | #64748b | #1e293b | 3.1:1 | 4.5:1 | ❌ |
| Footer text | #94a3b8 | #ffffff | 2.7:1 | 4.5:1 | ❌ |

### Priority Fixes

1. **Add text/shape to color-only status indicators** — Affects colorblind users (~8% of male anglers). Critical.
2. **Make river cards keyboard-accessible** — Currently unreachable by keyboard-only users. Critical.
3. **Fix the 4 failing contrast ratios** — Easy CSS changes, big impact.

---

## 3. Design System Audit

### Summary

**Components reviewed:** 18 | **Issues found:** 9 | **Score:** 62/100

The app has an emerging but undocumented design system living entirely in inline CSS. No tokens, no component library, no documentation. For a solo-dev MVP this is fine, but before scaling or adding contributors, these patterns should be formalized.

### Token Coverage

| Category | Defined Tokens | Hardcoded Values Found | Status |
|----------|---------------|----------------------|--------|
| Colors | 0 (all inline hex) | 28 unique hex colors | ❌ Needs tokens |
| Spacing | 0 | 12 unique values (4–24px) | ❌ Needs tokens |
| Typography | 0 | 11 unique font sizes | ❌ Needs tokens |
| Border Radius | 0 | 6 unique values | ❌ Needs tokens |
| Shadows | 0 | 4 unique shadow values | ❌ Needs tokens |

### Recommended Token System

```css
:root {
  /* Colors - Semantic */
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-success: #22c55e;
  --color-warning: #eab308;
  --color-danger: #ef4444;

  /* Colors - Neutral */
  --color-text: #1e293b;
  --color-text-secondary: #64748b;
  --color-text-muted: #94a3b8;
  --color-bg: #f8fafc;
  --color-bg-card: #ffffff;
  --color-border: #e2e8f0;

  /* Typography */
  --text-xs: 11px;
  --text-sm: 12px;
  --text-base: 13px;
  --text-lg: 16px;
  --text-xl: 20px;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;

  /* Radius */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;

  /* Shadows */
  --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.15);
}
```

### Component Completeness

| Component | States | Variants | Accessible | Score |
|-----------|--------|----------|------------|-------|
| River Card | ✅ hover, selected | ✅ green/yellow/red | ⚠️ not keyboard-accessible | 6/10 |
| Status Badge | ✅ | ✅ 3 variants | ⚠️ color-only | 7/10 |
| Button (primary) | ✅ hover, disabled | ⚠️ 1 variant | ✅ | 7/10 |
| Button (header) | ✅ hover, active | ⚠️ 1 variant | ✅ | 7/10 |
| Stat Box | ✅ | ❌ no variants | ✅ | 6/10 |
| Info Section | ✅ | ✅ weather/hatch/reports | ✅ | 8/10 |
| Modal | ✅ open/close | ❌ 1 type | ⚠️ no focus trap | 5/10 |
| Email Form | ✅ success/error | ❌ 1 variant | ⚠️ no label | 5/10 |
| Map Marker | ✅ | ✅ 3 colors | ⚠️ color-only | 5/10 |

### Priority Actions

1. **Extract CSS custom properties** — Move all hex colors and sizes to `:root` variables. 2-3 hours, massive maintainability win.
2. **Document the 3 status variants** — Green/Yellow/Red appear on cards, badges, status bars, map markers. Formalize the pattern.
3. **Create a button component spec** — Currently 4 button styles (primary, header, share, subscribe) with inconsistent sizing.

---

## 4. UX Copy Review

### Header & Navigation

| Element | Current Copy | Issue | Recommended | Rationale |
|---------|-------------|-------|-------------|-----------|
| App title | "Looking For Spots" | Good — memorable and descriptive | Keep as-is | — |
| Refresh button | "Refresh" | Generic | "Check Now" | Action-oriented, implies freshness |
| Near Me button | "📍 Near Me" | Good | Keep, but add aria-label="Find spots near me" | Clarify for screen readers |
| Shop Reports button | "Shop Reports" | Vague — "shop" could mean shopping | "Fly Shop Reports" or "Stream Reports" | Matches what anglers actually call these |

### Status Labels

| Current | Issue | Recommended Alternatives |
|---------|-------|------------------------|
| "Go Fish" (green) | Good — clear, action-oriented | Keep |
| "Fishable With Caveats" (yellow) | Too wordy for a badge (22 chars) | "Fish With Caution" or "Proceed Carefully" |
| "Don't Go" (red) | Direct but slightly negative | "Stay Home" or "Not Today" — softer, still clear |

### Status Reasons (auto-generated)

| Current | Issue | Recommended |
|---------|-------|-------------|
| "No flow data available" | Technical — anglers don't think in "flow data" | "No current readings — check back soon" |
| "Optimal range (526 cfs)" | Good for power users, confusing for novices | "Conditions are ideal (526 cfs)" |
| "Below optimal — low flows" | OK but passive | "Flows are low — wadeable but fewer fish holding" |
| "Above optimal — high water" | OK | "Flows are high — fish deep runs and seams" |

### Email Signup

| Element | Current | Recommended |
|---------|---------|-------------|
| Heading | "Get the Weekly Green Light Report" | Keep — strong, specific, uses the brand language |
| Subtext | "Every Monday — which spots went green, what's hatching, and where to fish." | Keep — clear value prop, answers "what do I get?" |
| Placeholder | "your@email.com" | Keep — standard |
| Button | "Subscribe" | "Get the Report" — more specific, matches the heading |
| Success | "You're in! Watch for the Green Light Report." | Good — confirms and sets expectation |
| Error | "Something went wrong." | "Couldn't subscribe — try again in a moment." |

### Empty States

| State | Current | Recommended |
|-------|---------|-------------|
| No favorites | (nothing shown) | "No saved spots yet. Tap the ⭐ on any river to add it here." |
| No reports for river | "No reports available yet" | "No recent shop reports for this river. Check back — shops update weekly." |
| No weather data | (shows nothing) | "Weather data loading — check back in a few minutes." |
| Reports modal empty filter | (nothing shown) | "No reports from this shop recently. Try 'All' to see everything." |

### Share Feature

| Element | Current | Recommended |
|---------|---------|-------------|
| Button label | "🔗 Share" | "Share Spot" — clearer action |
| Share text | "McCloud River is GREEN (526 cfs) right now!" | Good — includes status + data, creates urgency |
| Copied feedback | "Copied!" | "Link copied — send it to your crew!" — more fun, on-brand |

### Loading State

| Current | Recommended |
|---------|-------------|
| "Loading river conditions..." | "Checking 62 rivers..." — more specific, builds anticipation |
| "Loading..." (refresh button) | "Checking..." — matches |

---

## Summary of All Priorities

| # | Fix | Source | Effort | Impact |
|---|-----|--------|--------|--------|
| 1 | Add text/shape indicators alongside status colors | Accessibility | 2 hrs | 🔴 Critical — colorblind users blocked |
| 2 | Make river cards keyboard-accessible | Accessibility | 1 hr | 🔴 Critical — keyboard users blocked |
| 3 | Fix 4 failing contrast ratios | Accessibility | 30 min | 🟡 High — readability |
| 4 | Extract CSS custom properties (design tokens) | Design System | 3 hrs | 🟡 High — maintainability |
| 5 | Replace emoji icons with SVGs | Critique | 2 hrs | 🟡 Medium — cross-platform consistency |
| 6 | Improve loading/empty states | Critique + UX Copy | 1 hr | 🟡 Medium — first impression |
| 7 | Add focus trap to reports modal | Accessibility | 1 hr | 🟡 Medium — modal usability |
| 8 | Unify border-radius and type scale | Design System | 1 hr | 🟢 Low — visual polish |
| 9 | Update UX copy per recommendations | UX Copy | 1 hr | 🟢 Low — tone refinement |
