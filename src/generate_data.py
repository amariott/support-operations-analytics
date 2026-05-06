from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta

from utils import RAW_DIR, daterange, ensure_directories, hours_between, iso_date, iso_datetime, round_float, write_csv


SEED = 42
START_DATE = date(2025, 10, 1)
END_DATE = date(2026, 5, 31)
END_DATETIME = datetime.combine(END_DATE, time(23, 59))


DEPARTMENTS = [
    {"department_id": "dep_01", "department_name": "technical support", "manager_name": "alina markova"},
    {"department_id": "dep_02", "department_name": "billing support", "manager_name": "roman belov"},
    {"department_id": "dep_03", "department_name": "customer success", "manager_name": "sofia nikitina"},
    {"department_id": "dep_04", "department_name": "trust and safety", "manager_name": "ivan sokolov"},
    {"department_id": "dep_05", "department_name": "platform operations", "manager_name": "daria volkova"},
]

CUSTOMER_SEGMENTS = [
    {"customer_segment_id": "seg_01", "segment_name": "enterprise", "sla_multiplier": 0.75, "satisfaction_weight": 0.15},
    {"customer_segment_id": "seg_02", "segment_name": "premium smb", "sla_multiplier": 0.90, "satisfaction_weight": 0.10},
    {"customer_segment_id": "seg_03", "segment_name": "standard smb", "sla_multiplier": 1.00, "satisfaction_weight": 0.00},
    {"customer_segment_id": "seg_04", "segment_name": "self service", "sla_multiplier": 1.20, "satisfaction_weight": -0.05},
    {"customer_segment_id": "seg_05", "segment_name": "trial", "sla_multiplier": 1.35, "satisfaction_weight": -0.10},
]

SEGMENT_WEIGHTS = {
    "enterprise": 18,
    "premium smb": 22,
    "standard smb": 34,
    "self service": 18,
    "trial": 8,
}

AGENT_NAMES = [
    ("agt_001", "anna petrova", "dep_01", 1.04, 1.40, "senior"),
    ("agt_002", "mikhail orlov", "dep_01", 0.92, 1.05, "middle"),
    ("agt_003", "ksenia smirnova", "dep_01", 1.15, 0.85, "junior"),
    ("agt_004", "pavel morozov", "dep_01", 0.96, 1.15, "middle"),
    ("agt_005", "elena fedorova", "dep_02", 1.08, 1.35, "middle"),
    ("agt_006", "kirill egorov", "dep_02", 0.90, 0.95, "senior"),
    ("agt_007", "natalia kuzmina", "dep_02", 1.18, 0.80, "junior"),
    ("agt_008", "artem pavlov", "dep_03", 0.94, 1.10, "senior"),
    ("agt_009", "maria zaitseva", "dep_03", 1.10, 1.30, "middle"),
    ("agt_010", "sergey vinogradov", "dep_03", 1.20, 0.75, "junior"),
    ("agt_011", "dmitry antonov", "dep_04", 0.95, 1.05, "senior"),
    ("agt_012", "olga romanova", "dep_04", 1.12, 1.25, "middle"),
    ("agt_013", "viktor lebedev", "dep_04", 1.22, 0.75, "junior"),
    ("agt_014", "irina volkova", "dep_05", 1.06, 1.45, "middle"),
    ("agt_015", "nikolay belyaev", "dep_05", 0.89, 1.05, "senior"),
    ("agt_016", "yana medvedeva", "dep_05", 1.18, 0.85, "junior"),
    ("agt_017", "egor karpov", "dep_01", 1.00, 1.20, "middle"),
    ("agt_018", "vera gromova", "dep_03", 0.93, 1.00, "senior"),
]

