with jobs as (
    select * from {{ref('data_jobs')}}
),

unnested as (

    select 
        uuid,
        unnest(string_to_array(skills,',')) as skill        
    from jobs 

)

select 
    skill,
    count(*) as jobs_count
from unnested
group by skill 
order by jobs_count desc
