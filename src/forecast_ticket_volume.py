from __future__ import annotations

from datetime import date, timedelta
from math import fabs

from utils import MARTS_DIR, PROCESSED_DIR, REPORTS_DIR, mean, parse_date, read_csv, round_float, safe_divide, write_csv


TEST_DAYS = 28
FUTURE_DAYS = 14
RIDGE_LAMBDA = 0.25


def daily_counts() -> list[dict[str, object]]:
    tickets = read_csv(PROCESSED_DIR / "tickets.csv")
    calendar = read_csv(PROCESSED_DIR / "calendar.csv")
    counts = {row["date"]: 0 for row in calendar}
    for ticket in tickets:
        counts[ticket["created_at"][:10]] += 1

    rows = []
    history: list[int] = []
    for calendar_row in calendar:
        count = counts[calendar_row["date"]]
        rows.append(
            {
                "date": calendar_row["date"],
                "actual_tickets": count,
                "day_of_week": int(calendar_row["day_of_week"]),
                "month_number": int(calendar_row["date"][5:7]),
                "is_weekend": int(calendar_row["is_weekend"]),
                "lag_1": history[-1] if len(history) >= 1 else 0,
                "lag_7": history[-7] if len(history) >= 7 else 0,
                "rolling_7_mean": mean(history[-7:]) if len(history) >= 7 else 0,
            }
        )
        history.append(count)
    return rows


