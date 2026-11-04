# tripdays

A multi-leg trip itinerary should add up before you book anything.
`tripdays` takes a JSON list of stays — place, arrival date, departure
date — and reports:

- nights per stay, total nights, and total trip days;
- **gaps** between stays (unaccounted / travel days);
- **overlaps**, where the next stay starts before the previous one ends;
- **same-day moves**, where you change place without a buffer day;
- **day visits** (0 nights), which are easy to miscount.

Overlaps and same-day moves are warnings, not errors: the command
exits with status 1 when any warning is raised, and status 2 on an
unreadable or invalid itinerary, so it can be used in scripts.

## Install

```bash
pip install .
```

Requires Python 3.10+. No dependencies.

## Usage

Create an itinerary file:

```json
[
  {"place": "Lima", "arrive": "2027-01-01", "depart": "2027-01-04"},
  {"place": "Cusco", "arrive": "2027-01-05", "depart": "2027-01-09"}
]
```

Then run:

```bash
tripdays itinerary.json
# Place  Arrive  Depart  Nights
# Lima  2027-01-01  2027-01-04  3
# Cusco  2027-01-05  2027-01-09  4
# Total nights: 7
# Total trip days: 8
# Gap: 1 day(s) between Lima and Cusco (unaccounted / travel days)
```

Machine-readable output:

```bash
tripdays itinerary.json --json
```

## Library use

```python
from tripdays import Leg, assess_trip
from datetime import date

report = assess_trip([
    Leg("Lima", date(2027, 1, 1), date(2027, 1, 4)),
])
print(report.format())
```

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## License

MIT
