with sg as (
    select
        uuid,
        title,
        skills,
        all_category,
        min_experience,
        employment_types,
        status,
        company_name,
        salary_type,
        min_salary,
        max_salary,
        extracted_at,
        'mycareersfuture' as source
    from {{ ref('sg_complete') }}
),

adzuna as (
    select
        uuid,
        title,
        null as skills, -- Adzuna doesn't have skill list
        category as all_category,
        cast(null as bigint) as min_experience, --sg.min_experience is bigint, untyped null would fail the union
        employment_types,
        null as status,
        company_name,
        null as salary_type,
        cast(min_salary as text) as min_salary,
        cast(max_salary as text) as max_salary,
        extracted_at,
        'adzuna' as source
    from {{ ref('adzuna_deduplicate') }}
),

combined as (
    select * from sg
    union all
    select * from adzuna
),

deduped as (
    select *,
    row_number() over (
        -- catches the same posting scraped from both sources if both company name and title is the same
        partition by lower(trim(company_name)), lower(trim(title)) 
            case 
                when source = 'mycareersfuture' then 0  -- prefer MCF
                else 1 
            end,
            extracted_at desc
    ) as rn
    from combined
)


select
    uuid, 
    title, 
    skills, 
    all_category, 
    min_experience, 
    employment_types,
    status, 
    company_name, 
    salary_type, 
    min_salary, 
    max_salary, 
    extracted_at, 
    source
from deduped
where rn = 1
order by extracted_at desc