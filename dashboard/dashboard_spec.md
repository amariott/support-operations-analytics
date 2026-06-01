# Спецификация дашборда

Дашборд рассчитан на сборку в power bi или datalens. источники данных лежат в `data/marts`, а подготовка через excel / power query описана в `dashboard/power_bi_datalens_guide.md`.

## Страница 1: обзор поддержки

Основной экран для руководителя поддержки. показывает дневной объем обращений, текущий backlog, долю нарушений sla, среднее время первого ответа и среднюю оценку удовлетворенности.

Рекомендуемые визуализации:

- карточки kpi: tickets created, backlog open tickets, sla breach rate, avg first response hours, avg satisfaction score;
- линейный график дневного объема обращений;
- линейный график backlog по дням;
- столбчатый график нарушений sla по отделам;
- фильтры по дате, отделу, приоритету, каналу и сегменту клиента.

## Страница 2: sla и качество

Экран для поиска проблемных зон. сравнивает отделы, категории и приоритеты по нарушениям sla и времени решения.

Рекомендуемые визуализации:

- heatmap `department_name` x `priority` по sla breach rate;
- bar chart категорий, каналов и периодов с максимальной долей нарушений;
- scatter plot `resolution_hours` x `satisfaction_score`;
- таблица топ проблемных комбинаций отдел-категория-приоритет.

## Страница 3: нагрузка команды

Экран для тимлида. показывает распределение обращений между агентами и влияние перегруза на качество.

Рекомендуемые визуализации:

- bar chart assigned tickets по агентам;
- bar chart open backlog по агентам;
- table с agent name, seniority, assigned tickets, sla breach rate, avg satisfaction score;
- таблица bottlenecks: агент, отдел, нагрузка, backlog, sla breach rate, resolution time;
- фильтр `is_overloaded_group`.

## Страница 4: прогноз спроса

Экран для планирования смен. использует `mart_forecast.csv` и сравнивает факт, модель и скользящее среднее.

Рекомендуемые визуализации:

- line chart actual tickets и model forecast;
- line chart moving average forecast;
- карточки mae и mape из отчета;
- таблица будущих дат с прогнозом.
