ALTER TABLE courier
ALTER COLUMN working_days TYPE TEXT[] USING STRING_TO_ARRAY(working_days, ', ');
create index courier_working_days on courier using gin (working_days);