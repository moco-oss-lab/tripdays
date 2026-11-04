"""Command line interface for tripdays."""

from __future__ import annotations

import argparse
import json
import sys

from . import assess_trip, parse_leg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tripdays",
        description="Check a multi-leg trip itinerary: nights, gaps, overlaps.",
    )
    parser.add_argument("itinerary", help="JSON file with a list of legs")
    parser.add_argument("--json", action="store_true",
                        help="print machine-readable JSON instead of a table")
    args = parser.parse_args(argv)

    try:
        with open(args.itinerary, encoding="utf-8") as fh:
            raw = json.load(fh)
        if not isinstance(raw, list):
            raise ValueError("itinerary must be a JSON list of legs")
        report = assess_trip([parse_leg(item) for item in raw])
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"tripdays: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({
            "stays": [
                {"place": s.leg.place, "arrive": str(s.leg.arrive),
                 "depart": str(s.leg.depart), "nights": s.nights}
                for s in report.stays
            ],
            "gaps": [vars(g) for g in report.gaps],
            "warnings": report.warnings,
            "total_nights": report.total_nights,
            "total_days": report.total_days,
        }, indent=2, ensure_ascii=False))
    else:
        print(report.format())
    return 1 if report.warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
