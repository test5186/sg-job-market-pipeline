-- Materialized as a table (not the default view): as a view, this JSONB 
-- unnest+aggregate gets re-executed per query
{{ config(materialized='table') }}

with source as (
    select uuid,categories from {{ source('sg_raw', 'raw_jobs') }}
),

unnested as (
    select
        uuid,
        cartegories_obj ->> 'category' as category

    from source,
        jsonb_array_elements(cast(categories as JSONB)) as cartegories_obj
    
    where uuid is not null
)

select 
    uuid,
    string_agg(distinct category,','order by category) as all_category

from unnested
group by uuid