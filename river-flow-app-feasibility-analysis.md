# River Flow App — Feasibility Analysis

**Concept:** An app that connects Google Maps waterways with river system and dam release data, allowing a user to click any point on a river and see the CFS (cubic feet per second) flow rate at that location.

**Date:** March 31, 2026

---

## 1. Data Sources

### Primary: USGS Water Services API

This is the backbone of any US river flow app. The USGS operates approximately **8,700 active streamgages** across the country, recording discharge (CFS), gage height, water temperature, and other parameters. Key details:

- **Update frequency:** Typically every 15 minutes, transmitted hourly.
- **API access:** The legacy API at `waterservices.usgs.gov` is being **decommissioned in early 2027**. The replacement is `api.waterdata.usgs.gov`. Any new app should build against the new API from the start.
- **Data format:** JSON and WaterML. Free, no API key required, generous rate limits.
- **Historical data:** Decades of records available for most stations.
- **Coverage:** Strong in populated areas and major rivers. Sparse in remote/rural headwaters and small tributaries. The western US generally has better coverage of mountain rivers (due to water rights importance) while the Southeast has good coverage of larger rivers but gaps on smaller streams.

### Secondary: NOAA National Water Model (NWM)

This is the key to solving the "ungauged reaches" problem. The NWM simulates streamflow for **2.7 million river reaches** across the continental US — not just the ~8,700 gauged locations. It runs on the NHDPlus river network and produces forecasts (short-range, medium-range, long-range) plus an "analysis and assimilation" product that represents current conditions.

- **Access:** Output is available on AWS and Google Cloud Storage.
- **Resolution:** Covers virtually every mapped stream segment in the NHDPlus network.
- **Accuracy trade-off:** Model estimates at ungauged locations are less reliable than actual gauge readings, particularly during unusual events. But for a "click anywhere" app, this is the dataset that makes it possible.

### Dam Release Data

This is fragmented and messy — one of the harder problems:

- **Army Corps of Engineers:** Provides hourly dam operations data (pool elevation, inflow, outflow) through the Corps Water Management System (CWMS) Data API. Coverage is decent for Corps-managed dams but each district runs its own system (e.g., the Sacramento District at `spk-wc.usace.army.mil`).
- **Bureau of Reclamation:** Provides data for major western dams. The Lower Colorado Region publishes hourly release data. Access is through web reports and some machine-readable formats, but there's no single unified API.
- **State agencies:** Many states run their own dam monitoring. California's CDEC is excellent; other states vary widely.
- **Private dams:** This is a significant gap. There are roughly 91,000 dams in the US (per the National Inventory of Dams). Most small private dams have no public release data whatsoever. Hydropower dams regulated by FERC do publish some data, but it's often on individual operator websites with no standard format.

### River Geometry: National Hydrography Dataset (NHDPlus)

The USGS/EPA NHDPlus High Resolution dataset provides the actual river line geometry you'd overlay on a map. Each stream segment has a unique identifier (COMID/ReachCode) that can be linked to NWM output data. Available as GeoJSON, shapefiles, or through a REST MapServer at `hydro.nationalmap.gov`.

---

## 2. Technical Feasibility

### The Core Architecture

The fundamental approach would be:

1. **Display river geometry** from NHDPlus on the map as clickable polylines.
2. **When a user clicks a point**, identify the nearest NHDPlus stream segment (by COMID).
3. **Check if that segment has a USGS gauge** — if so, return real-time measured CFS.
4. **If ungauged**, return the NWM modeled estimate for that segment.
5. **Enrich with dam release data** where available for upstream dams.

### Gauge-to-River Matching

USGS gauge stations have lat/long coordinates, but they don't always sit neatly on NHDPlus geometry. You'd need a spatial join — snap each gauge to the nearest NHDPlus reach. The USGS has already done much of this work: many gauge sites include an NHDPlus COMID in their metadata. For any that don't, a nearest-neighbor spatial query within a reasonable tolerance (say, 100 meters) would handle most cases.

### Estimating Flow at Ungauged Points

This is the hard technical problem, and there are a few approaches in increasing order of sophistication:

