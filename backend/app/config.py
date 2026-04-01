"""
River configuration with thresholds, USGS site IDs, CDEC stations, and coordinates.

Thresholds are calibrated for FLY FISHING conditions (NOT kayaking/rafting).
Dual-mode rivers (Lower Sacramento, Trinity) have separate wade and drift boat thresholds.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List


@dataclass
class RiverThresholds:
    green_floor: float
    green_ceiling: float
    yellow_floor: float
    yellow_ceiling: float
    rapid_change_threshold: float
    notes: str


@dataclass
class RiverConfig:
    id: str
    name: str
    river_type: str  # 'tailwater', 'freestone', 'spring_creek', 'dam_controlled'
    latitude: float
    longitude: float
    usgs_site_id: Optional[str]
    cdec_station_id: Optional[str]
    thresholds: RiverThresholds
    # Dual-mode support: rivers fishable by both wade and drift boat
    fishing_modes: List[str] = field(default_factory=lambda: ["wade"])
    wade_thresholds: Optional[RiverThresholds] = None
    drift_thresholds: Optional[RiverThresholds] = None
    blown_out_cfs: Optional[float] = None  # Hard red above this
    dangerous_wade_cfs: Optional[float] = None  # Wading danger threshold


# =============================================================================
# FLY FISHING thresholds for NorCal rivers
# These are NOT kayaking/rafting thresholds (which are much higher).
# Sources: guide reports, fly shop intel, angler consensus.
# =============================================================================

RIVER_THRESHOLDS = {
    # --- LOWER SACRAMENTO ---
    # Drift boat river. Wade fishing not typical on the Lower Sac.
    # Drift boat optimal 4,000-8,000 CFS, blown out above ~12,000.
    "lower_sacramento": RiverThresholds(
        green_floor=4000,
        green_ceiling=8000,
        yellow_floor=3000,
        yellow_ceiling=12000,
        rapid_change_threshold=1500,
        notes="Drift boat river — wade fishing not typical. Optimal 4,000–8,000 cfs. Blown out above ~12,000."
    ),

    # --- UPPER SACRAMENTO ---
    # Optimal 400-800 CFS, wadeable below ~600, blown out above 1,200.
    "upper_sacramento": RiverThresholds(
        green_floor=400,
        green_ceiling=800,
        yellow_floor=300,
        yellow_ceiling=1200,
        rapid_change_threshold=200,
        notes="Optimal 400–800 cfs at Delta gauge. Wadeable below ~600. Blown out above 1,200."
    ),

    # --- McCLOUD RIVER ---
    # Optimal 800-1,200 CFS, wadeable below ~900.
    "mccloud": RiverThresholds(
        green_floor=800,
        green_ceiling=1200,
        yellow_floor=600,
        yellow_ceiling=1500,
        rapid_change_threshold=200,
        notes="Optimal 800–1,200 cfs. Wadeable below ~900. Spring-fed, relatively stable."
    ),

    # --- HAT CREEK ---
    # Spring creek — very low flows. Optimal 50-120 CFS.
    "hat_creek": RiverThresholds(
        green_floor=50,
        green_ceiling=120,
        yellow_floor=30,
        yellow_ceiling=180,
        rapid_change_threshold=30,
        notes="Spring creek, very low flows. Optimal 50–120 cfs. Wild Trout section below Powerhouse 2."
    ),

    # --- FALL RIVER ---
    # Spring-fed, very stable. Optimal 300-500 CFS. Always boat/tube fishing.
    "fall_river": RiverThresholds(
        green_floor=300,
        green_ceiling=500,
        yellow_floor=200,
        yellow_ceiling=600,
        rapid_change_threshold=50,
        notes="Spring-fed, very stable. Optimal 300–500 cfs. Boat/tube fishing only — no wading."
    ),

    # --- PIT RIVER ---
    # Optimal 280-450 CFS depending on section/powerhouse.
    "pit_river": RiverThresholds(
        green_floor=280,
        green_ceiling=450,
        yellow_floor=200,
        yellow_ceiling=600,
        rapid_change_threshold=75,
        notes="Optimal 280–450 cfs (varies by section/powerhouse). Difficult wading — wading staff essential."
    ),

    # --- TRINITY RIVER ---
    # Dual-mode: Wade fishing optimal 300-800 CFS, drift boat 800-2,500 CFS.
    # Default thresholds cover wade fishing (the more restrictive mode).
    "trinity": RiverThresholds(
        green_floor=300,
        green_ceiling=800,
        yellow_floor=200,
        yellow_ceiling=1200,
        rapid_change_threshold=400,
        notes="Wade optimal 300–800 cfs. Drift boat 800–2,500 cfs. Spring restoration pulses can spike flows."
    ),

    # --- TRUCKEE RIVER ---
    # Optimal 150-350 CFS for wading.
    "truckee": RiverThresholds(
        green_floor=150,
        green_ceiling=350,
        yellow_floor=100,
        yellow_ceiling=500,
        rapid_change_threshold=100,
        notes="Optimal 150–350 cfs for wading. Canyon section handles higher flows from a drift boat."
    ),

    # --- LITTLE TRUCKEE ---
    # Optimal 50-150 CFS.
    "little_truckee": RiverThresholds(
        green_floor=50,
        green_ceiling=150,
        yellow_floor=30,
        yellow_ceiling=200,
        rapid_change_threshold=50,
        notes="Optimal 50–150 cfs. Tailwater below Stampede with consistent temps."
    ),

    # --- EAST WALKER ---
    # Optimal 100-225 CFS, dangerous wading above 350.
    "east_walker": RiverThresholds(
        green_floor=100,
        green_ceiling=225,
        yellow_floor=75,
        yellow_ceiling=350,
        rapid_change_threshold=50,
        notes="Miracle Mile. Optimal 100–225 cfs. Dangerous wading above 350 cfs."
    ),

    # --- YUBA RIVER ---
    # Optimal 300-800 CFS for wading.
    "yuba": RiverThresholds(
        green_floor=300,
        green_ceiling=800,
        yellow_floor=200,
        yellow_ceiling=1200,
        rapid_change_threshold=200,
        notes="Optimal 300–800 cfs for wading. Multiple forks — conditions vary."
    ),

    # --- NORTH FORK AMERICAN ---
    # Optimal 500-1,000 CFS.
    "north_fork_american": RiverThresholds(
        green_floor=500,
        green_ceiling=1000,
        yellow_floor=350,
        yellow_ceiling=1500,
        rapid_change_threshold=300,
        notes="Optimal 500–1,000 cfs. Can run high during spring snowmelt."
    ),

    # --- LOWER OWENS ---
    "lower_owens": RiverThresholds(
        green_floor=80,
        green_ceiling=280,
        yellow_floor=50,
        yellow_ceiling=300,
        rapid_change_threshold=50,
        notes="Wading dangerous above 300."
    ),

    # --- UPPER OWENS ---
    "upper_owens": RiverThresholds(
        green_floor=100,
        green_ceiling=140,
        yellow_floor=70,
        yellow_ceiling=200,
        rapid_change_threshold=30,
        notes="Small stream. Below Hot Creek confluence ~140."
    ),

    # --- HOT CREEK ---
    "hot_creek": RiverThresholds(
        green_floor=8,
        green_ceiling=50,
        yellow_floor=5,
        yellow_ceiling=70,
        rapid_change_threshold=10,
        notes="Tiny spring creek. Very technical. Fishable year-round."
    ),
}

# Dual-mode thresholds for rivers with both wade and drift boat fishing
WADE_THRESHOLDS = {
    "lower_sacramento": RiverThresholds(
        green_floor=3500,
        green_ceiling=5000,
        yellow_floor=3000,
        yellow_ceiling=6000,
        rapid_change_threshold=1000,
        notes="Wade fishing atypical on the Lower Sac but possible near banks below 5,000 cfs."
    ),
    "trinity": RiverThresholds(
        green_floor=300,
        green_ceiling=800,
        yellow_floor=200,
        yellow_ceiling=1000,
        rapid_change_threshold=300,
        notes="Wade fishing optimal 300–800 cfs. Comfortable wading 450–550 cfs."
    ),
}

DRIFT_THRESHOLDS = {
    "lower_sacramento": RiverThresholds(
        green_floor=4000,
        green_ceiling=8000,
        yellow_floor=3000,
        yellow_ceiling=12000,
        rapid_change_threshold=1500,
        notes="Drift boat optimal 4,000–8,000 cfs. Blown out above ~12,000."
    ),
    "trinity": RiverThresholds(
        green_floor=800,
        green_ceiling=2500,
        yellow_floor=500,
        yellow_ceiling=3500,
        rapid_change_threshold=500,
        notes="Drift boat optimal 800–2,500 cfs."
    ),
}


# All rivers with their configurations
RIVERS: Dict[str, RiverConfig] = {
    "lower_sacramento": RiverConfig(
        id="lower_sacramento",
        name="Lower Sacramento River",
        river_type="tailwater",
        latitude=40.5865,
        longitude=-122.4458,
        usgs_site_id="11370500",
        cdec_station_id="KWK",
        thresholds=RIVER_THRESHOLDS["lower_sacramento"],
        fishing_modes=["drift", "wade"],
        wade_thresholds=WADE_THRESHOLDS["lower_sacramento"],
        drift_thresholds=DRIFT_THRESHOLDS["lower_sacramento"],
        blown_out_cfs=12000,
    ),
    "upper_sacramento": RiverConfig(
        id="upper_sacramento",
        name="Upper Sacramento River",
        river_type="freestone",
        latitude=41.1350,
        longitude=-122.3550,
        usgs_site_id="11342000",
        cdec_station_id="DLT",
        thresholds=RIVER_THRESHOLDS["upper_sacramento"],
        blown_out_cfs=1200,
        dangerous_wade_cfs=600,
    ),
    "mccloud": RiverConfig(
        id="mccloud",
        name="McCloud River",
        river_type="spring_fed",
        latitude=41.0700,
        longitude=-122.1100,
        usgs_site_id="11367500",
        cdec_station_id=None,
        thresholds=RIVER_THRESHOLDS["mccloud"],
        dangerous_wade_cfs=900,
    ),
    "hat_creek": RiverConfig(
        id="hat_creek",
        name="Hat Creek",
        river_type="spring_creek",
        latitude=40.8400,
        longitude=-121.5100,
        usgs_site_id=None,
        cdec_station_id="HTH",
        thresholds=RIVER_THRESHOLDS["hat_creek"],
    ),
    "fall_river": RiverConfig(
        id="fall_river",
        name="Fall River",
        river_type="spring_creek",
        latitude=41.0200,
        longitude=-121.4400,
        usgs_site_id=None,
        cdec_station_id=None,
        thresholds=RIVER_THRESHOLDS["fall_river"],
        fishing_modes=["boat"],
    ),
    "pit_river": RiverConfig(
        id="pit_river",
        name="Pit River (Pit 3)",
        river_type="dam_controlled",
        latitude=41.0350,
        longitude=-121.9350,
        usgs_site_id="11359500",
        cdec_station_id="PIT",
        thresholds=RIVER_THRESHOLDS["pit_river"],
    ),
    "trinity": RiverConfig(
        id="trinity",
        name="Trinity River",
        river_type="tailwater",
        latitude=40.7300,
        longitude=-122.8100,
        usgs_site_id="11525500",
        cdec_station_id=None,
        thresholds=RIVER_THRESHOLDS["trinity"],
        fishing_modes=["wade", "drift"],
        wade_thresholds=WADE_THRESHOLDS["trinity"],
        drift_thresholds=DRIFT_THRESHOLDS["trinity"],
    ),
    "truckee": RiverConfig(
        id="truckee",
        name="Truckee River",
        river_type="dam_controlled",
        latitude=39.4300,
        longitude=-120.0300,
        usgs_site_id="10346000",
        cdec_station_id=None,
        thresholds=RIVER_THRESHOLDS["truckee"],
    ),
    "little_truckee": RiverConfig(
        id="little_truckee",
        name="Little Truckee River",
        river_type="tailwater",
        latitude=39.5500,
        longitude=-120.1600,
        usgs_site_id="10340500",
        cdec_station_id=None,
        thresholds=RIVER_THRESHOLDS["little_truckee"],
    ),
    "east_walker": RiverConfig(
        id="east_walker",
        name="East Walker River",
        river_type="dam_controlled",
        latitude=38.3300,
        longitude=-119.2200,
        usgs_site_id="10293000",
        cdec_station_id=None,
        thresholds=RIVER_THRESHOLDS["east_walker"],
        dangerous_wade_cfs=350,
    ),
    "lower_owens": RiverConfig(
        id="lower_owens",
        name="Lower Owens River",
        river_type="managed",
        latitude=37.3900,
        longitude=-118.5100,
        usgs_site_id="10251300",
        cdec_station_id=None,
        thresholds=RIVER_THRESHOLDS["lower_owens"],
        dangerous_wade_cfs=300,
    ),
    "upper_owens": RiverConfig(
        id="upper_owens",
        name="Upper Owens River",
        river_type="freestone",
        latitude=37.6200,
        longitude=-118.7500,
        usgs_site_id="10250800",
        cdec_station_id=None,
        thresholds=RIVER_THRESHOLDS["upper_owens"],
    ),
    "yuba": RiverConfig(
        id="yuba",
        name="Yuba River",
        river_type="freestone",
        latitude=39.5700,
        longitude=-120.9300,
        usgs_site_id="11413000",
        cdec_station_id=None,
        thresholds=RIVER_THRESHOLDS["yuba"],
    ),
    "north_fork_american": RiverConfig(
        id="north_fork_american",
        name="North Fork American River",
        river_type="freestone",
        latitude=38.9400,
        longitude=-120.7300,
        usgs_site_id="11427000",
        cdec_station_id=None,
        thresholds=RIVER_THRESHOLDS["north_fork_american"],
    ),
    "hot_creek": RiverConfig(
        id="hot_creek",
        name="Hot Creek",
        river_type="spring_creek",
        latitude=37.6600,
        longitude=-118.8300,
        usgs_site_id="10265150",
        cdec_station_id=None,
        thresholds=RIVER_THRESHOLDS["hot_creek"],
    ),
}
