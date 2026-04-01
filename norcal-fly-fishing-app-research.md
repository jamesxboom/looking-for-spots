# NorCal Fly Fishing River Conditions App — Research Report

*March 31, 2026*

---

## 1. How Fly Fishing Guides/Apps Currently Handle Flow Conditions

### The Core Problem

Every existing flow app shows raw CFS numbers, but almost none translate those numbers into "is this river fishable right now?" Anglers are forced to interpret the data themselves or call a guide. This is the central gap in the market.

### What Existing Tools Do

**Fishbrain** integrates 10,000+ USGS gauges with a map interface. It shows real-time CFS charts, gauge height, water temperature, and 60-day historical trend lines with averages shown as dotted lines. Pro users get advanced flow trending. But it's species-agnostic and doesn't categorize conditions as good or bad for any specific type of fishing.

**TroutRoutes** (onX ecosystem) is the most trout-specific app, covering CA, WA, OR, MT, WY, CO, UT, ID. It has 50,000+ trout stream maps with 280,000+ curated access points and a "My Gages" feature for saving favorite gauges. However, it still shows raw data rather than fishability ratings.

**onWater Fish** has a "My Waters" dashboard consolidating gauges with weather and lunar data, plus customizable flow range alerts. It introduced the concept of "fishability" in their blog content, but the app itself doesn't generate fishability scores.

**DriftWise** provides free daily fly fishing reports for 50 top US trout/steelhead rivers with real-time flow, weather, and hatch data updated each morning. This is closer to what anglers want, but covers only 50 rivers nationwide.

**FlyFishFinder** is notable for letting users set custom "preferred CFS ranges" with push alerts when flows hit their sweet spot. It also has interactive hatch charts for 30+ rivers. This is the closest to a fishability tool.

**RiverBrain** uses color-coded visuals indicating which runs are "in" at a glance — green/yellow/red — correlated to actual run information at specific gauges. This is the most direct precedent for a traffic-light system, though it appears limited in scope.

### How Local NorCal Guides Communicate

**The Fly Shop (Redding)** publishes a weekly Northern California Stream Report rating rivers from "Poor" to "Great" with specific CFS numbers and conditions notes. They report flows like "Sacramento River spring flows 3,250-5,000 CFS low, 5-7,000 CFS high" with interpretation of what that means for fishing.

**Ted Fay Fly Shop (Dunsmuir)** publishes Guide Notes with specific CFS at various gauges (e.g., "Upper Sac flows are 689 at the bottom"), water temperatures ("mid 50s to maybe low 60s for Dunsmuir"), and a 10-day forecast.

**Clearwater Lodge** guides on Hat Creek, Fall River, Pit River, McCloud, and Lower Sacramento but relies on phone/email communication rather than published conditions data.

**Key Pattern**: Guides translate CFS into plain language ("fishing has been excellent," "river is running high but manageable in a drift boat," "stay home this week"). They combine flow data with water temp, hatch activity, and personal experience. No guide just gives a CFS number — they always contextualize it.

### USGS WaterWatch (Being Decommissioned)

Uses percentile-based categories: Much Below Normal (<10th), Below Normal (10-24th), Normal (25-75th), Above Normal (76-90th), Much Above Normal (>90th). Color-coded on maps. This is useful for general hydrology but doesn't map to fishing conditions — "normal" flow could still be unfishable depending on the river and season.

---

## 2. River-Specific Optimal CFS Ranges for Fly Fishing

This is the critical dataset for the app. Each river has dramatically different characteristics.

### Lower Sacramento River (Below Keswick Dam)

| Condition | CFS Range |
|-----------|-----------|
| Optimal for wading | 4,000–7,500 |
| Good general fishing | 5,000–8,000 |
| Drift boat recommended | Above 7,500 |
| Maximum fishable (wading) | ~10,000 |
| Blown out / dangerous | Above 10,000 |
| Winter typical | ~4,000 |
| Summer (irrigation) | 7,000–10,000 |
| Fall sweet spot | 5,000–6,000 |

**Notes**: Tailwater. Very wide river — higher CFS is manageable compared to smaller streams. Wading access opens up below 7,500 CFS. Most guided trips are drift boat regardless of flow.

### Upper Sacramento River (Above Lake Shasta)

| Condition | CFS Range |
|-----------|-----------|
| Optimal | 800–1,200 |
| Sweet spot (Delta gauge) | ~1,100 |
| High but fishable | 1,200–2,000 |
| Blown out (spring runoff) | Above 2,500 |