- **Drainage area ratio:** If you know the flow at an upstream gauge and the drainage area at both the gauge and the clicked point, you can estimate: `Q_point = Q_gauge × (Area_point / Area_gauge)`. Simple, works reasonably for nearby points on the same stream, but breaks down at tributary confluences or across different land use types.
- **Linear interpolation:** If there are gauges both upstream and downstream on the same reach, interpolate based on distance or drainage area. Published research shows this works well when conditions don't change significantly within the reach.
- **National Water Model output:** Use the NWM's modeled CFS for the specific NHDPlus segment. This is the most defensible approach for an MVP because the NWM already accounts for precipitation, land use, soil type, and routing. The trade-off is you're showing a model estimate, not a measurement.

**Recommendation for MVP:** Show NWM data as the default for ungauged reaches, with a clear visual distinction (e.g., "Estimated" vs. "Measured") so users understand the confidence level.

### Data Latency

- USGS gauge data: ~15–60 minute delay (recorded at 15-min intervals, transmitted hourly).
- NWM analysis: Updated every 1–3 hours depending on the cycle.
- Dam releases: Varies wildly — some are hourly, some are daily, some are published as schedules days in advance.

For recreational users (kayakers, anglers), a 1-hour latency is generally acceptable. For flood safety, it's not — but that's not your app's primary use case, and NOAA already covers flood warnings.

---

## 3. Mapping Platform

### Google Maps

- **Pros:** Ubiquitous, trusted, good satellite imagery for scouting river access points.
- **Cons:** The Maps JavaScript API supports Data Layers (GeoJSON overlays with click events), but Google Maps doesn't give you native access to its own waterway geometry. You'd be overlaying NHDPlus lines on top of Google's base map. Rendering thousands of river polylines can get expensive (both computationally and in API billing). Google Maps pricing starts free for low volume but scales up quickly.
- **Waterway interaction:** You can't "click on Google Maps' river" — you'd click on your custom NHDPlus polyline overlay that sits on top of the map.

### Mapbox (Recommended for this use case)

- **Pros:** Mapbox Streets v8 includes a native `waterway` layer with river/stream geometry already rendered. You can attach click handlers directly to these built-in features. Vector tiles mean the client only loads visible geometry, so performance is much better for dense river networks. Mapbox also offers more granular styling control (dash arrays, line widths by zoom level, color-coding by flow).
- **Cons:** Smaller brand recognition than Google Maps. The built-in waterway layer may not perfectly match NHDPlus geometry, so you might still want your own overlay for precise gauge matching.
- **Pricing:** Free tier is generous (50,000 map loads/month). More cost-effective than Google for this type of data-heavy overlay.

### Other Options

- **Leaflet + OpenStreetMap:** Free and open-source. Good for a bootstrapped MVP. OSM has decent waterway data. Performance with large GeoJSON datasets requires optimization (vector tiles via Mapbox GL JS or similar).
- **ArcGIS Online:** Overkill for a consumer app, but the USGS already publishes NHDPlus as ArcGIS map services, so there's a path of least resistance for prototyping.

**Recommendation:** Mapbox GL JS for the frontend map. It handles vector tile rendering of dense river networks well, has native waterway features you can interact with, and is more cost-effective for this geometry-heavy use case.

---

## 4. Key Challenges

### Hard Problem #1: The "Click Anywhere" Promise

Users expect to click any blue line on the map and get a number. In reality, only ~8,700 points have measured data. The NWM covers 2.7 million reaches, which is much better, but there are still tiny tributaries and ephemeral streams where even the NWM may not have useful output. You need a graceful degradation strategy: measured → modeled → "no data available."

### Hard Problem #2: Tributary Confluences

A user clicks on the Potomac River just below where the Shenandoah joins it. The flow at that point is roughly the sum of both rivers' flows, minus any losses. If your upstream gauge is above the confluence and your downstream gauge is 50 miles away, simple interpolation will be wrong right at the confluence. The NWM handles this via routing, which is another argument for using it as your estimation backbone.

### Hard Problem #3: Dam Operations

