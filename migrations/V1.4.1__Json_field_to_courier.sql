ALTER TABLE courier ADD contacts jsonb;

CREATE OR REPLACE FUNCTION GENERATE_RANDOM_PHONE_NUMBER
() RETURNS VARCHAR AS $$ 
	$$
	DECLARE
	    phone VARCHAR := '+7 ('
	        || LPAD(FLOOR(random() * 1000)::VARCHAR, 3, '0') || ') '
	        || LPAD(FLOOR(random() * 1000)::VARCHAR, 3, '0') || '-'
	        || LPAD(FLOOR(random() * 100)::VARCHAR, 2, '0') || '-'
	        || LPAD(FLOOR(random() * 100)::VARCHAR, 2, '0');
	BEGIN RETURN phone;
	END;
	$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION GENERATE_RANDOM_EMAIL() 
RETURNS VARCHAR AS $$ 
	$$
	DECLARE
	    domains VARCHAR[] := ARRAY['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'example.com'];
	username VARCHAR := '';
	domain VARCHAR := '';
	BEGIN username := 'account' || floor(random() * 1000)::VARCHAR;
	domain := domains [floor(
	    random() * array_length(domains, 1) + 1
	)];
	RETURN username || '@' || domain;
	END;
	$$ LANGUAGE plpgsql;


UPDATE courier
SET
    contacts = json_build_object(
        'phone',
        generate_random_phone_number(),
        'email',
        generate_random_email()
    );

create index courier_contacts on courier using gin (contacts);