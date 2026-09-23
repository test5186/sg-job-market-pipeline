with source as (
    select * from {{ source('adzuna_raw', 'adzuna_jobs') }}
),

renamed as (
    select
        
        id as uuid,
        title,
        initcap(contract_type) as employment_types,
        initcap(contract_time) as contract_time,
        company ->> 'display_name' as company_name,
        created as date_created,
        salary_min as min_salary,
        salary_max as max_salary,
        location ->> 'display_name' as location,
        category ->> 'tag' as category,
        description,

        extracted_at 


    from source
    where id is not null
)

select * from renamed