Dams fundamentally alter the flow regime. Below a peaking hydropower dam, CFS can swing from 200 to 5,000 within an hour based on electricity demand. Knowing the "natural" flow means nothing if there's an unmonitored dam upstream. You'd need to identify and flag dam-influenced reaches, ideally with release schedules where available.

### Hard Problem #4: Data Fragmentation

There is no single API for "all US water data." You're stitching together USGS, NOAA NWM, Army Corps, Bureau of Reclamation, and potentially state-level sources. Each has different formats, update frequencies, and reliability. Building and maintaining these integrations is a significant ongoing engineering effort.

### Hard Problem #5: Performance at Scale

The NHDPlus has millions of stream segments. You can't load them all at once. You need a tile-based approach where river geometry loads progressively as the user zooms in, with data fetched on-demand for the clicked segment. This is solvable (vector tiles handle it well) but requires thoughtful architecture.

---

## 5. What You Might Be Missing

### Existing Competition

Several apps already serve parts of this market:

- **RiverApp** — Over 40,000 hydrometric stations worldwide, 20,000+ rivers, with push alerts when flow hits user-defined thresholds. Strong in the kayaking/paddling community. Available on iOS and Android. This is probably your closest competitor.
- **Rivercast** — US-focused, pulls from NWS/NOAA/NWPS data. Targets boaters, fishermen, rafters.
- **American Whitewater** — Not an app per se, but their website is the de facto resource for whitewater paddlers, with flow data tied to specific river runs and difficulty ratings at different levels.
- **USGS National Water Dashboard** (`dashboard.waterdata.usgs.gov`) — The USGS's own map-based interface. Shows all active gauges on a map. Free, authoritative, but not mobile-optimized and doesn't interpolate between gauges.
- **River Brain Flows, HydroGauges** — Smaller apps pulling USGS/NOAA data for gauge-based readings.

**Your differentiation would be the "click anywhere" interpolation** — existing apps show you data *at gauge stations*. None of them (as of this research) let you click an arbitrary river point and get an estimated flow. That's a meaningful gap, but also the hardest feature to build.

### Seasonal & Temporal Complexity

CFS at a given point varies enormously — spring snowmelt on a Colorado river might be 10,000 CFS in June and 200 CFS in September. Users will need context: is this flow normal for the time of year? Historical percentiles (which USGS provides) are critical for making a raw CFS number meaningful.

### Liability and Safety

This is a serious consideration. If someone checks your app, sees "500 CFS" on a river, decides it's safe to kayak, and drowns because the flow spiked to 3,000 CFS from a dam release after your last data update — you have a potential liability exposure. Mitigations:

- Prominent disclaimers that data is not real-time and should not be used as the sole basis for safety decisions.
- Clear labeling of "measured" vs. "estimated" data with confidence indicators.
- Timestamp visibility showing when data was last updated.
- Terms of service with assumption-of-risk language.
- Consider consulting a lawyer familiar with outdoor recreation liability before launch.

### Private and Tribal Water Data

Some rivers cross tribal lands or are managed by private entities. Data availability may be limited or restricted, and there may be sensitivities around publishing flow data for certain waterways.

### International Expansion

If you ever want to go beyond the US, every country has different data infrastructure. Canada (Water Survey of Canada), the EU (various national agencies), and others all have their own systems. RiverApp has tackled this, but it's a massive data integration effort.

### Monetization

- **Freemium with alerts:** Free basic flow lookup; paid tier for push notifications when a specific river hits a target CFS (kayakers and anglers would pay for this).
- **Pro features:** Historical flow charts, trip planning ("will this river be runnable this weekend?"), offline caching.
- **B2B:** Sell API access to outfitters, fishing guides, or environmental consultancies.
- **Advertising:** Targeted ads for outdoor gear, guided trips, etc. (lower margin, can feel cheap).
- **The cautionary note:** USGS data is public domain. Your value is in the UX, interpolation, and curation — not the raw data. Anyone can build a basic gauge viewer, so your moat is the "click anywhere" estimation and the polish of the experience.

---

## 6. MVP Scope

A realistic minimum viable product, buildable by a small team in 3–6 months:

### Include in MVP

