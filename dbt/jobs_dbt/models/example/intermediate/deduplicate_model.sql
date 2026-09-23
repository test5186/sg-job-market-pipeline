with source as (
    select * from {{ ref('sg_raw_model') }}
),

clean as (
    select distinct on (uuid)
        uuid,
        title, 
        min_experience,
        employment_types,
        status,
        company_name,
        salary_type,
        min_salary,
        max_salary,
        extracted_at
    from source
    order by uuid, extracted_at desc
)

select * from clean