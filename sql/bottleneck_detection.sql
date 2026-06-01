WITH agent_daily AS (
    SELECT
        DATE(t.created_at) AS date,
        c.week_start,
        a.agent_id,
        a.agent_name,
        d.department_name,
        a.seniority,
        a.is_overloaded_group,
        COUNT(*) AS assigned_tickets,
        SUM(t.sla_breached) AS sla_breached_tickets,
        AVG(t.resolution_hours) AS avg_resolution_hours,
        AVG(t.satisfaction_score) AS avg_satisfaction_score
    FROM tickets t
    JOIN agents a ON a.agent_id = t.agent_id
    JOIN departments d ON d.department_id = a.department_id
    JOIN calendar c ON c.date = DATE(t.created_at)
    GROUP BY
        DATE(t.created_at),
        c.week_start,
        a.agent_id,
        a.agent_name,
        d.department_name,
        a.seniority,
        a.is_overloaded_group
),
benchmarks AS (
    SELECT
        *,
        AVG(assigned_tickets) OVER (PARTITION BY date, department_name) AS department_avg_assigned,
        AVG(sla_breached_tickets) OVER (PARTITION BY date, department_name) AS department_avg_breaches,
        ROUND(100.0 * sla_breached_tickets / NULLIF(assigned_tickets, 0), 2) AS sla_breach_rate
    FROM agent_daily
),
bottleneck_flags AS (
    SELECT
        *,
        CASE WHEN assigned_tickets > department_avg_assigned * 1.25 THEN 1 ELSE 0 END AS high_load_flag,
        CASE WHEN sla_breached_tickets > department_avg_breaches * 1.25 THEN 1 ELSE 0 END AS high_breach_flag,
        CASE WHEN avg_resolution_hours > 48 THEN 1 ELSE 0 END AS slow_resolution_flag
    FROM benchmarks
)
SELECT
    date,
    week_start,
    agent_id,
    agent_name,
    department_name,
    seniority,
    is_overloaded_group,
    assigned_tickets,
    sla_breached_tickets,
    sla_breach_rate,
    avg_resolution_hours,
    avg_satisfaction_score,
    high_load_flag,
    high_breach_flag,
    slow_resolution_flag,
    high_load_flag + high_breach_flag + slow_resolution_flag AS bottleneck_score
FROM bottleneck_flags
WHERE high_load_flag + high_breach_flag + slow_resolution_flag > 0
ORDER BY date, bottleneck_score DESC, assigned_tickets DESC;