- **Map interface** using Mapbox GL JS with NHDPlus waterway overlays (or Mapbox's built-in waterway layer for V1).
- **Click-to-query:** User taps a river → app identifies the NHDPlus segment → returns CFS.
- **USGS gauge integration:** For segments with a nearby gauge, show real-time measured CFS with timestamp.
- **NWM fallback:** For ungauged segments, show the latest NWM modeled estimate, clearly labeled as "Estimated."
- **Basic station info:** When showing gauge data, link to the full USGS page for that station.
- **Mobile-first responsive web app** (PWA) — faster to ship than native, works everywhere.
- **Geographic scope:** Start with one or two popular regions (e.g., Colorado Rockies, Pacific Northwest, Appalachian whitewater corridors) rather than going national on day one.
- **Disclaimers and safety language** baked in from the start.

### Defer to V2+

- Dam release schedules and integration with Corps/BOR data.
- Historical flow charts and seasonal context ("this is above/below normal").
- User accounts, saved rivers, and push notification alerts.
- Flow-based difficulty ratings for whitewater sections.
- Offline mode.
- Native mobile apps.
- National (and eventually international) coverage.
- Trip planning features.

### Tech Stack Suggestion

- **Frontend:** React or Next.js + Mapbox GL JS.
- **Backend:** Node.js or Python (FastAPI) — lightweight API server that proxies/caches USGS and NWM data.
- **Data layer:** PostGIS database with NHDPlus geometry and gauge-to-segment mappings. Pre-process the NWM output into per-segment latest-CFS values on a cron job.
- **Hosting:** AWS or GCP (NWM data is already on both clouds).
- **Estimated infrastructure cost for MVP:** Low — NWM data access is free, USGS API is free, Mapbox free tier covers early users. Main cost is compute for processing NWM output (~$50–200/month) and hosting.

---

## Bottom Line

**This is feasible and there's a real gap in the market.** The data exists (USGS + NWM), the mapping tech is mature (Mapbox), and the "click anywhere for CFS" feature is genuinely differentiated from existing apps that only show gauge station data. The hardest parts are: (1) building reliable flow estimation for ungauged reaches, (2) integrating fragmented dam release data, and (3) managing liability for safety-related usage. The NWM's 2.7-million-reach coverage is the enabler that makes this concept viable now in a way it wouldn't have been five years ago.

The biggest risk is market size — the intersection of "people who care about river CFS" and "people willing to pay for an app" is niche (kayakers, anglers, rafting outfitters, some researchers). But niche markets with passionate users can support a solid business if the product is excellent.

Start regional, nail the UX, and use the "estimated vs. measured" distinction to be honest with users about data quality. That transparency will build trust in a space where trust matters.

---

## Sources

- [USGS Water Data APIs](https://api.waterdata.usgs.gov/)
- [USGS Water Services (legacy, sunsetting 2027)](https://waterservices.usgs.gov/)
- [USGS National Water Dashboard](https://dashboard.waterdata.usgs.gov/)
- [NOAA National Water Model](https://water.noaa.gov/about/nwm)
- [NHDPlus (EPA)](https://www.epa.gov/waterdata/nhdplus-national-hydrography-dataset-plus)
- [NHDPlus HR MapServer (USGS)](https://hydro.nationalmap.gov/arcgis/rest/services/NHDPlus_HR/MapServer)
- [USGS National Hydrography Dataset](https://www.usgs.gov/national-hydrography/national-hydrography-dataset)
- [Army Corps of Engineers Water Data](https://water.usace.army.mil/a2w/f?p=100)
- [Bureau of Reclamation Lower Colorado River Operations](https://www.usbr.gov/lc/riverops.html)
- [RiverApp](https://www.riverapp.net/en)
- [Rivercast](https://www.rivercastapp.com/)
- [Mapbox Streets v8 Tileset Reference](https://docs.mapbox.com/data/tilesets/reference/mapbox-streets-v8/)
- [Google Maps Data Layer API](https://developers.google.com/maps/documentation/javascript/datalayer)
- [USGS Streamflow Monitoring Program](https://www.usgs.gov/programs/groundwater-and-streamflow-information-program/streamflow-monitoring)
- [High-Resolution Streamflow Estimation at Ungauged Sites (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0022169418306796)
