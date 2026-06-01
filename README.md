# Support operations analytics

Проект по операционной аналитике службы поддержки: обращения, sla, backlog, нагрузка агентов, витрины для bi-дашборда и базовый прогноз дневного объема тикетов.

## Что внутри

- синтетические данные службы поддержки в `data/raw`;
- проверка и очистка данных в `data/processed`;
- готовые bi-витрины в `data/marts`;
- sql-аналитика для sla, backlog, нагрузки, причин просрочек и качества данных;
- два ноутбука для eda и прогноза спроса;
- документация для метрик, пайплайна и сборки дашборда в power bi или datalens.


## Как запустить

Скрипты используют стандартную библиотеку python и могут запускаться без установки пакетов:

```bash
python3 src/generate_data.py
python3 src/clean_data.py
python3 src/build_marts.py
python3 src/forecast_ticket_volume.py
```

Для работы с ноутбуками установите зависимости:

```bash
python3 -m pip install -r requirements.txt
```

## Основные артефакты

- `data/raw/tickets.csv` - исходная таблица обращений;
- `data/raw/ticket_events.csv` - история событий по тикетам;
- `data/marts/mart_sla.csv` - показатели sla по датам, отделам и приоритетам;
- `data/marts/mart_backlog.csv` - динамика backlog;
- `data/marts/mart_workload.csv` - нагрузка и качество работы агентов;
- `data/marts/mart_ticket_volume.csv` - объем обращений по ключевым разрезам;
- `data/marts/mart_forecast.csv` - факт и прогноз объема тикетов;
- `reports/forecast_report.md` - краткая бизнес-интерпретация прогноза;
- `sql/sla_root_cause_analysis.sql` - анализ причин sla-просрочек;
- `dashboard/power_bi_datalens_guide.md` - инструкция сборки bi-дашборда;
- `docs/portfolio_case.md` - готовое описание проекта для портфолио.

## Проверка результата

После запуска пайплайна проверьте:

- в `data_quality_summary.csv` нет критичных ошибок;
- витрины обновились в `data/marts`;
- отчет прогноза содержит mae и mape;
- sql-скрипты соответствуют вашей целевой базе;
- структура дашборда в `dashboard/dashboard_spec.md` покрывает нужные страницы.
