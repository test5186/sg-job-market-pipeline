with source as (
    select * from {{ ref('adzuna_raw_model') }}
),

clean as (
    select distinct on (uuid)
        uuid,
        title,
        employment_types,
        contract_time,
        company_name,
        date_created,
        min_salary,
        max_salary,
        location,
        category,
        description,

        extracted_at 
        
    from source
    order by uuid, extracted_at desc
)

select * from clean