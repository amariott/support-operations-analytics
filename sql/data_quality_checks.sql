WITH ticket_checks AS (
    SELECT 'tickets' AS table_name, 'duplicate ticket_id' AS check_name, COUNT(*) - COUNT(DISTINCT ticket_id) AS issue_count
    FROM tickets
    UNION ALL
    SELECT 'tickets', 'missing created_at', COUNT(*)
    FROM tickets
    WHERE created_at IS NULL
    UNION ALL
    SELECT 'tickets', 'first response before created', COUNT(*)
    FROM tickets
    WHERE first_response_at < created_at
    UNION ALL
    SELECT 'tickets', 'closed before created', COUNT(*)
    FROM tickets
    WHERE closed_at IS NOT NULL AND closed_at < created_at
    UNION ALL
    SELECT 'tickets', 'negative duration', COUNT(*)
    FROM tickets
    WHERE first_response_hours < 0 OR resolution_hours < 0
),
event_checks AS (
    SELECT 'ticket_events' AS table_name, 'duplicate event_id' AS check_name, COUNT(*) - COUNT(DISTINCT event_id) AS issue_count
    FROM ticket_events
    UNION ALL
    SELECT 'ticket_events', 'events without ticket', COUNT(*)
    FROM ticket_events e
    LEFT JOIN tickets t ON t.ticket_id = e.ticket_id
    WHERE t.ticket_id IS NULL
),
all_checks AS (
    SELECT * FROM ticket_checks
    UNION ALL
    SELECT * FROM event_checks
)
SELECT
    table_name,
    check_name,
    issue_count,
    CASE WHEN issue_count = 0 THEN 'pass' ELSE 'fail' END AS result
FROM all_checks
ORDER BY table_name, check_name;

