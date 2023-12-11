CREATE MATERIALIZED VIEW delivery_view AS (
    WITH get_orders AS (
        SELECT c.id, jsonb_agg(
            jsonb_build_object('order_id', o.id, 'comment', o.comment, 'size', o.size, 'package', o.package, 'time_of_creation', o.time_of_creation, 'delivered', o.delivered)
        ) AS courier_orders
        FROM courier c
        JOIN orders o ON c.id = o.courier_id 
        GROUP BY c.id
    )
    SELECT d.id AS delivery_id, d.address, d.opening_time, d.closing_time, d.brand, 
    COALESCE(jsonb_agg(json_build_object('courier_id', c.id, 'vehicle', c.vehicle, 'working_days', c.working_days, 'contacts', c.contacts, 'name', c.name, 'age', c.age, 'orders', gor.courier_orders)) FILTER (WHERE c.id IS NOT NULL), '[]') AS couriers
    FROM delivery d
    LEFT JOIN delivery_to_courier dc ON d.id = dc.delivery_id
    LEFT JOIN courier c ON dc.courier_id = c.id
    LEFT JOIN get_orders gor ON gor.id = c.id
    GROUP BY d.id
);

-- для того чтобы refresh не блокировал чтение из представления
CREATE UNIQUE INDEX unique_delivery_id ON delivery_view (delivery_id);

create function delivery_view_refresh()
	returns trigger as
$$
begin
	refresh materialized view concurrently delivery_view;
	return new;
end;
$$
	language 'plpgsql';

create trigger delivery_table_update
	after insert or update or delete
	on delivery
	for each row
execute function delivery_view_refresh();

create trigger courier_table_update
	after insert or update or delete
	on courier
	for each row
execute function delivery_view_refresh();

create trigger orders_table_update
	after insert or update or delete
	on orders
	for each row
execute function delivery_view_refresh();