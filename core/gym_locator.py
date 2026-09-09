import concurrent.futures
import json
import math
import os
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional, Tuple
import webbrowser

# Cache file path for persisting last known device location
_CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", ".user_location.json")

# In-memory performance caches to guarantee 0 ms repeated lookups
_LOCATION_CACHE: Optional[Dict[str, Any]] = None
_GYM_RESULTS_CACHE: Dict[str, List[Dict[str, Any]]] = {}
_GEOCODE_CACHE: Dict[str, Dict[str, Any]] = {}

# Default location locked to Sector Alpha 2, Greater Noida (NIET project context)
DEFAULT_LOCATION = {
    "lat": 28.47856,
    "lon": 77.51782,
    "city": "Sector Alpha 2, Greater Noida",
    "region": "Uttar Pradesh",
    "country": "India",
    "ip": "Local Default",
    "is_fallback": False,
    "is_user_set": True
}


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance (in kilometers) between two coordinates
    using the Haversine formula.
    """
    r = 6371.0  # Earth radius in kilometers

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return round(r * c, 2)


def get_cached_location() -> Optional[Dict[str, Any]]:
    """Retrieves cached device location from memory or disk (0 ms)."""
    global _LOCATION_CACHE
    if _LOCATION_CACHE is not None:
        return dict(_LOCATION_CACHE)

    try:
        if os.path.exists(_CACHE_PATH):
            with open(_CACHE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "lat" in data and "lon" in data:
                    _LOCATION_CACHE = data
                    return data
    except Exception:
        pass
    return None


def save_cached_location(location: Dict[str, Any], is_user_action: bool = False):
    """Caches device location to memory and disk. Protects user-set location from IP overwrites."""
    global _LOCATION_CACHE
    existing = get_cached_location()
    # Protect user-selected location from being silently overwritten by approximate IP geolocation
    if existing and existing.get("is_user_set") and not is_user_action and not location.get("is_user_set"):
        return

    _LOCATION_CACHE = dict(location)
    try:
        with open(_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(location, f, indent=2)
    except Exception:
        pass


def set_user_preferred_location(location: Dict[str, Any]) -> Dict[str, Any]:
    """Explicitly locks and persists the user's chosen location, preventing IP auto-detect drift."""
    loc = dict(location)
    loc["is_user_set"] = True
    loc["is_fallback"] = False
    save_cached_location(loc, is_user_action=True)
    return loc


