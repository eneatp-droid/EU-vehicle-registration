with source_data as (
    select
        country,
        cast(year as integer) as year,
        lower(trim(power_type)) as power_type,
        cast(registrations as bigint) as registrations
    from {{ source('raw', 'stg_registros_veiculos') }}
)

select *
from source_data
where country is not null
  and power_type is not null
  and registrations is not null
