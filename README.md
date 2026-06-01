# Support operations analytics

Портфельный проект по операционной аналитике службы поддержки. проект показывает полный цикл работы data / bi analyst: от генерации и проверки данных до sql-аналитики, bi-ready витрин, описания дашборда и baseline-прогноза количества обращений.

## Цель проекта

Проанализировать работу службы поддержки и подготовить аналитическую основу для контроля sla, backlog, нагрузки команды и планирования смен.

Проект отвечает на вопросы:

- сколько обращений приходит по дням, каналам, категориям и приоритетам;
- где чаще всего нарушается sla;
- какие категории, каналы и периоды дают основной вклад в просрочки;
- у каких агентов и отделов появляется перегруз;
- как меняется backlog;
- сколько обращений ожидать в ближайшие дни.

## Стек

- python;
- pandas;
- scikit-learn;
- sql;
- power bi / datalens;
- excel / power query;
- git.

Основные скрипты пайплайна написаны на стандартной библиотеке python, чтобы проект можно было запустить локально без обязательной установки пакетов. зависимости из `requirements.txt` нужны для ноутбуков и расширенного анализа.

## Данные

В проекте используются синтетические данные службы поддержки. они генерируются скриптом `src/generate_data.py` и сохраняются в `data/raw`.

Основные таблицы:

- `tickets.csv` - обращения клиентов;
- `ticket_events.csv` - события по обращениям;
- `agents.csv` - агенты поддержки;
- `departments.csv` - отделы поддержки;
- `customer_segments.csv` - клиентские сегменты;
- `calendar.csv` - календарь для аналитики и прогноза.

В данных есть реалистичные зависимости: недельная сезонность обращений, разные sla targets по приоритетам, более рискованные категории, перегруз части агентов, рост backlog после пиков нагрузки и снижение satisfaction score при долгом resolution time.

## Метрики

В проекте рассчитаны:

- ticket volume;
- sla breached tickets;
- sla breach rate;
- first response time;
- resolution time;
- backlog open tickets;
- workload by agent;
- average satisfaction score;
- forecast tickets;
- bottleneck score.

Описание метрик находится в `docs/metrics_dictionary.md`.

## Структура проекта

```text
support-operations-analytics/
  README.md
  requirements.txt
  data/
    raw/
    processed/
    marts/
  src/
    generate_data.py
    clean_data.py
    build_marts.py
    forecast_ticket_volume.py
    utils.py
  sql/
    create_tables.sql
    sla_metrics.sql
    backlog_analysis.sql
    workload_by_agent.sql
    sla_root_cause_analysis.sql
    bottleneck_detection.sql
    ticket_volume_forecast_dataset.sql
    data_quality_checks.sql
  notebooks/
    01_eda.ipynb
    02_demand_forecast.ipynb
  dashboard/
    dashboard_spec.md
    dashboard_metrics.md
    power_bi_datalens_guide.md
    screenshots_placeholder.md
  docs/
    data_pipeline.md
    metrics_dictionary.md
    dashboard_user_guide.md
    data_quality_checks.md
    portfolio_case.md
  reports/
    forecast_report.md
    project_summary.md
```

## Пайплайн

Пайплайн состоит из четырех шагов:

1. `src/generate_data.py` генерирует исходные csv-таблицы.
2. `src/clean_data.py` проверяет пропуски, дубли, даты и отрицательные длительности.
3. `src/build_marts.py` собирает bi-ready витрины.
4. `src/forecast_ticket_volume.py` строит прогноз дневного количества обращений.

Результаты сохраняются в:

- `data/processed` - очищенные таблицы;
- `data/marts` - витрины для bi и анализа;
- `reports/forecast_report.md` - отчет по прогнозу.

## Как запустить

Запуск полного пайплайна:

```bash
python3 src/generate_data.py
python3 src/clean_data.py
python3 src/build_marts.py
python3 src/forecast_ticket_volume.py
```

Установка зависимостей для ноутбуков:

```bash
python3 -m pip install -r requirements.txt
```

После запуска проверьте:

- `data/processed/data_quality_summary.csv`;
- `data/marts/mart_sla.csv`;
- `data/marts/mart_backlog.csv`;
- `data/marts/mart_workload.csv`;
- `data/marts/mart_ticket_volume.csv`;
- `data/marts/mart_forecast.csv`;
- `reports/forecast_report.md`.

## Sql-аналитика

В папке `sql` находятся запросы для аналитики поддержки:

- `sla_metrics.sql` - расчет sla breach rate;
- `backlog_analysis.sql` - динамика backlog;
- `workload_by_agent.sql` - нагрузка агентов;
- `sla_root_cause_analysis.sql` - причины sla-просрочек по категориям, приоритетам, каналам и периодам;
- `bottleneck_detection.sql` - поиск узких мест по агентам и отделам;
- `ticket_volume_forecast_dataset.sql` - подготовка датасета для прогноза;
- `data_quality_checks.sql` - проверки качества данных.

Запросы используют cte, join, агрегации, оконные функции и фильтрацию по операционным разрезам.

## Bi-дашборд

Проект не содержит фейковый `.pbix`, но включает готовые csv-витрины и подробную спецификацию дашборда.

Документы для сборки:

- `dashboard/dashboard_spec.md` - страницы дашборда;
- `dashboard/dashboard_metrics.md` - kpi, фильтры и источники;
- `dashboard/power_bi_datalens_guide.md` - инструкция для power bi / datalens и power query;
- `dashboard/screenshots_placeholder.md` - место для будущих скриншотов.

Рекомендуемые страницы дашборда:

- обзор поддержки;
- sla и причины просрочек;
- нагрузка команды;
- прогноз обращений.

## Прогноз

Прогноз строится для дневного количества обращений. в модели используются:

- day of week;
- month;
- is weekend;
- lag features;
- rolling mean.

Скрипт `src/forecast_ticket_volume.py` сравнивает baseline-модель со скользящим средним и сохраняет результат в `data/marts/mart_forecast.csv`.

Текущий отчет: `reports/forecast_report.md`.

## Результат

Проект помогает:

- контролировать sla;
- видеть рост backlog;
- находить категории и каналы с повышенным риском просрочек;
- выявлять bottlenecks в команде поддержки;
- планировать нагрузку агентов по прогнозу обращений;
- подготовить данные для power bi, datalens или excel / power query.

Краткое описание для портфолио находится в `docs/portfolio_case.md`.