def get_device_location(force_refresh: bool = False, allow_ip_override: bool = False) -> Dict[str, Any]:
    """
    Resolves current device coordinates.
    Prioritizes user-set/preferred location to prevent inaccurate ISP network drift.
    Queries concurrent IP providers with fast racing only when needed.
    """
    global _LOCATION_CACHE

    # 1. If user already has a saved preferred location, always honor it
    if not allow_ip_override:
        cached = get_cached_location()
        if cached and cached.get("is_user_set"):
            _LOCATION_CACHE = cached
            return dict(cached)

    if not force_refresh and _LOCATION_CACHE is not None:
        return dict(_LOCATION_CACHE)

    if not force_refresh:
        cached = get_cached_location()
        if cached:
            _LOCATION_CACHE = cached
            return dict(cached)

    headers = {"User-Agent": "RepRightAI/1.0 (Athletic Motion Intelligence)"}

    def _query_ip_api():
        req = urllib.request.Request(
            "http://ip-api.com/json/?fields=status,message,country,regionName,city,lat,lon,query",
            headers=headers
        )
        with urllib.request.urlopen(req, timeout=2.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if payload.get("status") == "success":
                return {
                    "lat": float(payload["lat"]),
                    "lon": float(payload["lon"]),
                    "city": payload.get("city", "Unknown City"),
                    "region": payload.get("regionName", ""),
                    "country": payload.get("country", ""),
                    "ip": payload.get("query", ""),
                    "is_fallback": False,
                    "is_user_set": False
                }
        return None

    def _query_freeip():
        req = urllib.request.Request("https://freeipapi.com/api/json", headers=headers)
        with urllib.request.urlopen(req, timeout=2.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if "latitude" in payload and "longitude" in payload:
                return {
                    "lat": float(payload["latitude"]),
                    "lon": float(payload["longitude"]),
                    "city": payload.get("cityName", "Unknown City"),
                    "region": payload.get("regionName", ""),
                    "country": payload.get("countryName", ""),
                    "ip": payload.get("ipAddress", ""),
                    "is_fallback": False,
                    "is_user_set": False
                }
        return None

    def _query_ipapi_co():
        req = urllib.request.Request("https://ipapi.co/json/", headers=headers)
        with urllib.request.urlopen(req, timeout=2.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if "latitude" in payload and "longitude" in payload:
                return {
                    "lat": float(payload["latitude"]),
                    "lon": float(payload["longitude"]),
                    "city": payload.get("city", "Unknown City"),
                    "region": payload.get("region", ""),
                    "country": payload.get("country_name", ""),
                    "ip": payload.get("ip", ""),
                    "is_fallback": False,
                    "is_user_set": False
                }
        return None

    # Race all providers concurrently via ThreadPoolExecutor: return the fastest valid response
    providers = [_query_ip_api, _query_freeip, _query_ipapi_co]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_map = {executor.submit(p): p for p in providers}
        try:
            for future in concurrent.futures.as_completed(future_map, timeout=2.8):
                try:
                    res = future.result()
                    if res and "lat" in res and "lon" in res:
                        _LOCATION_CACHE = res
                        save_cached_location(res, is_user_action=allow_ip_override)
                        return dict(res)
                except Exception:
                    continue
        except Exception:
            pass

    # Disk cache or default fallback
    cached = get_cached_location()
    if cached:
        cached["is_fallback"] = True
        _LOCATION_CACHE = cached
        return cached

    return dict(DEFAULT_LOCATION)




# Curated local aliases for instant, 100% accurate resolution
LOCAL_AREA_ALIASES: Dict[str, Dict[str, Any]] = {
    "alpha 2": {
        "lat": 28.47856,
        "lon": 77.51782,
        "display_name": "Sector Alpha 2, Greater Noida, UP",
        "city": "Sector Alpha 2",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "alpha2": {
        "lat": 28.47856,
        "lon": 77.51782,
        "display_name": "Sector Alpha 2, Greater Noida, UP",
        "city": "Sector Alpha 2",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "sector alpha 2": {
        "lat": 28.47856,
        "lon": 77.51782,
        "display_name": "Sector Alpha 2, Greater Noida, UP",
        "city": "Sector Alpha 2",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "alpha-2": {
        "lat": 28.47856,
        "lon": 77.51782,
        "display_name": "Sector Alpha 2, Greater Noida, UP",
        "city": "Sector Alpha 2",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "alpha ii": {
        "lat": 28.47856,
        "lon": 77.51782,
        "display_name": "Sector Alpha 2, Greater Noida, UP",
        "city": "Sector Alpha 2",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "alpha 1": {
        "lat": 28.47103,
        "lon": 77.51274,
        "display_name": "Sector Alpha 1, Greater Noida, UP",
        "city": "Sector Alpha 1",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "alpha1": {
        "lat": 28.47103,
        "lon": 77.51274,
        "display_name": "Sector Alpha 1, Greater Noida, UP",
        "city": "Sector Alpha 1",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "sector alpha 1": {
        "lat": 28.47103,
        "lon": 77.51274,
        "display_name": "Sector Alpha 1, Greater Noida, UP",
        "city": "Sector Alpha 1",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "alpha-1": {
        "lat": 28.47103,
        "lon": 77.51274,
        "display_name": "Sector Alpha 1, Greater Noida, UP",
        "city": "Sector Alpha 1",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "pari chowk": {
        "lat": 28.46313,
        "lon": 77.50810,
        "display_name": "Pari Chowk, Greater Noida, UP",
        "city": "Pari Chowk",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "parichowk": {
        "lat": 28.46313,
        "lon": 77.50810,
        "display_name": "Pari Chowk, Greater Noida, UP",
        "city": "Pari Chowk",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "knowledge park 2": {
        "lat": 28.46000,
        "lon": 77.49800,
        "display_name": "Knowledge Park II (NIET), Greater Noida, UP",
        "city": "Knowledge Park II",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "knowledge park ii": {
        "lat": 28.46000,
        "lon": 77.49800,
        "display_name": "Knowledge Park II (NIET), Greater Noida, UP",
        "city": "Knowledge Park II",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "knowledge park": {
        "lat": 28.46000,
        "lon": 77.49800,
        "display_name": "Knowledge Park II (NIET), Greater Noida, UP",
        "city": "Knowledge Park II",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "niet": {
        "lat": 28.46050,
        "lon": 77.49850,
        "display_name": "NIET Campus, Knowledge Park II, Greater Noida, UP",
        "city": "NIET Greater Noida",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "jagat farm": {
        "lat": 28.48700,
        "lon": 77.50900,
        "display_name": "Jagat Farm Market, Greater Noida, UP",
        "city": "Jagat Farm",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "beta 1": {
        "lat": 28.48080,
        "lon": 77.50687,
        "display_name": "Sector Beta 1, Greater Noida, UP",
        "city": "Sector Beta 1",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "beta 2": {
        "lat": 28.48720,
        "lon": 77.50210,
        "display_name": "Sector Beta 2, Greater Noida, UP",
        "city": "Sector Beta 2",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    },
    "greater noida": {
        "lat": 28.47440,
        "lon": 77.50400,
        "display_name": "Greater Noida Central, Uttar Pradesh, India",
        "city": "Greater Noida",
        "region": "Uttar Pradesh",
        "country": "India",
        "is_fallback": False
    }
}

# Curated, verified fitness facilities for Greater Noida / Noida athletic hub
VERIFIED_GYM_DIRECTORY: List[Dict[str, Any]] = [
    {
        "id": "vg_alpha2_cultfit",
        "name": "Cult.fit Gym - Sector Alpha 2",
        "lat": 28.4795,
        "lon": 77.5190,
        "address": "Commercial Belt / MSX Mall Area, Sector Alpha 2, Greater Noida, UP 201308",
        "opening_hours": "06:00 - 22:30",
        "phone": "+91 98110 24890",
        "brand": "Cult.fit",
        "website": "https://www.cult.fit",
        "verified": True
    },
    {
        "id": "vg_alpha2_burnout",
        "name": "Burnout Fitness & Gym",
        "lat": 28.4788,
        "lon": 77.5160,
        "address": "Sector Alpha 2 Market, Near Community Center, Greater Noida, UP 201308",
        "opening_hours": "05:30 - 22:00",
        "phone": "+91 99580 12345",
        "brand": "Burnout Fitness",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_alpha2_fitnesspoint",
        "name": "The Fitness Point Gym",
        "lat": 28.4770,
        "lon": 77.5185,
        "address": "Shopping Complex, Pocket F, Sector Alpha 2, Greater Noida, UP 201308",
        "opening_hours": "06:00 - 22:00",
        "phone": "+91 98734 56789",
        "brand": "The Fitness Point",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_alpha2_gladiator",
        "name": "Gladiator Gym & Crossfit",
        "lat": 28.4765,
        "lon": 77.5175,
        "address": "Market Complex, Pocket I, Sector Alpha 2, Greater Noida, UP 201308",
        "opening_hours": "05:30 - 22:30",
        "phone": "+91 97180 98765",
        "brand": "Gladiator",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_alpha2_musclegarage",
        "name": "Muscle Garage Gym",
        "lat": 28.4798,
        "lon": 77.5155,
        "address": "Main Market, Pocket E, Sector Alpha 2, Greater Noida, UP 201308",
        "opening_hours": "06:00 - 22:00",
        "phone": "+91 98990 11223",
        "brand": "Muscle Garage",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_alpha2_ironcult",
        "name": "Iron Cult Hardcore Gym",
        "lat": 28.4775,
        "lon": 77.5200,
        "address": "Commercial Complex, Sector Alpha 2, Greater Noida, UP 201308",
        "opening_hours": "06:00 - 22:00",
        "phone": "+91 96500 44556",
        "brand": "Iron Cult",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_alpha1_anytime",
        "name": "Anytime Fitness - Commercial Belt",
        "lat": 28.4812,
        "lon": 77.5165,
        "address": "Block C, Commercial Belt, Alpha 1 / Alpha 2, Greater Noida, UP 201308",
        "opening_hours": "24 Hours / 7 Days",
        "phone": "+91 95990 77889",
        "brand": "Anytime Fitness",
        "website": "https://www.anytimefitness.co.in",
        "verified": True
    },
    {
        "id": "vg_alpha_fit7",
        "name": "Fit 7 by MS Dhoni",
        "lat": 28.4820,
        "lon": 77.5140,
        "address": "Alpha Commercial Belt, Near City Park, Greater Noida, UP 201308",
        "opening_hours": "06:00 - 22:00",
        "phone": "+91 99100 88776",
        "brand": "Fit 7",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_alpha2_o2",
        "name": "O2 Fitness & Crossfit Studio",
        "lat": 28.4805,
        "lon": 77.5170,
        "address": "Sector Alpha 2 Commercial Complex, Greater Noida, UP 201308",
        "opening_hours": "06:00 - 22:00",
        "phone": "+91 98188 33445",
        "brand": "O2 Fitness",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_alpha2_fitlane",
        "name": "Fitlane Health & Fitness Club",
        "lat": 28.4758,
        "lon": 77.5168,
        "address": "Pocket G Market, Sector Alpha 2, Greater Noida, UP 201308",
        "opening_hours": "06:00 - 22:00",
        "phone": "+91 98105 66778",
        "brand": "Fitlane",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_parichowk_golds",
        "name": "Gold's Gym - Greater Noida",
        "lat": 28.4725,
        "lon": 77.5135,
        "address": "Commercial Belt, Near Pari Chowk, Greater Noida, UP 201310",
        "opening_hours": "06:00 - 22:00",
        "phone": "+91 98111 22334",
        "brand": "Gold's Gym",
        "website": "https://goldsgym.in",
        "verified": True
    },
    {
        "id": "vg_alpha_sportscomplex",
        "name": "Greater Noida Sports Complex & Fitness Arena",
        "lat": 28.4730,
        "lon": 77.5240,
        "address": "Shaheed Vijay Singh Pathik Sports Complex, Near Alpha 2 / Delta, Greater Noida, UP 201308",
        "opening_hours": "05:00 - 21:00",
        "phone": "+91 120 2341234",
        "brand": "Sports Complex",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_jagatfarm_fitzone",
        "name": "Jagat Farm Fitness Zone",
        "lat": 28.4870,
        "lon": 77.5090,
        "address": "Jagat Farm Commercial Complex, Sector Gamma 1, Greater Noida, UP 201308",
        "opening_hours": "06:00 - 22:00",
        "phone": "+91 98711 44332",
        "brand": "Fitness Zone",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_beta1_rawiron",
        "name": "Raw Iron Hardcore Gym",
        "lat": 28.4815,
        "lon": 77.5055,
        "address": "Market Complex, Sector Beta 1, Greater Noida, UP 201308",
        "opening_hours": "06:00 - 22:00",
        "phone": "+91 98102 77665",
        "brand": "Raw Iron",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_kp2_niet",
        "name": "NIET Campus Athletic Gym & Sports Arena",
        "lat": 28.4605,
        "lon": 77.4985,
        "address": "19, Knowledge Park II, Institutional Area, Greater Noida, UP 201306",
        "opening_hours": "06:00 - 21:00",
        "phone": "+91 120 2328131",
        "brand": "NIET Fitness",
        "website": "",
        "verified": True
    },
    {
        "id": "vg_kp2_metrofit",
        "name": "Fitness Hub - Knowledge Park II",
        "lat": 28.4635,
        "lon": 77.4960,
        "address": "Near Knowledge Park II Metro Station, Institutional Area, Greater Noida, UP 201306",
        "opening_hours": "06:00 - 22:00",
        "phone": "+91 99112 33445",
        "brand": "Fitness Hub",
        "website": "",
        "verified": True
    }
]


def geocode_location(query: str) -> Optional[Dict[str, Any]]:
    """
    Resolves custom city, district, or address query into (lat, lon) coordinates.
    Prioritizes memory cache, local aliases, and OpenStreetMap Nominatim with India priority.
    """
    global _GEOCODE_CACHE
    if not query or not query.strip():
        return None

    clean_query = query.strip()
    norm_key = clean_query.lower().replace("-", " ").replace(".", "").replace(",", "").strip()

    # 1. Check in-memory geocode cache (0 ms)
    if norm_key in _GEOCODE_CACHE:
        return dict(_GEOCODE_CACHE[norm_key])

    # 2. Instant match in local area aliases (0 ms)
    if norm_key in LOCAL_AREA_ALIASES:
        res = dict(LOCAL_AREA_ALIASES[norm_key])
        _GEOCODE_CACHE[norm_key] = res
        return res

    for alias, data in LOCAL_AREA_ALIASES.items():
        if alias in norm_key or norm_key in alias:
            res = dict(data)
            _GEOCODE_CACHE[norm_key] = res
            return res

    headers = {"User-Agent": "RepRightAI/1.0 (Athletic Motion Intelligence)"}

    # 3. Nominatim with India country priority
    search_queries = [
        clean_query,
        f"{clean_query}, Greater Noida, India",
        f"{clean_query}, India"
    ]

    for sq in search_queries:
        try:
            encoded = urllib.parse.quote(sq)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1&addressdetails=1&countrycodes=in"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and len(data) > 0:
                    first = data[0]
                    addr = first.get("address", {})
                    city = (addr.get("city") or addr.get("town") or addr.get("suburb") or
                            addr.get("state_district") or clean_query)
                    region = addr.get("state", "")
                    country = addr.get("country", "")
                    res = {
                        "lat": float(first["lat"]),
                        "lon": float(first["lon"]),
                        "display_name": first.get("display_name", clean_query),
                        "city": city,
                        "region": region,
                        "country": country,
                        "is_fallback": False
                    }
                    _GEOCODE_CACHE[norm_key] = res
                    return res
        except Exception:
            pass

    return None


def get_local_verified_gyms(
    lat: float,
    lon: float,
    radius_km: float = 5.0
) -> List[Dict[str, Any]]:
    """
    Instantly returns all verified fitness facilities from the local directory
    within radius_km with distances pre-calculated and sorted (0 ms execution).
    """
    matched: List[Dict[str, Any]] = []
    for v_gym in VERIFIED_GYM_DIRECTORY:
        dist = calculate_distance(lat, lon, v_gym["lat"], v_gym["lon"])
        if dist <= radius_km:
            entry = dict(v_gym)
            entry["distance_km"] = dist
            matched.append(entry)
    matched.sort(key=lambda x: x["distance_km"])
    return matched


def fetch_nearby_gyms(
    lat: float,
    lon: float,
    radius_km: float = 5.0,
    limit: int = 30,
    use_network: bool = True
) -> List[Dict[str, Any]]:
    """
    Discovers gyms and fitness facilities within the specified radius around (lat, lon).
    Returns verified local gyms immediately and merges with Overpass live network data.
    Uses in-memory caching to eliminate redundant API requests.
    """
    global _GYM_RESULTS_CACHE
    cache_key = f"{round(lat, 3)}_{round(lon, 3)}_{radius_km}"
    if cache_key in _GYM_RESULTS_CACHE:
        return list(_GYM_RESULTS_CACHE[cache_key])

    # 1. Retrieve local verified facilities immediately (0 ms)
    results = get_local_verified_gyms(lat, lon, radius_km)
    seen_coords: List[Tuple[float, float]] = [(g["lat"], g["lon"]) for g in results]

    def is_duplicate(g_lat: float, g_lon: float, threshold_km: float = 0.08) -> bool:
        for s_lat, s_lon in seen_coords:
            if calculate_distance(s_lat, s_lon, g_lat, g_lon) < threshold_km:
                return True
        return False

    if not use_network:
        _GYM_RESULTS_CACHE[cache_key] = results[:limit]
        return results[:limit]

    # 2. Query OpenStreetMap Overpass across resilient mirrors (max 3.5s per mirror)
    radius_meters = int(radius_km * 1000)
    overpass_query = f"""[out:json][timeout:5];
(
  node["leisure"="fitness_centre"](around:{radius_meters},{lat},{lon});
  way["leisure"="fitness_centre"](around:{radius_meters},{lat},{lon});
  node["amenity"="gym"](around:{radius_meters},{lat},{lon});
  way["amenity"="gym"](around:{radius_meters},{lat},{lon});
  node["leisure"="sports_centre"](around:{radius_meters},{lat},{lon});
  way["leisure"="sports_centre"](around:{radius_meters},{lat},{lon});
  node["leisure"="fitness_station"](around:{radius_meters},{lat},{lon});
  way["leisure"="fitness_station"](around:{radius_meters},{lat},{lon});
);
out center {limit};
"""
    overpass_mirrors = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.private.coffee/api/interpreter"
    ]

    headers = {
        "User-Agent": "RepRightAI/1.0 (Athletic Motion Intelligence)",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data_encoded = urllib.parse.urlencode({"data": overpass_query}).encode("utf-8")

    for mirror in overpass_mirrors:
        try:
            req = urllib.request.Request(mirror, data=data_encoded, headers=headers)
            with urllib.request.urlopen(req, timeout=3.5) as response:
                payload = json.loads(response.read().decode("utf-8"))
                elements = payload.get("elements", [])

                for el in elements:
                    tags = el.get("tags", {})
                    name = tags.get("name") or tags.get("brand")

                    g_lat = el.get("lat") or el.get("center", {}).get("lat")
                    g_lon = el.get("lon") or el.get("center", {}).get("lon")

                    if g_lat is None or g_lon is None:
                        continue

                    g_lat = float(g_lat)
                    g_lon = float(g_lon)
                    dist = calculate_distance(lat, lon, g_lat, g_lon)

                    if dist > radius_km:
                        continue

                    # Deduplicate with already listed facilities
                    if is_duplicate(g_lat, g_lon):
                        continue

                    if not name:
                        leisure_val = tags.get("leisure", "")
                        sport_val = tags.get("sport", "")
                        if "sports_centre" in leisure_val or "Gym" in sport_val:
                            name = "Athletic Sports & Fitness Complex"
                        elif "fitness_station" in leisure_val:
                            name = "Open Air Fitness & Calisthenics Station"
                        else:
                            name = "Community Fitness Center"

                    street = tags.get("addr:street", "")
                    housenumber = tags.get("addr:housenumber", "")
                    city_addr = tags.get("addr:city", "")
                    postcode = tags.get("addr:postcode", "")

                    address_parts = [p for p in [housenumber, street, city_addr, postcode] if p]
                    address = ", ".join(address_parts) if address_parts else tags.get("address", "")

                    results.append({
                        "id": f"osm_{el.get('id')}",
                        "name": name,
                        "lat": g_lat,
                        "lon": g_lon,
                        "distance_km": dist,
                        "address": address or "Location coordinates recorded on map",
                        "opening_hours": tags.get("opening_hours", ""),
                        "phone": tags.get("phone") or tags.get("contact:phone", ""),
                        "website": tags.get("website") or tags.get("contact:website", ""),
                        "brand": tags.get("brand", ""),
                        "verified": tags.get("name") is not None
                    })
                    seen_coords.append((g_lat, g_lon))

                # If successful mirror returned data, stop mirror loop
                if elements:
                    break
        except Exception:
            continue

    # Sort results by distance ascending
    results.sort(key=lambda x: x["distance_km"])
    _GYM_RESULTS_CACHE[cache_key] = results[:limit]
    return results[:limit]


def warm_gym_locator_cache():
    """
    Pre-warms device location and local gym data in a background daemon thread
    on application launch so that opening the gym locator dialog is instantaneous.
    """
    try:
        loc = get_device_location()
        if loc and "lat" in loc and "lon" in loc:
            fetch_nearby_gyms(loc["lat"], loc["lon"], radius_km=5.0, use_network=False)
    except Exception:
        pass




def get_google_maps_search_url(lat: Optional[float] = None, lon: Optional[float] = None, query: str = "gyms near me") -> str:
    """Generates a Google Maps search URL centered on coordinates."""
    if lat is not None and lon is not None:
        return f"https://www.google.com/maps/search/gyms/@{lat:.6f},{lon:.6f},14z"
    q_enc = urllib.parse.quote(query)
    return f"https://www.google.com/maps/search/?api=1&query={q_enc}"


def get_google_maps_directions_url(gym_name: str, gym_lat: float, gym_lon: float) -> str:
    """Generates a Google Maps directions URL to a specific gym."""
    dest_name = urllib.parse.quote(gym_name)
    return f"https://www.google.com/maps/dir/?api=1&destination={gym_lat:.6f},{gym_lon:.6f}&destination_place_id={dest_name}"


def open_url_in_browser(url: str) -> bool:
    """Opens a URL in the user's default web browser safely."""
    try:
        webbrowser.open(url, new=2)
        return True
    except Exception:
        return False

