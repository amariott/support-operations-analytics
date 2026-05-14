from __future__ import annotations

from datetime import datetime

from utils import PROCESSED_DIR, RAW_DIR, ensure_directories, parse_datetime, read_csv, to_float, write_csv


RAW_TABLES = [
    "tickets",
    "ticket_events",
    "agents",
    "departments",
    "customer_segments",
    "calendar",
]


def check_duplicates(rows: list[dict[str, str]], key: str) -> int:
    seen = set()
    duplicate_count = 0
    for row in rows:
        value = row.get(key, "")
        if value in seen:
            duplicate_count += 1
        seen.add(value)
    return duplicate_count


def normalize_datetime(value: str) -> str:
    if not value:
        return ""
    return datetime.fromisoformat(value).isoformat(sep=" ", timespec="minutes")


def clean_tickets(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    cleaned: list[dict[str, str]] = []
    checks: list[dict[str, object]] = []
    duplicate_count = check_duplicates(rows, "ticket_id")
    invalid_dates = 0
    negative_durations = 0
    missing_required = 0

    for row in rows:
        required_values = [
            row.get("ticket_id"),
            row.get("created_at"),
            row.get("first_response_at"),
            row.get("priority"),
            row.get("category"),
            row.get("agent_id"),
            row.get("department_id"),
            row.get("customer_segment_id"),
        ]
        if any(value in (None, "") for value in required_values):
            missing_required += 1
            continue

        try:
            created_at = parse_datetime(row["created_at"])
            first_response_at = parse_datetime(row["first_response_at"])
            closed_at = parse_datetime(row.get("closed_at", ""))
        except ValueError:
            invalid_dates += 1
            continue

        if first_response_at is None or created_at is None:
            invalid_dates += 1
            continue
        if first_response_at < created_at or (closed_at is not None and closed_at < created_at):
            negative_durations += 1
            continue
        if to_float(row.get("first_response_hours")) < 0 or to_float(row.get("resolution_hours")) < 0:
            negative_durations += 1
            continue

        normalized = row.copy()
        normalized["created_at"] = normalize_datetime(row["created_at"])
        normalized["first_response_at"] = normalize_datetime(row["first_response_at"])
        normalized["closed_at"] = normalize_datetime(row.get("closed_at", ""))
        normalized["sla_target_hours"] = str(int(float(row["sla_target_hours"])))
        normalized["sla_breached"] = "1" if row["sla_breached"] in ("1", "true", "True") else "0"
        normalized["first_response_hours"] = f"{to_float(row['first_response_hours']):.2f}"
        normalized["resolution_hours"] = f"{to_float(row['resolution_hours']):.2f}"
        if normalized.get("satisfaction_score"):
            normalized["satisfaction_score"] = f"{to_float(row['satisfaction_score']):.1f}"
        cleaned.append(normalized)

    checks.extend(
        [
            {
                "table_name": "tickets",
                "check_name": "duplicate ticket_id",
                "issue_count": duplicate_count,
                "result": "pass" if duplicate_count == 0 else "fail",
            },
            {
                "table_name": "tickets",
                "check_name": "missing required values",
                "issue_count": missing_required,
                "result": "pass" if missing_required == 0 else "fail",
            },
            {
                "table_name": "tickets",
                "check_name": "invalid dates",
                "issue_count": invalid_dates,
                "result": "pass" if invalid_dates == 0 else "fail",
            },
            {
                "table_name": "tickets",
                "check_name": "negative durations",
                "issue_count": negative_durations,
                "result": "pass" if negative_durations == 0 else "fail",
            },
        ]
    )
    return cleaned, checks


def clean_events(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    cleaned: list[dict[str, str]] = []
    duplicate_count = check_duplicates(rows, "event_id")
    invalid_dates = 0
    missing_required = 0

    for row in rows:
        if not row.get("event_id") or not row.get("ticket_id") or not row.get("event_time"):
            missing_required += 1
            continue
        try:
            normalized = row.copy()
            normalized["event_time"] = normalize_datetime(row["event_time"])
        except ValueError:
            invalid_dates += 1
            continue
        cleaned.append(normalized)

    checks = [
        {
            "table_name": "ticket_events",
            "check_name": "duplicate event_id",
            "issue_count": duplicate_count,
            "result": "pass" if duplicate_count == 0 else "fail",
        },
        {
            "table_name": "ticket_events",
            "check_name": "missing required values",
            "issue_count": missing_required,
            "result": "pass" if missing_required == 0 else "fail",
        },
        {
            "table_name": "ticket_events",
            "check_name": "invalid event dates",
            "issue_count": invalid_dates,
            "result": "pass" if invalid_dates == 0 else "fail",
        },
    ]
    return cleaned, checks


def copy_dimension_table(table_name: str) -> list[dict[str, str]]:
    return read_csv(RAW_DIR / f"{table_name}.csv")


def main() -> None:
    ensure_directories()
    quality_checks: list[dict[str, object]] = []

    raw_tickets = read_csv(RAW_DIR / "tickets.csv")
    raw_events = read_csv(RAW_DIR / "ticket_events.csv")
    tickets, ticket_checks = clean_tickets(raw_tickets)
    events, event_checks = clean_events(raw_events)
    quality_checks.extend(ticket_checks)
    quality_checks.extend(event_checks)

    write_csv(PROCESSED_DIR / "tickets.csv", tickets)
    write_csv(PROCESSED_DIR / "ticket_events.csv", events)

    for table_name in RAW_TABLES:
        if table_name in ("tickets", "ticket_events"):
            continue
        rows = copy_dimension_table(table_name)
        write_csv(PROCESSED_DIR / f"{table_name}.csv", rows)
        key = rows[0].keys().__iter__().__next__() if rows else "id"
        duplicates = check_duplicates(rows, key)
        quality_checks.append(
            {
                "table_name": table_name,
                "check_name": f"duplicate {key}",
                "issue_count": duplicates,
                "result": "pass" if duplicates == 0 else "fail",
            }
        )

    write_csv(
        PROCESSED_DIR / "data_quality_summary.csv",
        quality_checks,
        ["table_name", "check_name", "issue_count", "result"],
    )
    print(f"cleaned {len(tickets)} tickets and {len(events)} events")


if __name__ == "__main__":
    main()