**Notes**: Freestone river. Easy wading when flows are in range. Spring runoff (March–June) can push flows too high. Recovery from 2016 I-5 spill has been strong.

### McCloud River

| Condition | CFS Range |
|-----------|-----------|
| Holy Water section (wadeable) | 170–250 |
| Optimal (opens full river) | 600–1,000 |
| Summer dam releases (stable) | ~200 |

**Notes**: Spring-fed below McCloud Reservoir. Remarkably consistent summer flows. The Holy Water section is the most popular and is wadeable at typical summer flows.

### Hat Creek

| Condition | CFS Range |
|-----------|-----------|
| Wild Trout section (good) | 380–500 |
| Stable powerhouse releases | 550–650 |
| Low but fishable | 125–380 |

**Notes**: Spring creek. Rarely affected by runoff. The Wild Trout section below Powerhouse 2 is the prime water. Consistent flows make this a reliable destination.

### Fall River

**Unique case**: Nation's largest spring creek. Average 6+ feet deep. Wading is essentially impossible — fishing is from drift boats, float tubes, or prams. Flows remain consistent year-round due to spring-fed origin. CFS thresholds are less relevant here; water temperature and hatch activity matter more.

### Pit River

| Condition | CFS Range |
|-----------|-----------|
| Optimal (Pit 3) | 300–430 |
| Great flow | ~310 |
| Typical range | 390–430 |
| Below Pit 4 Dam | ~450 |
| Fall minimum | ~300 |

**Notes**: Dam-controlled, fast year-round. Notorious for difficult wading even at optimal flows (slippery basalt boulders). Wading staff essential.

### North Yuba River

| Condition | CFS Range |
|-----------|-----------|
| Optimal | Below 200 |
| Fishable | Up to 800 |
| Best season | Late spring–fall |

**Notes**: Low-flow freestone. Small stream character. Best when flows drop after spring runoff.

### Lower (South) Yuba River

| Condition | CFS Range |
|-----------|-----------|
| Fishable | 2,700–3,400 |

**Notes**: Consistent flows from Englebright Dam releases. Higher volume than North Yuba.

### Truckee River

| Section | Optimal CFS |
|---------|-------------|
| Upper (Town of Truckee) | 200–300 |
| Middle (Below Martis Creek) | 500–600 |
| Canyon Section | 1,000+ (advanced wading) |
| Summer base flows | ~300 |

**Notes**: Dam-controlled from Lake Tahoe. High runoff March–June makes fishing difficult. Best fishing late spring/early summer and fall.

### Little Truckee River

| Condition | CFS Range |
|-----------|-----------|
| Perfect | ~350 |
| Good spring | 130–200 |
| Winter | ~47 |
| Summer | 150–200 |

**Notes**: Tailwater with consistent temperatures. Highly responsive to seasonal changes. March 2026 report showed 132 CFS with 40–46°F water temp as ideal for the season.

### East Walker River

| Condition | CFS Range |
|-----------|-----------|
| Optimal releases | 175–225 |
| Good fishing range | 80–250 |
| Max fishable | 280 |
| Wading dangerous | Above 350 |

**Notes**: Miracle Mile section has particularly slippery rocks. Nymphing best at 50–300 CFS; streamers better above 300 CFS.

### Hot Creek

| Condition | CFS Range |
|-----------|-----------|
| Typical flow | 8–50 (spring-fed, very low) |
| Water temp | 40s cold season, low 60s warm |

**Notes**: Extremely clear spring creek. Very technical fishing. Tiny stream — CFS numbers are low but the creek is fishable year-round.

### Upper Owens River

| Condition | CFS Range |
|-----------|-----------|
| Optimal | 100–140 |
| Above Hot Creek confluence | ~108 |
| Below Hot Creek | ~140 |

### Lower Owens River

| Condition | CFS Range |
|-----------|-----------|
| Optimal | Below 300 |
| Good | 80–280 |
| Wading dangerous | Above 300 |

### Trinity River

| Condition | CFS Range |
|-----------|-----------|
| Optimal (upper) | 300–1,000 |
| Most comfortable | 450–550 |
| Winter baseflow | ~300 |
| Restoration pulses (spring) | 300–1,700 |
| High flow (May–June) | 5,000–12,000 |

**Notes**: Tailwater below Lewiston Dam. Spring restoration flows from Trinity River Restoration Project create periodic high-water events.

