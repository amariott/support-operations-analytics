from __future__ import annotations

from collections import defaultdict
from datetime import datetime, time

from utils import (
    MARTS_DIR,
    PROCESSED_DIR,
    hours_between,
    mean,
    parse_date,
    parse_datetime,
    read_csv,
    round_float,
    safe_divide,
    to_float,
    to_int,
    write_csv,
)


def load_dimensions() -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    agents = {row["agent_id"]: row for row in read_csv(PROCESSED_DIR / "agents.csv")}
    departments = {row["department_id"]: row for row in read_csv(PROCESSED_DIR / "departments.csv")}
    segments = {row["customer_segment_id"]: row for row in read_csv(PROCESSED_DIR / "customer_segments.csv")}
    return agents, departments, segments


def enrich_ticket(row: dict[str, str], departments: dict[str, dict[str, str]]) -> dict[str, object]:
    created_at = parse_datetime(row["created_at"])
    closed_at = parse_datetime(row.get("closed_at", ""))
    if created_at is None:
        raise ValueError("created_at is required")
    department = departments[row["department_id"]]
    return {
        **row,
        "created_dt": created_at,
        "created_date": created_at.date(),
        "closed_dt": closed_at,
        "closed_date": closed_at.date() if closed_at else None,
        "department_name": department["department_name"],
        "sla_breached_int": to_int(row["sla_breached"]),
        "first_response_float": to_float(row["first_response_hours"]),
        "resolution_float": to_float(row["resolution_hours"]),
        "satisfaction_float": to_float(row.get("satisfaction_score"), default=None),
    }


