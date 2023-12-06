select * from some_table where colomn like '%кошка%';

CREATE INDEX gin_sample on some_table using gin(to_tsvector('russian', colomn))

select * from some_table where to_tsvector('russian', colomn) @@ to_tsquery('russian', 'кошка')

create extension if not EXISTS fuzzystrmatch;
select title from equipment where levenshtein(title, 'Полатка') < 3;
-- SQL injections
