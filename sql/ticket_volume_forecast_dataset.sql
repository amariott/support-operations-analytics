WITH daily_volume AS (
    SELECT
        c.date,
        c.day_of_week,
        c.month,
        c.is_weekend,
        COUNT(t.ticket_id) AS actual_tickets
    FROM calendar c
    LEFT JOIN tickets t ON DATE(t.created_at) = c.date
    GROUP BY c.date, c.day_of_week, c.month, c.is_weekend
),
features AS (
    SELECT
        *,
        LAG(actual_tickets, 1) OVER (ORDER BY date) AS lag_1,
        LAG(actual_tickets, 7) OVER (ORDER BY date) AS lag_7,
        AVG(actual_tickets) OVER (
            ORDER BY date
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) AS rolling_7_mean
    FROM daily_volume
)
SELECT *
FROM features
WHERE lag_7 IS NOT NULL
ORDER BY date;

