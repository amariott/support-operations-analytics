from __future__ import annotations

import csv
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median as statistics_median


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MARTS_DIR = DATA_DIR / "marts"
REPORTS_DIR = ROOT_DIR / "reports"


def ensure_directories() -> None:
    for directory in (RAW_DIR, PROCESSED_DIR, MARTS_DIR, REPORTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def iso_datetime(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.isoformat(sep=" ", timespec="minutes")


def iso_date(value: date | None) -> str:
    if value is None:
        return ""
    return value.isoformat()


def daterange(start_date: date, end_date: date) -> list[date]:
    days = (end_date - start_date).days
    return [start_date + timedelta(days=offset) for offset in range(days + 1)]


def hours_between(start_value: datetime, end_value: datetime) -> float:
    return round((end_value - start_value).total_seconds() / 3600, 2)


def mean(values: list[float]) -> float:
    clean_values = [value for value in values if value is not None]
    if not clean_values:
        return 0.0
    return sum(clean_values) / len(clean_values)


def median(values: list[float]) -> float:
    clean_values = [value for value in values if value is not None]
    if not clean_values:
        return 0.0
    return float(statistics_median(clean_values))


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def round_float(value: float | None, digits: int = 2) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def to_float(value: str | None, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)


def to_int(value: str | None, default: int = 0) -> int:
    if value in (None, ""):
        return default
    return int(float(value))

