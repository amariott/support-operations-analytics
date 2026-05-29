WITH ticket_base AS (
    SELECT
        t.ticket_id,
        DATE(t.created_at) AS created_date,
        c.week_start,
        d.department_name,
        t.priority,
        t.category,
        t.channel,
        t.sla_target_hours,
        t.sla_breached,
        t.first_response_hours,
        t.resolution_hours,
        t.satisfaction_score
    FROM tickets t
    JOIN departments d ON d.department_id = t.department_id
    JOIN calendar c ON c.date = DATE(t.created_at)
),
weekly_metrics AS (
    SELECT
        week_start,
        department_name,
        priority,
        COUNT(*) AS tickets_created,
        SUM(sla_breached) AS sla_breached_tickets,
        AVG(first_response_hours) AS avg_first_response_hours,
        AVG(resolution_hours) AS avg_resolution_hours,
        AVG(satisfaction_score) AS avg_satisfaction_score
    FROM ticket_base
    GROUP BY week_start, department_name, priority
),
ranked AS (
    SELECT
        *,
        ROUND(100.0 * sla_breached_tickets / NULLIF(tickets_created, 0), 2) AS sla_breach_rate,
        RANK() OVER (
            PARTITION BY week_start
            ORDER BY 100.0 * sla_breached_tickets / NULLIF(tickets_created, 0) DESC
        ) AS weekly_risk_rank
    FROM weekly_metrics
)
SELECT *
FROM ranked
ORDER BY week_start, weekly_risk_rank, department_name, priority;

