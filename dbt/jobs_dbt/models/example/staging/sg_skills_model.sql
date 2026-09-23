{{ config(materialized='table') }}

with source as (
    select uuid,skills from {{ source('sg_raw', 'raw_jobs') }}
),

unnested as (
    select
        uuid,
        skills_obj ->> 'skill' as skill_name

    from source,
        jsonb_array_elements(cast(skills as JSONB)) as skills_obj
    
    where uuid is not null
)

select 
    uuid,
    string_agg(distinct skill_name,','order by skill_name) as skills

from unnested
group by uuid