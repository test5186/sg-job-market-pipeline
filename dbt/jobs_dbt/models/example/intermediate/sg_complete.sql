with t1 as (
    select * from {{ ref('deduplicate_model') }}
),

t2 as (
    select * from {{ ref('sg_categories_model') }}
),

t3 as (
    select * from {{ ref('sg_skills_model') }}
),

final as (
    select 
        t1.uuid,
        t1.title, 
        t3.skills,
        t2.all_category,
        t1.min_experience,
        t1.employment_types,
        t1.status,
        t1.company_name,
        t1.salary_type,
        t1.min_salary,
        t1.max_salary,
        t1.extracted_at
        
    from t1
    left join t3 on t1.uuid = t3.uuid
    left join t2 on t1.uuid = t2.uuid
    order by t1.extracted_at desc
)

select * from final