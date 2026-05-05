from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import get_events


def assert_ok(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    all_events = get_events(start_date=None, end_date=None, region=None, event_type=None)
    assert_ok(len(all_events) > 0, "Expected /api/events to return at least one event")
    assert_ok(
        all("sample" not in event["title"].lower() and "sample" not in event["description"].lower() for event in all_events),
        "Expected real event labels without sample placeholders",
    )

    hk_closed_events = get_events(
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 31),
        region="HK",
        event_type="market_holiday",
    )
    assert_ok(any(event["date"] == "2026-05-01" and event["title"] == "HK Closed" for event in hk_closed_events),
        "Expected HK holiday closures to be present in May 2026")

    public_holidays = get_events(
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 31),
        region="CN,HK,US",
        event_type="public_holiday",
    )
    assert_ok(
        any(event["date"] == "2026-05-01" and event["title"] == "CN PH: Labour Day" for event in public_holidays),
        "Expected mainland public holidays to be present"
    )
    assert_ok(
        any(event["date"] == "2026-05-01" and event["title"] == "HK PH: Labour Day" for event in public_holidays),
        "Expected Hong Kong public holidays to be present"
    )
    assert_ok(
        any(event["date"] == "2026-05-25" and event["title"] == "US PH: Memorial Day" for event in public_holidays),
        "Expected US public holidays to be present"
    )
    assert_ok(
        any(event["date"] == "2026-04-05" and event["title"] == "CN ST: 清明" for event in all_events),
        "Expected Chinese solar terms to be included in public holiday data"
    )

    macro_events = get_events(
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 31),
        region="US",
        event_type="macro_event",
    )
    assert_ok(
        any(event["date"] == "2026-03-18" and event["title"] == "FOMC Rate Decision" for event in macro_events),
        "Expected dynamic FOMC macro events to be present"
    )

    may_events = get_events(
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 31),
        region=None,
        event_type=None,
    )
    assert_ok(
        all("2026-05-01" <= event["date"] <= "2026-05-31" for event in may_events),
        "Expected date range filtering to constrain the response",
    )
    assert_ok(
        all(event["type"] != "market_open" for event in may_events),
        "Expected market-open events to be omitted from the API output",
    )

    print(f"PASS: base={len(all_events)} hk_closed={len(hk_closed_events)} public={len(public_holidays)} macro={len(macro_events)} may={len(may_events)}")


if __name__ == "__main__":
    main()
