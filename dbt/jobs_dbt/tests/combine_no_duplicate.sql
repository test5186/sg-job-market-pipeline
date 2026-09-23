select
    lower(trim(company_name)) as company_key,
    lower(trim(title)) as title_key,
    count(*) as row_count
from {{ ref('combine') }}
group by 1, 2
having count(*) > 1