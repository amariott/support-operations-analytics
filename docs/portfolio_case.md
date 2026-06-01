# Описание для портфолио

## Короткое описание

Аналитика поддержки: sla, backlog, нагрузка команды и прогноз обращений.

## Что сделано

- собран аналитический пайплайн на python и sql для расчета операционных метрик поддержки;
- рассчитаны ticket volume, sla breach rate, resolution time, backlog и workload by agent;
- проанализированы причины sla-просрочек по категориям, приоритетам, каналам и временным периодам;
- подготовлен bi-дашборд для power bi или datalens с kpi, фильтрами и страницами для поиска bottlenecks;
- добавлен прогноз количества обращений на основе календарных признаков, lag features и rolling mean.

## Стек

python, pandas, scikit-learn, sql, power bi / datalens, excel / power query, git.

## Результат

Проект помогает контролировать sla, выявлять узкие места и планировать нагрузку команды поддержки.

## Где это видно в проекте

- python-пайплайн: `src`;
- sql-аналитика: `sql`;
- bi-витрины: `data/marts`;
- дашборд: `dashboard`;
- прогноз: `src/forecast_ticket_volume.py` и `reports/forecast_report.md`;
- описание результата: `reports/project_summary.md`.
