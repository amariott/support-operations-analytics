# Сборка дашборда в power bi или datalens

## Цель

Дашборд нужен для мониторинга нагрузки поддержки, контроля sla, поиска bottlenecks и планирования смен по прогнозу обращений.

## Источники данных

Загрузите csv из папки `data/marts`:

- `mart_sla.csv`;
- `mart_backlog.csv`;
- `mart_workload.csv`;
- `mart_ticket_volume.csv`;
- `mart_forecast.csv`.

## Power query

Рекомендуемые шаги в excel или power bi:

- импортировать csv через `get data`;
- привести `date` и `week_start` к типу date;
- привести `ticket_count`, `tickets_created`, `tickets_closed`, `assigned_tickets`, `open_backlog`, `backlog_open_tickets` к whole number;
- привести `sla_breach_rate`, `avg_resolution_hours`, `avg_first_response_hours`, `avg_satisfaction_score`, `model_forecast` к decimal number;
- проверить, что пустые значения в forecast не превращаются в нули;
- назвать запросы так же, как файлы витрин.

## Модель данных

Для простой версии можно оставить витрины независимыми и связывать страницы дашборда только фильтрами внутри каждой страницы.

Для расширенной версии создайте календарную таблицу и связи:

- `calendar[date]` -> `mart_sla[date]`;
- `calendar[date]` -> `mart_backlog[date]`;
- `calendar[date]` -> `mart_workload[date]`;
- `calendar[date]` -> `mart_ticket_volume[date]`;
- `calendar[date]` -> `mart_forecast[date]`.

## Меры для power bi

```text
tickets created = sum(mart_sla[tickets_created])
sla breached tickets = sum(mart_sla[sla_breached_tickets])
sla breach rate = divide([sla breached tickets], [tickets created])
avg resolution hours = average(mart_sla[avg_resolution_hours])
avg first response hours = average(mart_sla[avg_first_response_hours])
backlog open tickets = sum(mart_backlog[backlog_open_tickets])
assigned tickets = sum(mart_workload[assigned_tickets])
open backlog by agent = sum(mart_workload[open_backlog])
forecast tickets = sum(mart_forecast[model_forecast])
```

## Страницы

Соберите четыре страницы:

- обзор поддержки: kpi, ticket volume, backlog, sla breach rate;
- sla и причины просрочек: category, priority, channel, week_start, day_of_week;
- нагрузка команды: workload by agent, open backlog, overloaded group, bottleneck score;
- прогноз обращений: actual tickets, model forecast, moving average forecast.

## Что считать bottleneck

Узкое место можно считать найденным, если одновременно видны:

- высокая нагрузка агента или отдела;
- высокий sla breach rate;
- длинный resolution time;
- растущий backlog;
- падение satisfaction score.

