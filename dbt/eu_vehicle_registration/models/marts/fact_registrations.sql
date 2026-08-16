select
    year,
    country,
    power_type,
    sum(registrations) as total_registrations
from {{ ref('stg_registrations') }}
group by year, country, power_type
order by year, country, power_type
