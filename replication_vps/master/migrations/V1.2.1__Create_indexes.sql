create index invert_delivery_brand on delivery using gin(to_tsvector('russian', brand));  

create extension if not exists pg_trgm;
create index ngram_delivery_brand on delivery using gin(brand gin_trgm_ops);

create extension if not exists fuzzystrmatch;