### Feather River (Below Oroville)

| Condition | CFS Range |
|-----------|-----------|
| Low flow section standard | ~600 |

**Notes**: Primarily steelhead/salmon-focused. Low flow section is ~5.5 miles from hatchery to Thermalito Afterbay Outlet.

### Lower American River

| Condition | CFS Range |
|-----------|-----------|
| Optimal for wading | ~1,500 |
| Good range | 1,500–3,000 |
| Harder wading | 3,000–5,000 |
| Dangerous | Above 5,000 |
| Drift boat safe | Below 6,000 |

**Notes**: Primarily boat-fished. Wading challenging even at optimal flows. Fish get spooky below 1,500 CFS (too clear/shallow).

---

## 3. The Traffic Light System — Analysis

### Why It Works

The Surfline model is the gold standard for translating complex environmental data into simple decisions. Surfline uses 7 levels (VERY POOR through EPIC) with color coding from red/orange through yellow to green. The key insight: **the color answers the user's primary question before they even read any text.**

**Surfline's approach**: Complex data (wave height, wind, period, swell direction, tide) → single color rating. Detailed data available one tap deeper for those who want it.

### Proposed System for Fly Fishing

**Three-tier traffic light per river:**

**GREEN — Go Fish**
- Flow within optimal range for this specific river
- Water temp below 65°F
- Flows stable or slowly falling
- Translation: "Conditions are good. Worth the drive."

**YELLOW — Fishable With Caveats**
- Flow outside optimal but still fishable (high side or low side)
- Water temp 65–68°F (fish carefully, minimize fight time)
- Flows rising moderately
- Translation: "You can fish, but it won't be ideal. Consider alternatives."

**RED — Don't Go**
- Flow above maximum fishable (blown out) or well below minimum
- Water temp above 68°F (ethical concern — trout mortality)
- Rapid flow changes (rising fast from dam release or storm)
- Translation: "Save your gas. Try a different river or wait."

### How to Set Thresholds

**Option A: Expert-defined (MVP approach)**
Use the CFS ranges documented in Section 2 above. For each river, define:
- Green floor and ceiling (optimal range)
- Yellow floor and ceiling (fishable but not optimal)
- Red thresholds (blown out / too low)
- Temperature override: any temp above 68°F forces Yellow or Red regardless of flow

**Option B: Guide-crowdsourced (V2)**
Build relationships with 5–10 NorCal guides. Give them a simple interface to set/adjust thresholds per river per season. Guides already know this intuitively. Seasonal adjustment is important — what's "green" in July may be "yellow" in March due to snowmelt expectations and hatch timing.

**Option C: Historical percentile-based (automated)**
Use USGS historical data to calculate percentile ranges. Map "normal" flows (25th–75th percentile for that time of year) to Green. This auto-adjusts seasonally. Limitation: "normal" doesn't always mean "fishable" — a river at its normal spring runoff level might still be blown out for fishing. This is why expert input is needed.

**Recommended approach**: Start with Option A using the data above, then add Option B as a refinement layer. Option C can supplement but shouldn't replace expert knowledge.

### Temperature Overrides

This is critical and non-negotiable:

- Below 65°F: no temperature-based override
- 65–67°F: yellow flag — "Water is warming. Fish early morning."
- Above 68°F: RED — "Water too warm. Trout are stressed. Do not fish for trout."

This override should trump all other conditions. If the McCloud is at perfect flow but water temp is 71°F, it must show Red.

---

## 4. What Else Matters Besides CFS

### Tier 1: Critical (Include in MVP)

**Water Temperature**
- Optimal trout feeding: 50–65°F
- Stress threshold: 67°F (recovery from fighting is compromised)
- Stop fishing: 68–70°F (insufficient dissolved oxygen; post-release mortality)
- Importance: CRITICAL — ethical and practical
- API available: YES (CDEC Sensor 25, USGS parameter 00010)

**Rate of Change (Flow Trend)**
- Stable flows: BEST for fishing. Fish are comfortable and feeding.
- Slowly falling: GOOD. Fish sense dropping water and become active feeders.
- Rising water: MIXED. Can stimulate feeding but also muddies water.
- Rapidly changing (either direction): POOR. Fish hunker down.
- Importance: HIGH
- API available: YES — calculate from consecutive CDEC/USGS readings (delta over 3–6 hours)
- UX: Simple trend arrows (↑ rising, → stable, ↓ falling) with color coding

