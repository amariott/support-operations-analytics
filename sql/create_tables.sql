CREATE TABLE departments (
    department_id TEXT PRIMARY KEY,
    department_name TEXT NOT NULL,
    manager_name TEXT NOT NULL
);

CREATE TABLE customer_segments (
    customer_segment_id TEXT PRIMARY KEY,
    segment_name TEXT NOT NULL,
    sla_multiplier NUMERIC(6, 2) NOT NULL,
    satisfaction_weight NUMERIC(6, 2) NOT NULL
);

CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    department_id TEXT NOT NULL REFERENCES departments(department_id),
    seniority TEXT NOT NULL,
    speed_factor NUMERIC(6, 2) NOT NULL,
    assignment_weight NUMERIC(6, 2) NOT NULL,
    is_overloaded_group TEXT NOT NULL
);

CREATE TABLE calendar (
    date DATE PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name TEXT NOT NULL,
    week_start DATE NOT NULL,
    is_weekend INT NOT NULL,
    is_business_day INT NOT NULL
);

CREATE TABLE tickets (
    ticket_id TEXT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    first_response_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    category TEXT NOT NULL,
    channel TEXT NOT NULL,
    agent_id TEXT NOT NULL REFERENCES agents(agent_id),
    department_id TEXT NOT NULL REFERENCES departments(department_id),
    customer_segment_id TEXT NOT NULL REFERENCES customer_segments(customer_segment_id),
    sla_target_hours INT NOT NULL,
    sla_breached INT NOT NULL,
    first_response_hours NUMERIC(10, 2) NOT NULL,
    resolution_hours NUMERIC(10, 2) NOT NULL,
    satisfaction_score NUMERIC(3, 1)
);

CREATE TABLE ticket_events (
    event_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL REFERENCES tickets(ticket_id),
    event_time TIMESTAMP NOT NULL,
    event_type TEXT NOT NULL,
    old_status TEXT,
    new_status TEXT,
    agent_id TEXT REFERENCES agents(agent_id)
);

