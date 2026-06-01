WITH ticket_base AS (
    SELECT
        t.ticket_id,
        DATE(t.created_at) AS created_date,
        c.week_start,
        c.month,
        c.day_of_week,
        d.department_name,
        t.category,
        t.priority,
        t.channel,
        t.sla_breached,
        t.resolution_hours,
        t.first_response_hours,
        t.satisfaction_score
    FROM tickets t
    JOIN departments d ON d.department_id = t.department_id
    JOIN calendar c ON c.date = DATE(t.created_at)
),
root_cause_segments AS (
    SELECT
        week_start,
        month,
        day_of_week,
        department_name,
        category,
        priority,
        channel,
        COUNT(*) AS tickets_created,
        SUM(sla_breached) AS sla_breached_tickets,
        AVG(resolution_hours) AS avg_resolution_hours,
        AVG(first_response_hours) AS avg_first_response_hours,
        AVG(satisfaction_score) AS avg_satisfaction_score
    FROM ticket_base
    GROUP BY
        week_start,
        month,
        day_of_week,
        department_name,
        category,
        priority,
        channel
),
with_rates AS (
    SELECT
        *,
        ROUND(100.0 * sla_breached_tickets / NULLIF(tickets_created, 0), 2) AS sla_breach_rate,
        SUM(sla_breached_tickets) OVER (PARTITION BY week_start) AS weekly_breaches_total,
        ROUND(
            100.0 * sla_breached_tickets / NULLIF(SUM(sla_breached_tickets) OVER (PARTITION BY week_start), 0),
            2
        ) AS breach_contribution_rate
    FROM root_cause_segments
),
ranked_segments AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY week_start
            ORDER BY breach_contribution_rate DESC, sla_breach_rate DESC, tickets_created DESC
        ) AS weekly_bottleneck_rank
    FROM with_rates
)
SELECT
    week_start,
    month,
    day_of_week,
    department_name,
    category,
    priority,
    channel,
    tickets_created,
    sla_breached_tickets,
    sla_breach_rate,
    breach_contribution_rate,
    avg_resolution_hours,
    avg_first_response_hours,
    avg_satisfaction_score,
    weekly_bottleneck_rank
FROM ranked_segments
WHERE tickets_created >= 3
ORDER BY week_start, weekly_bottleneck_rank, sla_breach_rate DESC;

