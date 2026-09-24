-- Filters the combined dataset down to permanent "data engineer" roles
select * 
from {{ref('combine')}} 
where title ilike '%data engineer%' 
and employment_types ilike '%permanent%'