"""Download a small, documented OSM road snapshot for central Lomé."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "reference" / "osm" / "lome-roads.json"
DEFAULT_ENDPOINT = "https://overpass-api.de/api/interpreter"
BBOX = (6.08, 1.12, 6.25, 1.32)  # south, west, north, east
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
USER_AGENT = (
    "lome-smart-traffic/0.1 "
    "(+https://github.com/yannick-maya/Smart-trafic-streaming)"
)


def build_query() -> str:
    """Return one bounded Overpass query for roads and zone reference POIs."""
    south, west, north, east = BBOX
    bbox = f"{south},{west},{north},{east}"
    return f"""[out:json][timeout:90];
(
  way["highway"~"^(trunk|primary|secondary|tertiary)$"]({bbox});
  nwr["aeroway"="aerodrome"]({bbox});
  nwr["amenity"~"^(marketplace|port)$"]({bbox});
  nwr["landuse"="port"]({bbox});
  nwr["shop"="mall"]({bbox});
);
out body geom;"""


def fetch(endpoint: str, retries: int, retry_delay: int) -> dict:
    """Fetch once, retry transient errors, and return the Overpass JSON."""
    query = build_query().encode("utf-8")
    request = Request(
        endpoint,
        data=query,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
        method="POST",
    )
    for attempt in range(retries + 1):
        try:
            with urlopen(request, timeout=120) as response:
                body = response.read(MAX_RESPONSE_BYTES + 1)
                if len(body) > MAX_RESPONSE_BYTES:
                    raise ValueError(
                        f"OSM response exceeds {MAX_RESPONSE_BYTES} bytes"
                    )
                payload = json.loads(body)
                if not isinstance(payload.get("elements"), list):
                    raise ValueError("Overpass response has no elements array")
                return payload
        except HTTPError as exc:
            retryable = exc.code in {408, 429, 500, 502, 503, 504, 406}
            if not retryable or attempt >= retries:
                raise RuntimeError(f"Overpass returned HTTP {exc.code}") from exc
            delay = max(retry_delay, int(exc.headers.get("Retry-After", "0") or 0))
            if exc.code in {429, 406}:
                delay = max(30, delay)
            time.sleep(delay * (2**attempt))
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            if attempt >= retries:
                raise RuntimeError(f"Overpass request failed: {exc}") from exc
            time.sleep(retry_delay * (2**attempt))
    raise AssertionError("unreachable retry loop")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--retry-delay", type=int, default=5)
    args = parser.parse_args()

    output = args.output.resolve()
    if not output.is_relative_to(ROOT):
        parser.error(f"output must stay inside the D: project checkout: {ROOT}")
    if args.retries < 0 or args.retry_delay < 0:
        parser.error("retry counts and delay must be non-negative")

    try:
        response = fetch(args.endpoint, args.retries, args.retry_delay)
        document = {
            "snapshot": {
                "fetched_at_utc": datetime.now(timezone.utc)
                .replace(microsecond=0)
                .isoformat(),
                "osm_timestamp": response.get("osm3s", {}).get(
                    "timestamp_osm_base"
                ),
                "source": args.endpoint,
                "query": build_query(),
                "user_agent": USER_AGENT,
                "bbox_south_west_north_east": list(BBOX),
                "attribution": "© OpenStreetMap contributors (ODbL)",
            },
            "elements": response["elements"],
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(
            json.dumps(document, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output)
        print(
            json.dumps(
                {
                    "status": "ok",
                    "output": str(output),
                    "elements": len(response["elements"]),
                    "bytes": output.stat().st_size,
                    "osm_timestamp": document["snapshot"]["osm_timestamp"],
                },
                ensure_ascii=False,
            )
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