### Tier 2: Important (Include in V2)

**Hatch Activity**
- Determines what flies to use and when to be on the water
- NorCal key hatches: Blue-winged olives (Baetis), pale morning duns, October caddis, March browns, stoneflies, tricos
- No public API exists — this is manual/community-driven data
- The Fly Shop publishes hatch charts; Sierra Nevada hatch charts exist based on 15+ years of Truckee River data
- Can approximate timing from water temperature + Julian day
- Importance: HIGH for fly selection; MODERATE for "should I go?" decision
- Integration: Static seasonal hatch calendar per river, refined by current water temp

**Turbidity / Clarity**
- Clear water: smaller flies (#18-20), lighter tippet, more careful approaches
- Murky water: larger, flashier flies, less spooky fish
- Importance: MODERATE-HIGH
- API: PARTIAL — some USGS stations have turbidity sensors but coverage is spotty

**Recent Fish Stocking**
- CDFW publishes stocking data at nrm.dfg.ca.gov/FishPlants/
- No dedicated API, but the portal can be scraped
- Importance: MODERATE — affects planted sections dramatically

### Tier 3: Nice to Have (V3+)

**Barometric Pressure**: Optimal 29.70–30.40 inches; falling pressure can stimulate feeding. Available via weather APIs. Low-moderate importance.

**Moon Phases**: Inconsistent evidence for effect on trout feeding. Easy to include via lunar APIs. Low importance.

**Air Temperature / Weather**: Standard weather API data. Useful for trip planning comfort, less so for fish behavior prediction (water temp is what matters).

**Road/Access Conditions**: Critical for trip logistics (Caltrans QuickMap at quickmap.dot.ca.gov). Not a fishing condition per se, but essential for "should I drive there?" decisions.

---

## 5. Water Temperature Data Availability

### CDEC (California Data Exchange Center)

- **Sensor 25** specifically measures water temperature in °F
- 211 stations with 1,270 sensors statewide
- Many stations have flow data but NOT temperature — temp coverage is less comprehensive

**API endpoint**: `http://cdec.water.ca.gov/dynamicapp/wsSensorData`
- Formats: JSON, CSV, XML
- Parameters: Station ID, Sensor number (25 for temp), duration code (H=hourly), date range
- Example: `cdec.water.ca.gov/dynamicapp/req/CSVDataServlet?Stations=HHM&SensorNums=25&dur_code=H&Start=2026-03-01&End=2026-03-31`

### USGS

- Parameter code 00010 for water temperature
- Real-time data limited to 120 days
- Daily values service has longer historical records
- 13,500+ stations nationwide via National Water Dashboard

**API**: `waterservices.usgs.gov/` — JSON, XML, RDB formats

### NorCal River Temperature Coverage

Rivers with confirmed real-time temperature monitoring:
- Lower Sacramento River (multiple stations from Keswick downstream) — GOOD coverage
- Upper Sacramento River — some coverage
- American River — hourly data available
- Trinity River — monitoring exists

Rivers with likely but unconfirmed temp data:
- Truckee River, Pit River, Feather River — likely have some stations

Rivers with uncertain/limited temp coverage:
- McCloud, Hat Creek, Fall River, East Walker, Hot Creek, Owens — may need supplementary data sources or manual monitoring

### Key Finding

**Temperature data is less universally available than flow data.** Many CDEC/USGS stations measure flow but not temperature. For the MVP, you'll need to inventory which specific stations have Sensor 25 data for each of the target rivers. Where temp data is missing, you could use air temperature as a rough proxy (with appropriate caveats) or partner with local guides who measure temp manually.

### Additional Temperature Sources

- **USBR (Bureau of Reclamation)**: Northern CVP Water Temperature Report covers Sacramento River from Keswick downstream
- **SacPAS**: Sacramento Prediction and Assessment of Salmon — provides temperature threshold analysis using CDEC data
- **Trout Unlimited**: Operates 50 gauges in California (largest non-governmental stream gauge system in the state) — some may include temperature

---

## 6. Simplicity-First UX for Fly Fishermen

### The Core User Story

> "It's 6 AM on Saturday. I have 8 hours free. I'm willing to drive up to 2.5 hours. Should I fish the McCloud, Hat Creek, or the Upper Sac today?"

The app needs to answer this in under 10 seconds.

### Surfline as the Model

Surfline proved that complex environmental data can be reduced to a color and a word. Surfers see "GOOD" in green and know to grab their board. The detailed data (swell height, period, wind, tide) is there for those who want it, but the color answers the question.

### Proposed Information Architecture

**Level 1: Dashboard (The Glance)**
- List of "My Rivers" (user picks favorites)
- Each river shows: Name, Traffic Light (Green/Yellow/Red), Water Temp, Trend Arrow
- Sorted by condition (Green first) or by distance
- Total time on screen: 3 seconds to answer "where should I go?"

**Level 2: River Detail (The Check)**
- Tap a river to see:
  - Current CFS + what's optimal for this river ("4,200 CFS — optimal is 4,000–7,500")
  - Water temperature with threshold warning if applicable
  - Flow trend over last 24 hours (simple sparkline chart)
  - Hatch calendar for current week ("BWOs expected afternoon, caddis at dusk")
  - Today's weather at the river
  - Last updated timestamp

**Level 3: Deep Dive (The Nerd)**
- Historical flow chart (30 days)
- Year-over-year comparison
- Full hatch chart for the season
- Access points and directions
- Link to guide reports (The Fly Shop, Ted Fay, etc.)

### Key UX Principles

1. **Answer the question, then explain.** Color first, data second.
2. **Temperature warnings are non-negotiable.** If water is above 68°F, show a prominent warning. This isn't just about fishing quality — it's about fish survival.
3. **Trend matters as much as current value.** A river at 6,000 CFS and falling is different from 6,000 CFS and rising. Show this with simple arrows.
4. **"Fish or don't fish" > "interpret these numbers."** The user shouldn't need to know that 4,200 CFS on the Lower Sac is good. The app should know that.
5. **Offline support is essential.** Many NorCal fishing spots have zero cell coverage. Cache the morning's conditions for offline viewing.
6. **Don't replicate mapping.** TroutRoutes and onX already do maps well. Focus on conditions.

### Visual Design Inspiration

- **Surfline**: Color-coded conditions with one-word summary
- **Ski resort apps**: Multi-resort comparison at a glance (OnTheSnow's "Powder Finder")
- **Weather apps**: Simple current conditions with "feels like" translation

---

## 7. Competitive Landscape

### Direct Competitors (Flow/Conditions for Fishing)

| Tool | What It Does | NorCal Coverage | Fishability Rating? | Gap |
|------|-------------|-----------------|--------------------|----|
| RiverApp | 40K+ gauges worldwide, raw flow data | Yes (via USGS) | No | No fishing context |
| TroutRoutes | Trout stream maps + "My Gages" | CA covered | No | Maps-focused, no conditions rating |
| onWater Fish | Dashboard with flow + weather + lunar | Yes | No (but coined "fishability") | No per-river thresholds |
| DriftWise | Daily reports for 50 US rivers | Limited NorCal | Implicit (editorial) | Only 50 rivers, not interactive |
| FlyFishFinder | Custom CFS alerts + hatch charts | Some | User-set ranges | User must set own thresholds |
| RiverBrain | Color-coded run status | Unknown | YES (green/yellow/red) | Appears limited scope |
| Fishbrain | 10K gauges + trends | Yes | No | General fishing, not fly-specific |

### NorCal-Specific Resources (Not Apps)

| Resource | Format | Update Frequency |
|----------|--------|-----------------|
| The Fly Shop Stream Report | Web page, text | Weekly |
| Ted Fay Guide Notes | Web page, text | Regular |
| California Fly Fishing Reports | Web page | Weekly |
| AC Fly Fishing Reports | Web page | Weekly |
| Matt Dover Fly Fishing Report | Web page | Regular |

### The Gap

**Nobody is doing all three of these things for NorCal:**
1. Aggregating flow + temp + conditions across multiple rivers
2. Translating that data into a simple fishability rating per river
3. Presenting it in a mobile-friendly, at-a-glance format

The closest is The Fly Shop's stream report, but it's a text-based web page updated weekly. The closest app-based approach is RiverBrain's color-coded system, but it doesn't appear to have significant NorCal coverage.

**This is a real, underserved niche.** Fly fishermen in NorCal are currently checking 3–5 different sources (USGS gauges, fly shop websites, weather apps, forum posts, phone calls to guides) to answer a question that should take 10 seconds.

---

## 8. MVP Specification

### The Simplest Useful Version

**Name concept**: Something like "NorCal Flows" or "Hatch & Flow" or "Fish Check"

**Scope**: 12–15 NorCal trout rivers with traffic light conditions

### Rivers for MVP

1. Lower Sacramento River
2. Upper Sacramento River
3. McCloud River
4. Hat Creek
5. Fall River
6. Pit River
7. Trinity River
8. Truckee River
9. Little Truckee River
10. East Walker River
11. Lower Owens River
12. Upper Owens River
13. North Yuba River
14. Lower American River
15. Hot Creek

### Data Per River

| Data Point | Source | Update Frequency |
|-----------|--------|-----------------|
| Current CFS | CDEC/USGS API | Hourly |
| Optimal CFS range | Hardcoded per river (from Section 2) | Static (seasonal adjustment) |
| Traffic light status | Calculated from CFS vs. optimal range | Hourly |
| Water temperature | CDEC Sensor 25 / USGS | Hourly (where available) |
| Flow trend | Calculated (current vs. 6 hours ago) | Hourly |
| Hatch info | Static seasonal data per river | Monthly update |

### Traffic Light Algorithm (V1)

```
function getStatus(river, currentCFS, waterTemp, cfsChange6hr):

  // Temperature overrides everything
  if waterTemp > 68: return RED ("Water too warm for trout")
  if waterTemp > 65: tempWarning = true

  // Flow-based status
  if currentCFS >= river.greenFloor AND currentCFS <= river.greenCeiling:
    status = GREEN
  elif currentCFS >= river.yellowFloor AND currentCFS <= river.yellowCeiling:
    status = YELLOW
  else:
    status = RED

  // Rate of change modifier
  if abs(cfsChange6hr) > river.rapidChangeThreshold:
    status = max(status, YELLOW)  // bump to at least yellow

  // Temperature warning overlay
  if tempWarning and status == GREEN:
    status = YELLOW ("Good flow but water warming — fish early")

  return status
```

### Tech Stack (Lean)

- **Frontend**: React web app (responsive, works on mobile)
- **Backend**: Simple Node/Python service
- **Data**: CDEC + USGS APIs (free, public)
- **Hosting**: Vercel or similar (low cost)
- **No login required** for viewing (consider accounts later for favorites/alerts)

### What to Build First (Week 1–2)

1. Data pipeline: Pull CFS and temp from CDEC/USGS for all 15 rivers
2. River config: Hardcode optimal ranges per river from Section 2 data
3. Traffic light calculator: Implement the algorithm above
4. Dashboard UI: List view with river name, traffic light, temp, trend arrow
5. River detail page: Current CFS, optimal range context, 24hr trend chart

### What to Add Next (Week 3–4)

- Push notifications when a favorite river changes status
- Hatch calendar per river (static data, manually curated)
- "Best conditions right now" — auto-sort by status
- Historical comparison ("flows are X% above average for this date")

### What to Save for V2

- Guide reports integration (partnership with The Fly Shop, Ted Fay)
- Community reporting ("I'm on Hat Creek — BWOs hatching heavy")
- Offline caching
- Weather integration
- Road/access conditions
- Stocking alerts (CDFW data)

### Validation Strategy

1. Share with 10–15 NorCal fly fishermen for feedback on traffic light accuracy
2. Compare your status ratings to The Fly Shop's weekly stream report — are they aligned?
3. Track: Do users check the app before driving to fish? That's the core success metric.
4. Partner with 2–3 guides for threshold calibration — pay them in attribution/links

---

## Key Sources

### Apps & Tools
- Fishbrain: fishbrain.com
- TroutRoutes: troutroutes.com
- onWater: onwaterapp.com
- DriftWise: driftwise.app
- FlyFishFinder: flyfishfinder.com
- RiverApp: riverapp.net

### NorCal Guide Reports
- The Fly Shop: theflyshop.com/streamreport.html
- Ted Fay Fly Shop: tedfay.com/guidenotes
- California Fly Fishing Reports: californiaflyfishingreports.com
- Matt Dover Fly Fishing: mattdoverflyfishing.com

### Data APIs
- CDEC: cdec.water.ca.gov (Sensor 25 for temp, Sensor 20 for flow)
- USGS: waterservices.usgs.gov (param 00010 for temp, 00060 for discharge)
- CDFW Fish Plants: nrm.dfg.ca.gov/FishPlants/
- Caltrans QuickMap: quickmap.dot.ca.gov

### UX References
- Surfline conditions model: surfline.com
- OnTheSnow ski conditions: onthesnow.com
