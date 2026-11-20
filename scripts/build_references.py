"""Build deterministic road, zone, and simulated-sensor CSVs from an OSM snapshot."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "reference" / "osm" / "lome-roads.json"
OUTPUT_DIR = ROOT / "data" / "reference"
ROAD_CLASSES = ("trunk", "primary", "secondary", "tertiary")
DEFAULT_SPEED_KMH = {
    "trunk": 60.0,
    "primary": 50.0,
    "secondary": 40.0,
    "tertiary": 30.0,
}
CLASS_ORDER = {name: index for index, name in enumerate(ROAD_CLASSES)}
TARGET_AXES = (
    "13 janvier",
    "mono",
    "circulaire",
    "eyadema",
    "eyadéma",
    "aneho",
    "aného",
    "rn2",
    "port",
    "aeroport",
    "aéroport",
    "aflao",
    "grand marche",
    "grand marché",
)
ZONE_DEFINITIONS = (
    (
        "centre-ville",
        "Centre-ville",
        "centre",
        (6.1320, 1.2150),
        ("centre-ville", "city centre", "city center"),
    ),
    (
        "port",
        "Port autonome",
        "port",
        (6.1300, 1.2850),
        ("port autonome", "port de lomé", "port of lome"),
    ),
    (
        "aeroport",
        "Aéroport",
        "aeroport",
        (6.1650, 1.2540),
        ("aéroport", "aeroport", "airport"),
    ),
    (
        "marche",
        "Grand Marché",
        "marche",
        (6.1300, 1.2180),
        ("grand marché", "grand marche", "marché de lomé", "market"),
    ),
    ("aflao", "Frontière d'Aflao", "frontiere", (6.1400, 1.1700), ("aflao", "border")),
    (
        "peripherie",
        "Périphérie nord",
        "peripherie",
        (6.2050, 1.2150),
        ("périphérie", "peripherie", "suburb"),
    ),
)
EARTH_RADIUS_M = 6_371_008.8


def haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Compute geodesic distance in metres for (latitude, longitude) pairs."""
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * math.asin(min(1.0, math.sqrt(h)))


def parse_number(value: Any) -> float | None:
    """Parse the first numeric value from common OSM tag representations."""
    if value is None:
        return None
    match = re.search(r"\d+(?:[.,]\d+)?", str(value))
    return float(match.group(0).replace(",", ".")) if match else None


def speed_limit(tags: dict[str, Any], highway: str) -> float:
    """Read maxspeed, converting mph and selecting the lowest listed limit."""
    raw = tags.get("maxspeed")
    if raw:
        values = [parse_number(part) for part in str(raw).split(";")]
        values = [value for value in values if value is not None]
        if values:
            if "mph" in str(raw).lower():
                values = [value * 1.609344 for value in values]
            return min(values)
    return DEFAULT_SPEED_KMH[highway]


def way_geometry(element: dict[str, Any]) -> list[tuple[float, float]]:
    """Return an OSM way geometry as de-duplicated (lat, lon) pairs."""
    points: list[tuple[float, float]] = []
    for point in element.get("geometry", []):
        pair = (float(point["lat"]), float(point["lon"]))
        if not points or points[-1] != pair:
            points.append(pair)
    return points


def line_length(points: list[tuple[float, float]]) -> float:
    return sum(haversine(a, b) for a, b in zip(points, points[1:]))


def centroid(element: dict[str, Any]) -> tuple[float, float] | None:
    """Return node coordinates, an Overpass center, or an area vertex mean."""
    if "lat" in element and "lon" in element:
        return float(element["lat"]), float(element["lon"])
    center = element.get("center")
    points = element.get("geometry") or ([center] if center else [])
    if not points and element.get("members"):
        points = [
            point
            for member in element["members"]
            if member.get("role") != "inner"
            for point in member.get("geometry", [])
        ]
    if not points:
        return None
    return (
        sum(float(point["lat"]) for point in points) / len(points),
        sum(float(point["lon"]) for point in points) / len(points),
    )


def normalized_name(tags: dict[str, Any], way_id: int) -> str:
    return str(tags.get("name") or tags.get("ref") or f"Sans nom OSM {way_id}").strip()


def axis_priority(name: str) -> int:
    normalized = name.casefold()
    for index, term in enumerate(TARGET_AXES):
        if term.casefold() in normalized:
            return index
    return len(TARGET_AXES)


def select_ways(
    elements: list[dict[str, Any]], limit: int = 20
) -> list[dict[str, Any]]:
    """Select a stable sample with a cap per named road."""
    candidates = []
    for element in elements:
        tags = element.get("tags", {})
        highway = tags.get("highway")
        points = way_geometry(element)
        if highway not in ROAD_CLASSES or len(points) < 2:
            continue
        length = line_length(points)
        if length < 50:
            continue
        name = normalized_name(tags, int(element["id"]))
        candidates.append(
            {
                "element": element,
                "name": name,
                "priority": axis_priority(name),
                "class_order": CLASS_ORDER[highway],
                "length": length,
                "center": (
                    sum(point[0] for point in points) / len(points),
                    sum(point[1] for point in points) / len(points),
                ),
            }
        )
    candidates.sort(
        key=lambda item: (
            item["priority"],
            item["class_order"],
            item["name"].casefold(),
            int(item["element"]["id"]),
        )
    )
    selected: list[dict[str, Any]] = []
    name_counts: dict[str, int] = {}
    # First pass spreads across mapped road names, including target corridors.
    for item in candidates:
        key = item["name"].casefold()
        if name_counts.get(key, 0) == 0:
            selected.append(item)
            name_counts[key] = 1
            if len(selected) == limit:
                return selected
    # Fill remaining positions while limiting repeated pieces of one named road.
    for item in candidates:
        if item in selected:
            continue
        key = item["name"].casefold()
        if name_counts.get(key, 0) >= 3:
            continue
        selected.append(item)
        name_counts[key] = name_counts.get(key, 0) + 1
        if len(selected) == limit:
            break
    if len(selected) < 15:
        raise ValueError(
            f"Only {len(selected)} eligible OSM ways found; need at least 15. "
            "Check the snapshot extent or endpoint."
        )
    return selected


