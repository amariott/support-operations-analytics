WITH agent_daily AS (
    SELECT
        DATE(t.created_at) AS date,
        a.agent_id,
        a.agent_name,
        d.department_name,
        a.seniority,
        a.is_overloaded_group,
        COUNT(*) AS assigned_tickets,
        COUNT(*) FILTER (WHERE t.closed_at IS NOT NULL) AS resolved_tickets,
        SUM(t.sla_breached) AS sla_breached_tickets,
        AVG(t.resolution_hours) AS avg_resolution_hours,
        AVG(t.satisfaction_score) AS avg_satisfaction_score
    FROM tickets t
    JOIN agents a ON a.agent_id = t.agent_id
    JOIN departments d ON d.department_id = a.department_id
    GROUP BY DATE(t.created_at), a.agent_id, a.agent_name, d.department_name, a.seniority, a.is_overloaded_group
),
with_department_benchmark AS (
    SELECT
        *,
        AVG(assigned_tickets) OVER (PARTITION BY date, department_name) AS department_avg_assigned,
        assigned_tickets - AVG(assigned_tickets) OVER (PARTITION BY date, department_name) AS load_vs_department_avg,
        ROUND(100.0 * sla_breached_tickets / NULLIF(assigned_tickets, 0), 2) AS sla_breach_rate
    FROM agent_daily
)
SELECT *
FROM with_department_benchmark
ORDER BY date, department_name, assigned_tickets DESC;