def features(row: dict[str, object]) -> list[float]:
    day_of_week = int(row["day_of_week"])
    day_flags = [1.0 if day_of_week == value else 0.0 for value in range(1, 8)]
    return [
        1.0,
        float(row["month_number"]),
        float(row["is_weekend"]),
        float(row["lag_1"]),
        float(row["lag_7"]),
        float(row["rolling_7_mean"]),
        *day_flags,
    ]


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [matrix[row][:] + [vector[row]] for row in range(size)]

    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(augmented[row][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        if abs(pivot_value) < 1e-9:
            continue
        for item in range(column, size + 1):
            augmented[column][item] /= pivot_value
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            for item in range(column, size + 1):
                augmented[row][item] -= factor * augmented[column][item]

    return [augmented[row][size] for row in range(size)]


def fit_ridge_regression(rows: list[dict[str, object]]) -> list[float]:
    sample_features = features(rows[0])
    feature_count = len(sample_features)
    xtx = [[0.0 for _ in range(feature_count)] for _ in range(feature_count)]
    xty = [0.0 for _ in range(feature_count)]

    for row in rows:
        x_values = features(row)
        y_value = float(row["actual_tickets"])
        for i in range(feature_count):
            xty[i] += x_values[i] * y_value
            for j in range(feature_count):
                xtx[i][j] += x_values[i] * x_values[j]

    for i in range(feature_count):
        if i != 0:
            xtx[i][i] += RIDGE_LAMBDA
    return solve_linear_system(xtx, xty)


def predict(row: dict[str, object], coefficients: list[float]) -> float:
    return max(0.0, sum(value * coefficients[index] for index, value in enumerate(features(row))))


def mae(actual: list[float], predicted: list[float]) -> float:
    return mean([fabs(a_value - p_value) for a_value, p_value in zip(actual, predicted)])


def mape(actual: list[float], predicted: list[float]) -> float:
    values = [safe_divide(fabs(a_value - p_value), a_value) for a_value, p_value in zip(actual, predicted) if a_value != 0]
    return mean(values) * 100


def make_future_rows(rows: list[dict[str, object]], coefficients: list[float]) -> list[dict[str, object]]:
    future_rows: list[dict[str, object]] = []
    history_counts = [int(row["actual_tickets"]) for row in rows]
    last_date = parse_date(str(rows[-1]["date"]))
    if last_date is None:
        return future_rows

    for offset in range(1, FUTURE_DAYS + 1):
        current_date = last_date + timedelta(days=offset)
        row = {
            "date": current_date.isoformat(),
            "actual_tickets": "",
            "day_of_week": current_date.weekday() + 1,
            "month_number": current_date.month,
            "is_weekend": 1 if current_date.weekday() >= 5 else 0,
            "lag_1": history_counts[-1],
            "lag_7": history_counts[-7] if len(history_counts) >= 7 else history_counts[-1],
            "rolling_7_mean": mean(history_counts[-7:]),
        }
        forecast_value = round(predict(row, coefficients))
        row["model_forecast"] = forecast_value
        row["moving_average_forecast"] = round(row["rolling_7_mean"])
        row["dataset_split"] = "future"
        row["absolute_error"] = ""
        future_rows.append(row)
        history_counts.append(forecast_value)
    return future_rows


def build_forecast_mart() -> tuple[list[dict[str, object]], dict[str, float]]:
    rows = daily_counts()
    model_rows = rows[14:]
    train_rows = model_rows[:-TEST_DAYS]
    test_rows = model_rows[-TEST_DAYS:]
    coefficients = fit_ridge_regression(train_rows)

    actual_values: list[float] = []
    model_predictions: list[float] = []
    baseline_predictions: list[float] = []

    output_rows: list[dict[str, object]] = []
    test_dates = {row["date"] for row in test_rows}
    for row in rows:
        is_test = row["date"] in test_dates
        model_forecast = predict(row, coefficients) if is_test and row in model_rows else ""
        baseline_forecast = row["rolling_7_mean"] if is_test else ""
        if is_test:
            actual_values.append(float(row["actual_tickets"]))
            model_predictions.append(float(model_forecast))
            baseline_predictions.append(float(baseline_forecast))
        output_rows.append(
            {
                "date": row["date"],
                "actual_tickets": row["actual_tickets"],
                "day_of_week": row["day_of_week"],
                "month": str(row["date"])[:7],
                "is_weekend": row["is_weekend"],
                "lag_1": row["lag_1"],
                "lag_7": row["lag_7"],
                "rolling_7_mean": round_float(float(row["rolling_7_mean"])),
                "model_forecast": round_float(float(model_forecast)) if model_forecast != "" else "",
                "moving_average_forecast": round_float(float(baseline_forecast)) if baseline_forecast != "" else "",
                "dataset_split": "test" if is_test else "train",
                "absolute_error": round_float(fabs(float(row["actual_tickets"]) - float(model_forecast))) if is_test else "",
            }
        )

    for row in make_future_rows(rows, coefficients):
        output_rows.append(
            {
                "date": row["date"],
                "actual_tickets": "",
                "day_of_week": row["day_of_week"],
                "month": str(row["date"])[:7],
                "is_weekend": row["is_weekend"],
                "lag_1": row["lag_1"],
                "lag_7": row["lag_7"],
                "rolling_7_mean": round_float(float(row["rolling_7_mean"])),
                "model_forecast": round_float(float(row["model_forecast"])),
                "moving_average_forecast": round_float(float(row["moving_average_forecast"])),
                "dataset_split": "future",
                "absolute_error": "",
            }
        )

    metrics = {
        "model_mae": mae(actual_values, model_predictions),
        "model_mape": mape(actual_values, model_predictions),
        "baseline_mae": mae(actual_values, baseline_predictions),
        "baseline_mape": mape(actual_values, baseline_predictions),
    }
    return output_rows, metrics


def write_report(metrics: dict[str, float]) -> None:
    report = f"""# Отчет по прогнозу обращений

## Качество модели

- mae модели: {metrics["model_mae"]:.2f};
- mape модели: {metrics["model_mape"]:.2f}%;
- mae скользящего среднего: {metrics["baseline_mae"]:.2f};
- mape скользящего среднего: {metrics["baseline_mape"]:.2f}%.

## Интерпретация

Модель использует день недели, месяц, признак выходного дня, лаги и среднее за последние семь дней. она лучше всего подходит для планирования смен на ближайшие одну-две недели, потому что отражает регулярные недельные пики и частично учитывает свежие всплески нагрузки.

Если прогноз выше обычного уровня понедельника или вторника, руководителю поддержки стоит заранее усилить первую линию и проверить backlog по high и critical обращениям. при росте прогноза после инцидентных дней лучше отдельно смотреть категории `integration issue`, `bug report` и `login access`.

## Ограничения

Это baseline без внешних факторов: релизы, маркетинговые кампании, массовые сбои и праздники не передаются модели отдельными признаками. для промышленного сценария стоит добавить календарь релизов, праздники и историю инцидентов.
"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "forecast_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    forecast_rows, metrics = build_forecast_mart()
    write_csv(MARTS_DIR / "mart_forecast.csv", forecast_rows)
    write_report(metrics)
    print(f"forecast mae={metrics['model_mae']:.2f}, mape={metrics['model_mape']:.2f}%")


if __name__ == "__main__":
    main()