CATEGORIES = [
    {"category": "login access", "department_id": "dep_01", "complexity": 0.80, "breach_bias": 0.90},
    {"category": "bug report", "department_id": "dep_01", "complexity": 1.25, "breach_bias": 1.20},
    {"category": "integration issue", "department_id": "dep_05", "complexity": 1.45, "breach_bias": 1.35},
    {"category": "billing question", "department_id": "dep_02", "complexity": 0.75, "breach_bias": 0.85},
    {"category": "invoice dispute", "department_id": "dep_02", "complexity": 1.05, "breach_bias": 1.15},
    {"category": "onboarding help", "department_id": "dep_03", "complexity": 0.95, "breach_bias": 0.90},
    {"category": "feature request", "department_id": "dep_03", "complexity": 1.10, "breach_bias": 1.05},
    {"category": "abuse report", "department_id": "dep_04", "complexity": 1.30, "breach_bias": 1.25},
    {"category": "data export", "department_id": "dep_05", "complexity": 1.15, "breach_bias": 1.10},
]

CATEGORY_WEIGHTS = {
    "login access": 16,
    "bug report": 17,
    "integration issue": 11,
    "billing question": 16,
    "invoice dispute": 9,
    "onboarding help": 12,
    "feature request": 9,
    "abuse report": 5,
    "data export": 5,
}

PRIORITIES = {
    "low": {"weight": 28, "sla_hours": 96, "first_response_target": 24, "resolution_base": 34},
    "medium": {"weight": 46, "sla_hours": 48, "first_response_target": 12, "resolution_base": 24},
    "high": {"weight": 20, "sla_hours": 18, "first_response_target": 4, "resolution_base": 13},
    "critical": {"weight": 6, "sla_hours": 8, "first_response_target": 1, "resolution_base": 7},
}

CHANNEL_WEIGHTS = {
    "email": 34,
    "chat": 26,
    "portal": 20,
    "phone": 14,
    "social": 6,
}

SPIKE_DAYS = {
    date(2025, 11, 24): {"extra": 36, "categories": {"login access": 30, "bug report": 26, "integration issue": 24}},
    date(2025, 12, 29): {"extra": 28, "categories": {"invoice dispute": 30, "billing question": 25}},
    date(2026, 2, 3): {"extra": 26, "categories": {"billing question": 25, "invoice dispute": 20}},
    date(2026, 3, 16): {"extra": 34, "categories": {"integration issue": 32, "bug report": 25}},
    date(2026, 4, 21): {"extra": 42, "categories": {"integration issue": 38, "bug report": 28, "login access": 20}},
}


def weighted_choice(items: list[dict[str, object]], weights: list[float]) -> dict[str, object]:
    return random.choices(items, weights=weights, k=1)[0]


def weighted_key(weights_by_key: dict[str, float]) -> str:
    return random.choices(list(weights_by_key.keys()), weights=list(weights_by_key.values()), k=1)[0]


def build_agents() -> list[dict[str, object]]:
    agents = []
    for agent_id, agent_name, department_id, speed_factor, assignment_weight, seniority in AGENT_NAMES:
        agents.append(
            {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "department_id": department_id,
                "seniority": seniority,
                "speed_factor": speed_factor,
                "assignment_weight": assignment_weight,
                "is_overloaded_group": "yes" if assignment_weight >= 1.25 else "no",
            }
        )
    return agents


def build_calendar() -> list[dict[str, object]]:
    rows = []
    for day in daterange(START_DATE, END_DATE):
        week_start = day - timedelta(days=day.weekday())
        rows.append(
            {
                "date": iso_date(day),
                "year": day.year,
                "month": day.month,
                "day": day.day,
                "day_of_week": day.weekday() + 1,
                "day_name": day.strftime("%A").lower(),
                "week_start": iso_date(week_start),
                "is_weekend": 1 if day.weekday() >= 5 else 0,
                "is_business_day": 0 if day.weekday() >= 5 else 1,
            }
        )
    return rows