def interpolate(points: list[tuple[float, float]], ratio: float) -> tuple[float, float]:
    """Interpolate a point along a polyline by cumulative geodesic distance."""
    distances = [haversine(a, b) for a, b in zip(points, points[1:])]
    target = sum(distances) * ratio
    walked = 0.0
    for index, distance in enumerate(distances):
        if walked + distance >= target:
            fraction = (target - walked) / distance if distance else 0.0
            first, second = points[index], points[index + 1]
            return (
                first[0] + (second[0] - first[0]) * fraction,
                first[1] + (second[1] - first[1]) * fraction,
            )
        walked += distance
    return points[-1]


def wkt_line(points: list[tuple[float, float]]) -> str:
    coordinates = ", ".join(
        f"{lon:.7f} {lat:.7f}" for lat, lon in points
    )
    return f"LINESTRING ({coordinates})"


def wkt_box(lat: float, lon: float, side_m: float = 720.0) -> str:
    """Create an approximately square, metre-sized analytical footprint."""
    half_side_m = side_m / 2
    latitude_delta = half_side_m / 111_320
    longitude_delta = half_side_m / (111_320 * math.cos(math.radians(lat)))
    south, west = lat - latitude_delta, lon - longitude_delta
    north, east = lat + latitude_delta, lon + longitude_delta
    ring = ((west, south), (east, south), (east, north), (west, north), (west, south))
    return "POLYGON ((" + ", ".join(f"{x:.7f} {y:.7f}" for x, y in ring) + "))"


def build_zones(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Resolve six analytical zones to OSM POIs where possible."""
    zones = []
    for zone_id, label, zone_type, fallback, terms in ZONE_DEFINITIONS:
        match = None
        for element in elements:
            tags = element.get("tags", {})
            if zone_id == "aeroport" and tags.get("aeroway") != "aerodrome":
                continue
            if zone_id == "port" and not (
                tags.get("landuse") == "port" or tags.get("amenity") == "port"
            ):
                continue
            if zone_id in {"marche", "aflao"} and tags.get("amenity") != "marketplace":
                continue
            name_tags = ("name", "name:fr", "alt_name", "ref")
            haystack = " ".join(
                str(tags.get(key, "")) for key in name_tags
            ).casefold()
            if any(term.casefold() in haystack for term in terms):
                point = centroid(element)
                if point:
                    match = (element, point)
                    break
        element, point = match if match else (None, fallback)
        lat, lon = point
        zones.append(
            {
                "zone_id": zone_id,
                "zone_name": label,
                "zone_type": zone_type,
                "latitude": f"{lat:.7f}",
                "longitude": f"{lon:.7f}",
                "footprint_wkt": wkt_box(lat, lon),
                "footprint_method": "analytical_buffer_720m",
                "data_origin": "real" if element else "simulated",
                "source_osm_id": (
                    f"{element['type']}/{element['id']}"
                    if element
                    else "documented-footprint"
                ),
            }
        )
    return zones


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build(snapshot_path: Path) -> dict[str, int]:
    document = json.loads(snapshot_path.read_text(encoding="utf-8"))
    elements = document.get("elements", [])
    if not elements:
        raise ValueError("OSM snapshot contains no elements")
    selected = select_ways(elements)
    roads = []
    sensors = []
    for item in selected:
        element = item["element"]
        tags = element.get("tags", {})
        points = way_geometry(element)
        highway = tags["highway"]
        limit = speed_limit(tags, highway)
        way_id = int(element["id"])
        road_id = f"osm-way-{way_id}"
        lanes = parse_number(tags.get("lanes"))
        roads.append(
            {
                "troncon_id": road_id,
                "osm_way_ids": str(way_id),
                "axis_name": item["name"],
                "highway_class": highway,
                "lanes": int(lanes) if lanes is not None else "",
                "length_m": f"{item['length']:.1f}",
                "speed_limit_kmh": f"{limit:.1f}",
                "free_flow_speed_kmh": f"{min(80.0, limit * 0.9):.1f}",
                "geometry_wkt": wkt_line(points),
                "data_origin": "real",
            }
        )
        for index, ratio in enumerate((1 / 3, 2 / 3), start=1):
            lat, lon = interpolate(points, ratio)
            sensors.append(
                {
                    "capteur_id": f"sensor-{way_id}-{index}",
                    "troncon_id": road_id,
                    "sensor_type": "flow_speed",
                    "latitude": f"{lat:.7f}",
                    "longitude": f"{lon:.7f}",
                    "data_origin": "simulated",
                }
            )
    zones = build_zones(elements)
    write_csv(OUTPUT_DIR / "troncons.csv", roads)
    write_csv(OUTPUT_DIR / "capteurs.csv", sensors)
    write_csv(OUTPUT_DIR / "zones.csv", zones)
    return {"troncons": len(roads), "capteurs": len(sensors), "zones": len(zones)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()
    snapshot = args.input.resolve()
    if not snapshot.is_relative_to(ROOT):
        parser.error(f"input must be inside the D: project checkout: {ROOT}")
    try:
        result = build(snapshot)
        print(json.dumps({"status": "ok", **result}, ensure_ascii=False))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