def build_sla_mart(tickets: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for ticket in tickets:
        key = (ticket["created_date"], ticket["department_id"], ticket["department_name"], ticket["priority"])
        groups[key].append(ticket)

    rows = []
    for (created_date, department_id, department_name, priority), group in sorted(groups.items()):
        closed_group = [ticket for ticket in group if ticket["closed_dt"] is not None]
        rows.append(
            {
                "date": created_date,
                "department_id": department_id,
                "department_name": department_name,
                "priority": priority,
                "tickets_created": len(group),
                "tickets_closed": len(closed_group),
                "sla_breached_tickets": sum(int(ticket["sla_breached_int"]) for ticket in group),
                "sla_breach_rate": round_float(safe_divide(sum(int(ticket["sla_breached_int"]) for ticket in group), len(group))),
                "avg_first_response_hours": round_float(mean([float(ticket["first_response_float"]) for ticket in group])),
                "avg_resolution_hours": round_float(mean([float(ticket["resolution_float"]) for ticket in group])),
                "avg_satisfaction_score": round_float(
                    mean([float(ticket["satisfaction_float"]) for ticket in closed_group if ticket["satisfaction_float"] is not None]),
                    2,
                ),
            }
        )
    return rows


def build_backlog_mart(tickets: list[dict[str, object]], calendar_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    rows = []
    for calendar_row in calendar_rows:
        current_date = parse_date(calendar_row["date"])
        if current_date is None:
            continue
        day_end = datetime.combine(current_date, time(23, 59))
        opened_today = [ticket for ticket in tickets if ticket["created_date"] == current_date]
        closed_today = [ticket for ticket in tickets if ticket["closed_date"] == current_date]
        open_at_end = [
            ticket
            for ticket in tickets
            if ticket["created_dt"] <= day_end and (ticket["closed_dt"] is None or ticket["closed_dt"] > day_end)
        ]
        high_priority_open = [ticket for ticket in open_at_end if ticket["priority"] in ("high", "critical")]
        rows.append(
            {
                "date": calendar_row["date"],
                "week_start": calendar_row["week_start"],
                "day_of_week": calendar_row["day_of_week"],
                "is_weekend": calendar_row["is_weekend"],
                "tickets_opened": len(opened_today),
                "tickets_closed": len(closed_today),
                "backlog_open_tickets": len(open_at_end),
                "high_priority_backlog": len(high_priority_open),
                "sla_breached_in_backlog": sum(int(ticket["sla_breached_int"]) for ticket in open_at_end),
                "avg_open_age_hours": round_float(mean([hours_between(ticket["created_dt"], day_end) for ticket in open_at_end])),
            }
        )
    return rows


def build_workload_mart(
    tickets: list[dict[str, object]],
    agents: dict[str, dict[str, str]],
    departments: dict[str, dict[str, str]],
    calendar_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    rows = []
    for calendar_row in calendar_rows:
        current_date = parse_date(calendar_row["date"])
        if current_date is None:
            continue
        day_end = datetime.combine(current_date, time(23, 59))
        for agent_id, agent in agents.items():
            assigned_today = [ticket for ticket in tickets if ticket["agent_id"] == agent_id and ticket["created_date"] == current_date]
            closed_today = [ticket for ticket in tickets if ticket["agent_id"] == agent_id and ticket["closed_date"] == current_date]
            backlog = [
                ticket
                for ticket in tickets
                if ticket["agent_id"] == agent_id
                and ticket["created_dt"] <= day_end
                and (ticket["closed_dt"] is None or ticket["closed_dt"] > day_end)
            ]
            rows.append(
                {
                    "date": calendar_row["date"],
                    "agent_id": agent_id,
                    "agent_name": agent["agent_name"],
                    "department_id": agent["department_id"],
                    "department_name": departments[agent["department_id"]]["department_name"],
                    "seniority": agent["seniority"],
                    "is_overloaded_group": agent["is_overloaded_group"],
                    "assigned_tickets": len(assigned_today),
                    "closed_tickets": len(closed_today),
                    "open_backlog": len(backlog),
                    "sla_breach_rate": round_float(
                        safe_divide(sum(int(ticket["sla_breached_int"]) for ticket in assigned_today), len(assigned_today))
                    ),
                    "avg_resolution_hours": round_float(mean([float(ticket["resolution_float"]) for ticket in closed_today])),
                    "avg_satisfaction_score": round_float(
                        mean([float(ticket["satisfaction_float"]) for ticket in closed_today if ticket["satisfaction_float"] is not None])
                    ),
                }
            )
    return rows


def build_ticket_volume_mart(tickets: list[dict[str, object]], calendar_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    calendar_by_date = {row["date"]: row for row in calendar_rows}
    groups: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for ticket in tickets:
        date_value = str(ticket["created_date"])
        key = (
            date_value,
            ticket["category"],
            ticket["channel"],
            ticket["priority"],
            ticket["department_name"],
        )
        groups[key].append(ticket)

    rows = []
    for (date_value, category, channel, priority, department_name), group in sorted(groups.items()):
        calendar_row = calendar_by_date[date_value]
        rows.append(
            {
                "date": date_value,
                "week_start": calendar_row["week_start"],
                "month": date_value[:7],
                "day_of_week": calendar_row["day_of_week"],
                "is_weekend": calendar_row["is_weekend"],
                "category": category,
                "channel": channel,
                "priority": priority,
                "department_name": department_name,
                "ticket_count": len(group),
                "sla_breach_rate": round_float(safe_divide(sum(int(ticket["sla_breached_int"]) for ticket in group), len(group))),
                "avg_first_response_hours": round_float(mean([float(ticket["first_response_float"]) for ticket in group])),
                "avg_resolution_hours": round_float(mean([float(ticket["resolution_float"]) for ticket in group])),
            }
        )
    return rows


def build_forecast_base_mart(tickets: list[dict[str, object]], calendar_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    counts_by_date: dict[str, int] = defaultdict(int)
    for ticket in tickets:
        counts_by_date[str(ticket["created_date"])] += 1

    rows = []
    counts_history: list[int] = []
    for calendar_row in calendar_rows:
        count = counts_by_date[calendar_row["date"]]
        lag_1 = counts_history[-1] if len(counts_history) >= 1 else ""
        lag_7 = counts_history[-7] if len(counts_history) >= 7 else ""
        rolling_7 = round_float(mean(counts_history[-7:])) if len(counts_history) >= 7 else ""
        rows.append(
            {
                "date": calendar_row["date"],
                "actual_tickets": count,
                "day_of_week": calendar_row["day_of_week"],
                "month": calendar_row["date"][:7],
                "is_weekend": calendar_row["is_weekend"],
                "lag_1": lag_1,
                "lag_7": lag_7,
                "rolling_7_mean": rolling_7,
                "model_forecast": "",
                "moving_average_forecast": "",
                "dataset_split": "history",
                "absolute_error": "",
            }
        )
        counts_history.append(count)
    return rows


def main() -> None:
    agents, departments, _segments = load_dimensions()
    calendar_rows = read_csv(PROCESSED_DIR / "calendar.csv")
    tickets = [enrich_ticket(row, departments) for row in read_csv(PROCESSED_DIR / "tickets.csv")]

    write_csv(MARTS_DIR / "mart_sla.csv", build_sla_mart(tickets))
    write_csv(MARTS_DIR / "mart_backlog.csv", build_backlog_mart(tickets, calendar_rows))
    write_csv(MARTS_DIR / "mart_workload.csv", build_workload_mart(tickets, agents, departments, calendar_rows))
    write_csv(MARTS_DIR / "mart_ticket_volume.csv", build_ticket_volume_mart(tickets, calendar_rows))
    write_csv(MARTS_DIR / "mart_forecast.csv", build_forecast_base_mart(tickets, calendar_rows))
    print("built mart_sla, mart_backlog, mart_workload, mart_ticket_volume and mart_forecast")


if __name__ == "__main__":
    main()