def daily_ticket_volume(day: date) -> int:
    base = 22
    if day.weekday() == 0:
        base += 12
    elif day.weekday() in (1, 2, 3):
        base += 6
    elif day.weekday() == 4:
        base += 3
    else:
        base -= 11

    if day.month in (11, 12):
        base += 4
    if day.month in (3, 4):
        base += 3
    if day in SPIKE_DAYS:
        base += SPIKE_DAYS[day]["extra"]

    return max(6, int(random.gauss(base, 4.5)))


def choose_category(day: date) -> dict[str, object]:
    weights = CATEGORY_WEIGHTS.copy()
    if day in SPIKE_DAYS:
        weights.update(SPIKE_DAYS[day]["categories"])
    category_name = weighted_key(weights)
    return next(category for category in CATEGORIES if category["category"] == category_name)


def choose_created_time(day: date) -> datetime:
    hours = list(range(24))
    hour_weights = [2, 1, 1, 1, 1, 2, 5, 10, 16, 19, 20, 18, 16, 17, 18, 20, 19, 16, 11, 8, 6, 4, 3, 2]
    if day.weekday() >= 5:
        hour_weights = [1, 1, 1, 1, 1, 1, 2, 4, 6, 8, 9, 9, 8, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1]
    hour = random.choices(hours, weights=hour_weights, k=1)[0]
    return datetime.combine(day, time(hour, random.randint(0, 59)))


def clamp_score(value: float) -> float:
    return max(1.0, min(5.0, value))


def generate_ticket_rows() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    agents = build_agents()
    agents_by_department: dict[str, list[dict[str, object]]] = {}
    for agent in agents:
        agents_by_department.setdefault(str(agent["department_id"]), []).append(agent)

    tickets: list[dict[str, object]] = []
    events: list[dict[str, object]] = []
    event_id = 1
    ticket_number = 1

    for day in daterange(START_DATE, END_DATE):
        volume = daily_ticket_volume(day)
        volume_pressure = 1.0 + max(0, volume - 32) / 75

        for _ in range(volume):
            category = choose_category(day)
            priority = weighted_key({key: value["weight"] for key, value in PRIORITIES.items()})
            priority_profile = PRIORITIES[priority]
            segment = weighted_choice(
                CUSTOMER_SEGMENTS,
                [SEGMENT_WEIGHTS[str(item["segment_name"])] for item in CUSTOMER_SEGMENTS],
            )
            channel = weighted_key(CHANNEL_WEIGHTS)
            department_id = str(category["department_id"])
            agent_pool = agents_by_department[department_id]
            agent = weighted_choice(agent_pool, [float(item["assignment_weight"]) for item in agent_pool])

            created_at = choose_created_time(day)
            segment_multiplier = float(segment["sla_multiplier"])
            sla_target_hours = max(4, int(priority_profile["sla_hours"] * segment_multiplier))

            response_noise = random.lognormvariate(0, 0.45)
            first_response_hours = (
                float(priority_profile["first_response_target"])
                * float(agent["speed_factor"])
                * float(category["complexity"])
                * volume_pressure
                * response_noise
            )
            resolution_noise = random.lognormvariate(0, 0.55)
            resolution_hours = (
                float(priority_profile["resolution_base"])
                * float(category["complexity"])
                * float(agent["speed_factor"])
                * float(category["breach_bias"])
                * volume_pressure
                * resolution_noise
            )
            resolution_hours = max(first_response_hours + 0.5, resolution_hours)

            first_response_at = created_at + timedelta(hours=first_response_hours)
            planned_closed_at = created_at + timedelta(hours=resolution_hours)
            days_to_end = (END_DATE - day).days
            open_probability = 0.02 + (0.13 if days_to_end < 14 else 0.0) + (0.05 if resolution_hours > sla_target_hours else 0.0)
            is_open = planned_closed_at > END_DATETIME or random.random() < open_probability

            if is_open:
                closed_at = None
                status = random.choices(["open", "pending", "in_progress"], weights=[22, 34, 44], k=1)[0]
                current_age_hours = hours_between(created_at, END_DATETIME)
                if first_response_at > END_DATETIME:
                    first_response_hours = max(0.1, current_age_hours * 0.55)
                    first_response_at = created_at + timedelta(hours=first_response_hours)
                resolution_value = current_age_hours
                sla_breached = current_age_hours > sla_target_hours
                satisfaction_score = ""
            else:
                closed_at = planned_closed_at
                status = random.choices(["closed", "resolved"], weights=[86, 14], k=1)[0]
                resolution_value = resolution_hours
                sla_breached = resolution_hours > sla_target_hours
                score = (
                    4.8
                    + float(segment["satisfaction_weight"])
                    - (0.85 if sla_breached else 0.0)
                    - min(1.35, resolution_hours / max(sla_target_hours, 1) * 0.35)
                    - (0.35 if priority in ("high", "critical") and sla_breached else 0.0)
                    + random.gauss(0, 0.35)
                )
                satisfaction_score = f"{clamp_score(score):.1f}"

            ticket_id = f"tck_{ticket_number:06d}"
            tickets.append(
                {
                    "ticket_id": ticket_id,
                    "created_at": iso_datetime(created_at),
                    "first_response_at": iso_datetime(first_response_at),
                    "closed_at": iso_datetime(closed_at),
                    "status": status,
                    "priority": priority,
                    "category": category["category"],
                    "channel": channel,
                    "agent_id": agent["agent_id"],
                    "department_id": department_id,
                    "customer_segment_id": segment["customer_segment_id"],
                    "sla_target_hours": sla_target_hours,
                    "sla_breached": 1 if sla_breached else 0,
                    "first_response_hours": round_float(first_response_hours),
                    "resolution_hours": round_float(resolution_value),
                    "satisfaction_score": satisfaction_score,
                }
            )

            event_id = add_event(events, event_id, ticket_id, created_at, "created", "", "open", "")
            assigned_at = created_at + timedelta(minutes=random.randint(3, 45))
            event_id = add_event(events, event_id, ticket_id, assigned_at, "assigned", "open", "assigned", str(agent["agent_id"]))
            event_id = add_event(events, event_id, ticket_id, first_response_at, "first_response", "assigned", "in_progress", str(agent["agent_id"]))
            if sla_breached and priority in ("high", "critical", "medium"):
                escalation_at = created_at + timedelta(hours=min(resolution_value * 0.65, sla_target_hours + 1))
                event_id = add_event(events, event_id, ticket_id, escalation_at, "escalated", "in_progress", "escalated", str(agent["agent_id"]))
            if closed_at is not None:
                event_id = add_event(events, event_id, ticket_id, closed_at, "closed", "in_progress", status, str(agent["agent_id"]))

            ticket_number += 1

    return tickets, events, agents


