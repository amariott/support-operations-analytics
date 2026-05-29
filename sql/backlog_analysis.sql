WITH day_ticket_state AS (
    SELECT
        c.date,
        c.week_start,
        t.ticket_id,
        t.priority,
        t.department_id,
        t.created_at,
        t.closed_at,
        t.sla_target_hours,
        t.sla_breached,
        CASE
            WHEN t.created_at::date <= c.date
             AND (t.closed_at IS NULL OR t.closed_at::date > c.date)
            THEN 1 ELSE 0
        END AS is_open_at_day_end
    FROM calendar c
    JOIN tickets t ON t.created_at::date <= c.date
),
daily_backlog AS (
    SELECT
        date,
        week_start,
        COUNT(*) FILTER (WHERE is_open_at_day_end = 1) AS backlog_open_tickets,
        COUNT(*) FILTER (WHERE is_open_at_day_end = 1 AND priority IN ('high', 'critical')) AS high_priority_backlog,
        COUNT(*) FILTER (WHERE is_open_at_day_end = 1 AND sla_breached = 1) AS breached_backlog,
        AVG(EXTRACT(EPOCH FROM (date + INTERVAL '23 hours 59 minutes' - created_at)) / 3600)
            FILTER (WHERE is_open_at_day_end = 1) AS avg_open_age_hours
    FROM day_ticket_state
    GROUP BY date, week_start
),
with_trend AS (
    SELECT
        *,
        backlog_open_tickets - LAG(backlog_open_tickets) OVER (ORDER BY date) AS backlog_delta,
        AVG(backlog_open_tickets) OVER (
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS backlog_rolling_7d
    FROM daily_backlog
)
SELECT *
FROM with_trend
ORDER BY date;

