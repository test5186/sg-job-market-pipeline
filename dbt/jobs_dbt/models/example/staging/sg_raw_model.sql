with source as (
    select * from {{ source('sg_raw', 'raw_jobs') }}
),

renamed as (
    select
        
        uuid,
        title, 
        "minimumYearsExperience" as min_experience,
        -- skills
        -- categories
        cast("employmentTypes" as JSONB) -> 0 ->> 'employmentType' as employment_types,
        cast("status" as JSONB) ->> 'jobStatus' as status,

        coalesce(
            cast("hiringCompany" as JSONB) ->> 'name',
            cast("postedCompany" as JSONB) ->> 'name'
        ) as company_name,

        cast(salary as JSONB) -> 'type' ->> 'salaryType' as salary_type,
        cast(salary as JSONB) ->> 'minimum' as min_salary,
        cast(salary as JSONB) ->> 'maximum' as max_salary,

        extracted_at 

    from source
    where uuid is not null
)

select * from renamed