def add_event(
    events: list[dict[str, object]],
    event_number: int,
    ticket_id: str,
    event_time: datetime,
    event_type: str,
    old_status: str,
    new_status: str,
    agent_id: str,
) -> int:
    events.append(
        {
            "event_id": f"evt_{event_number:07d}",
            "ticket_id": ticket_id,
            "event_time": iso_datetime(event_time),
            "event_type": event_type,
            "old_status": old_status,
            "new_status": new_status,
            "agent_id": agent_id,
        }
    )
    return event_number + 1


def main() -> None:
    random.seed(SEED)
    ensure_directories()

    tickets, events, agents = generate_ticket_rows()
    write_csv(RAW_DIR / "departments.csv", DEPARTMENTS)
    write_csv(RAW_DIR / "customer_segments.csv", CUSTOMER_SEGMENTS)
    write_csv(RAW_DIR / "agents.csv", agents)
    write_csv(RAW_DIR / "calendar.csv", build_calendar())
    write_csv(RAW_DIR / "tickets.csv", tickets)
    write_csv(RAW_DIR / "ticket_events.csv", sorted(events, key=lambda row: (row["ticket_id"], row["event_time"])))

    print(f"generated {len(tickets)} tickets and {len(events)} events")


if __name__ == "__main__":
    main()
