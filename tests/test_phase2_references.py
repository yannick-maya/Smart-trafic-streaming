"""Offline integrity checks for the committed phase 2 reference data."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unittest
from pathlib import Path

from scripts import build_references

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = ROOT / "data" / "reference"
SCHEMA_DIR = ROOT / "simulator" / "schemas"
SNAPSHOT = REFERENCE_DIR / "osm" / "lome-roads.json"
COORDINATE = re.compile(r"\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*")


def read_csv(name: str) -> list[dict[str, str]]:
    with (REFERENCE_DIR / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def parse_wkt_coordinates(wkt: str, geometry_type: str) -> list[tuple[float, float]]:
    prefix = f"{geometry_type} ("
    if not wkt.startswith(prefix) or not wkt.endswith(")"):
        raise AssertionError(f"unexpected {geometry_type} WKT: {wkt[:50]}")
    text = wkt[len(prefix) : -1]
    if geometry_type == "POLYGON":
        if not text.startswith("(") or not text.endswith(")"):
            raise AssertionError("polygon must contain one explicitly closed ring")
        text = text[1:-1]
    points = []
    for pair in text.split(","):
        match = COORDINATE.fullmatch(pair)
        if match is None:
            raise AssertionError(f"invalid WKT coordinate pair: {pair}")
        points.append((float(match.group(1)), float(match.group(2))))
    return points


def point_on_polyline(
    point: tuple[float, float], line: list[tuple[float, float]]
) -> bool:
    """Check that a sensor point lies on one WKT line segment, in degrees."""
    x, y = point
    for first, second in zip(line, line[1:]):
        dx, dy = second[0] - first[0], second[1] - first[1]
        length_squared = dx * dx + dy * dy
        if length_squared == 0:
            continue
        projection = ((x - first[0]) * dx + (y - first[1]) * dy) / length_squared
        ratio = max(0.0, min(1.0, projection))
        projected = (first[0] + ratio * dx, first[1] + ratio * dy)
        if (x - projected[0]) ** 2 + (y - projected[1]) ** 2 <= 1e-12:
            return True
    return False


class ReferenceDataTests(unittest.TestCase):
    def test_expected_reference_counts_and_foreign_keys(self) -> None:
        roads = read_csv("troncons.csv")
        sensors = read_csv("capteurs.csv")
        zones = read_csv("zones.csv")
        road_ids = {row["troncon_id"] for row in roads}
        self.assertGreaterEqual(len(roads), 15)
        self.assertLessEqual(len(roads), 25)
        self.assertGreaterEqual(len(sensors), 30)
        self.assertLessEqual(len(sensors), 60)
        self.assertEqual(len(road_ids), len(roads))
        self.assertEqual(len({row["capteur_id"] for row in sensors}), len(sensors))
        self.assertTrue(all(sensor["troncon_id"] in road_ids for sensor in sensors))
        snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        osm_ids = {
            (element["type"], str(element["id"]))
            for element in snapshot["elements"]
        }
        for road in roads:
            for way_id in road["osm_way_ids"].split(";"):
                self.assertIn(("way", way_id), osm_ids)
        for zone in zones:
            if zone["source_osm_id"] != "documented-footprint":
                self.assertIn(tuple(zone["source_osm_id"].split("/")), osm_ids)
        line_by_road = {
            row["troncon_id"]: parse_wkt_coordinates(row["geometry_wkt"], "LINESTRING")
            for row in roads
        }
        for sensor in sensors:
            self.assertTrue(
                point_on_polyline(
                    (float(sensor["longitude"]), float(sensor["latitude"])),
                    line_by_road[sensor["troncon_id"]],
                )
            )
        self.assertEqual(len(zones), 6)
        self.assertEqual(len({zone["zone_id"] for zone in zones}), len(zones))

    def test_geometries_are_well_formed_and_within_lome_snapshot_extent(self) -> None:
        for road in read_csv("troncons.csv"):
            coordinates = parse_wkt_coordinates(road["geometry_wkt"], "LINESTRING")
            self.assertGreaterEqual(len(coordinates), 2)
            self.assertGreater(float(road["length_m"]), 0)
            self.assertTrue(
                any(
                    1.12 <= lon <= 1.32 and 6.08 <= lat <= 6.25
                    for lon, lat in coordinates
                )
            )
            self.assertTrue(
                all(
                    1.10 <= lon <= 1.34 and 6.06 <= lat <= 6.27
                    for lon, lat in coordinates
                )
            )
        for zone in read_csv("zones.csv"):
            coordinates = parse_wkt_coordinates(zone["footprint_wkt"], "POLYGON")
            self.assertEqual(coordinates[0], coordinates[-1])
            self.assertEqual(len(coordinates), 5)
            longitudes = [point[0] for point in coordinates]
            latitudes = [point[1] for point in coordinates]
            side_latitude = build_references.haversine(
                (min(latitudes), min(longitudes)),
                (max(latitudes), min(longitudes)),
            )
            self.assertAlmostEqual(side_latitude, 720, delta=2)
            self.assertIn(zone["data_origin"], {"real", "simulated"})
            self.assertEqual(zone["footprint_method"], "analytical_buffer_720m")
            if zone["source_osm_id"] == "documented-footprint":
                self.assertEqual(zone["data_origin"], "simulated")
            else:
                self.assertEqual(zone["data_origin"], "real")

    def test_origins_and_schema_examples_are_explicit(self) -> None:
        self.assertTrue(
            all(row["data_origin"] == "real" for row in read_csv("troncons.csv"))
        )
        self.assertTrue(
            all(row["data_origin"] == "simulated" for row in read_csv("capteurs.csv"))
        )
        schemas = sorted(SCHEMA_DIR.glob("*.schema.json"))
        self.assertEqual(len(schemas), 5)
        for path in schemas:
            schema = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                schema["$schema"], "https://json-schema.org/draft/2020-12/schema"
            )
            self.assertEqual(schema["type"], "object")
            self.assertFalse(schema["additionalProperties"])
            self.assertIn("data_origin", schema["required"])
            self.assertIn("data_origin", schema["properties"])
            self.assertTrue(schema.get("examples"))
            for example in schema["examples"]:
                self.assertTrue(set(schema["required"]).issubset(example))
                self.assertLessEqual(set(example), set(schema["properties"]))
                for name, value in example.items():
                    prop = schema["properties"][name]
                    if "const" in prop:
                        self.assertEqual(value, prop["const"])
                    if "enum" in prop:
                        self.assertIn(value, prop["enum"])

    def test_offline_generation_is_byte_deterministic(self) -> None:
        paths = [
            REFERENCE_DIR / name
            for name in ("troncons.csv", "capteurs.csv", "zones.csv")
        ]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        counts = build_references.build(SNAPSHOT)
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        self.assertEqual(before, after)
        self.assertEqual(counts, {"troncons": 20, "capteurs": 40, "zones": 6})

    def test_snapshot_is_small_attributed_and_self_describing(self) -> None:
        document = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        self.assertLess(SNAPSHOT.stat().st_size, 3 * 1024 * 1024)
        self.assertEqual(len(document["elements"]), 1245)
        self.assertIn(
            "© OpenStreetMap contributors (ODbL)", document["snapshot"]["attribution"]
        )
        self.assertTrue(document["snapshot"]["osm_timestamp"])
        self.assertTrue(document["snapshot"]["query"])


if __name__ == "__main__":
    unittest.main()
