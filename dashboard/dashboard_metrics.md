# Метрики дашборда

## Kpi

- tickets created: количество созданных обращений;
- tickets closed: количество закрытых обращений;
- backlog open tickets: количество открытых обращений на конец дня;
- sla breached tickets: количество обращений с нарушением целевого времени решения;
- sla breach rate: доля обращений с нарушением sla;
- avg first response hours: среднее время до первого ответа;
- avg resolution hours: среднее время решения или текущий возраст открытого обращения;
- avg satisfaction score: средняя оценка клиента по закрытым обращениям;
- forecast tickets: прогноз дневного объема обращений.
- bottleneck score: сумма флагов высокой нагрузки, высокого sla breach rate и длинного resolution time.

## Фильтры

- date;
- week_start;
- department_name;
- agent_name;
- priority;
- category;
- channel;
- is_overloaded_group;
- dataset_split.
- day_of_week.

## Источники

- `mart_sla.csv` для sla и качества;
- `mart_backlog.csv` для backlog;
- `mart_workload.csv` для нагрузки агентов;
- `mart_ticket_volume.csv` для объема обращений;
- `mart_forecast.csv` для прогноза.
- `sla_root_cause_analysis.sql` для анализа причин просрочек по категориям, приоритетам, каналам и периодам;
- `bottleneck_detection.sql` для поиска узких мест на уровне агентов и отделов.
