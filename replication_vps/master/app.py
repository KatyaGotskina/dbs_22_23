from flask import Flask, request
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Literal
import logging
import os 
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()
connection_param_master = {
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('MASTER_PORT'),
    'database': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

connection_param_slave = {
    'host': os.getenv('SLAVE_HOST'),
    'port': os.getenv('SLAVE_PORT'),
    'database': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

for key in connection_param_master:
    if connection_param_master[key] is None:
        logging.error(f'{key} is None')

for key in connection_param_slave:
    if connection_param_slave[key] is None:
        logging.error(f'{key} is None')


def create_connection_master():
    conn = psycopg2.connect(**connection_param_master,
                            cursor_factory=RealDictCursor)
    conn.autocommit = True
    return conn

def create_connection_slave():
    conn = psycopg2.connect(**connection_param_slave,
                            cursor_factory=RealDictCursor)
    conn.autocommit = True
    return conn

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route("/deliveries")
def get_delivery():
    try:
        query = """with get_orders as (
        select c.id, jsonb_agg(
        jsonb_build_object('order_id', o.id, 'comment', o.comment, 'size', o.size, 'package', o.package, 'time_of_creation', o.time_of_creation, 'delivered', o.delivered)) as courier_orders
        from courier c
            join orders o on c.id = o.courier_id 
            group by c.id
        )
        select d.id as delivery_id, d.address, d.opening_time, d.closing_time, d.brand, 
        coalesce(jsonb_agg(json_build_object('courier_id', c.id, 'vehicle', c.vehicle, 'working_days', c.working_days, 'name', c.name, 'age', c.age, 'orders', gor.courier_orders)) filter (where c.id is not null), '[]') as couriers
        from delivery d
        left join delivery_to_courier dc on d.id = dc.delivery_id
        left join courier c on dc.courier_id = c.id
        left join get_orders gor on gor.id = c.id
        group by d.id;
        """
        with create_connection_slave() as conn, conn.cursor() as cur:
            cur.execute(query)
            deliveries = cur.fetchall()
            for delivery in deliveries:
                delivery['opening_time'] = str(delivery['opening_time'])
                delivery['closing_time'] = str(delivery['closing_time'])
        return deliveries
    except Exception as ex:
        logging.error(ex, exc_info=True)
        return '', 400


@app.route("/deliveries/create", methods=['POST'])
def create_delivery():
    try:
        body = request.json
        opening_time = Literal(datetime.strptime(body['opening_time'], '%H:%M').time())
        closing_time = Literal(datetime.strptime(body['closing_time'], '%H:%M').time())
        query = SQL("""
        insert into delivery(address, opening_time, closing_time, brand) 
        values({address}, {opening_time}, {closing_time}, {brand})
        returning id, address, opening_time, closing_time, brand
        """).format(closing_time=closing_time, address=Literal(body['address']), opening_time=opening_time, brand=Literal(body['brand']))

        with create_connection_master() as conn, conn.cursor() as cur:
            cur.execute(query)
            delivery = cur.fetchone()
            delivery['opening_time'] = str(delivery['opening_time'])
            delivery['closing_time'] = str(delivery['closing_time'])

        return delivery, 201
    except Exception as ex:
        logging.error(ex, exc_info=True)
        return '', 400


@app.route("/deliveries/update", methods=['POST'])
def update_delivery():
    try:
        body = request.json
        opening_time = Literal(datetime.strptime(body['opening_time'], '%H:%M').time())
        closing_time = Literal(datetime.strptime(body['closing_time'], '%H:%M').time())
        query = SQL("""
        update delivery 
        set opening_time = {opening_time}, address = {address}, closing_time = {closing_time}, brand = {brand}
        where id = {id}
        returning id
        """).format(opening_time=opening_time, closing_time=closing_time, id=Literal(body['id']), address=Literal(body['address']), brand = Literal(body['brand']))

        with create_connection_master() as conn, conn.cursor() as cur:
            cur.execute(query)
            updated_rows = cur.fetchall()

        if len(updated_rows) == 0:
            return '', 404

        return '', 200
    except Exception as ex:
        logging.error(ex, exc_info=True)
        return '', 400


@app.route("/deliveries/delete", methods=['DELETE'])
def delete_delivery():
    try:
        body = request.json

        query = SQL("""
        delete from delivery 
        where id = {id}
        returning id
        """).format(id=Literal(body['id']))

        with create_connection_master() as conn, conn.cursor() as cur:
            cur.execute(query)
            deleted_rows = cur.fetchall()

        if len(deleted_rows) == 0:
            return '', 404

        return '', 204
    except Exception as ex:
        logging.error(ex, exc_info=True)
        return '', 400


#http:/127.0.0.1:5000/deliveries/find_by_brand?brand=PizzaHouse
@app.route("/deliveries/find_by_brand")
def brand_search():
    try:
        brand = request.args.get('brand')
        if not brand:
            return '', 404


        query = SQL(f"""with get_orders as (
    select c.id, jsonb_agg(
    jsonb_build_object('order_id', o.id, 'comment', o.comment, 'size', o.size, 'package', o.package, 'time_of_creation', o.time_of_creation, 'delivered', o.delivered)) as courier_orders
    from courier c
        join orders o on c.id = o.courier_id 
        group by c.id
    )
    select d.id as delivery_id, d.address, d.opening_time, d.closing_time, d.brand, 
    coalesce(jsonb_agg(json_build_object('courier_id', c.id, 'vehicle', c.vehicle, 'working_days', c.working_days, 'name', c.name, 'age', c.age, 'orders', gor.courier_orders)) filter (where c.id is not null), '[]') as couriers
    from delivery d
    left join delivery_to_courier dc on d.id = dc.delivery_id
    left join courier c on dc.courier_id = c.id
    left join get_orders gor on gor.id = c.id where brand = '{brand}'
    group by d.id;""".format(brand=Literal(brand)))

        with create_connection_slave() as conn, conn.cursor() as cur:
            cur.execute(query)
            delivery = cur.fetchone()
            delivery['opening_time'] = str(delivery['opening_time'])
            delivery['closing_time'] = str(delivery['closing_time'])

        if delivery is None:
            return '', 404

        return delivery
    except Exception as ex:
        logging.error(ex, exc_info=True)
        return '', 400


#http:/127.0.0.1:5000//working_hours/search?opening_time_from=08:00:00
@app.route("/working_hours/search")
def working_hours_search():
    try:
        opening_time_from = request.args.get('opening_time_from')
        closing_time_to = request.args.get('closing_time_to')

        opening_time_from_condition = "true" if not opening_time_from else "opening_time >= '{opening_time}'"
        closing_time_from_condition = "true" if not closing_time_to else "closing_time <= '{closing_time}'"
        query = SQL(f"""with get_orders as (
        select c.id, jsonb_agg(
        jsonb_build_object('order_id', o.id, 'comment', o.comment, 'size', o.size, 'package', o.package, 'time_of_creation', o.time_of_creation, 'delivered', o.delivered)) as courier_orders
        from courier c
            join orders o on c.id = o.courier_id 
            group by c.id
        )
        select d.id as delivery_id, d.address, d.opening_time, d.closing_time, d.brand, 
        coalesce(jsonb_agg(json_build_object('courier_id', c.id, 'vehicle', c.vehicle, 'working_days', c.working_days, 'name', c.name, 'age', c.age, 'orders', gor.courier_orders)) filter (where c.id is not null), '[]') as couriers
        from delivery d
        left join delivery_to_courier dc on d.id = dc.delivery_id
        left join courier c on dc.courier_id = c.id
        left join get_orders gor on gor.id = c.id where {opening_time_from_condition} and {closing_time_from_condition}
        group by d.id;""".format(closing_time=closing_time_to, opening_time=opening_time_from))

        with create_connection_slave() as conn, conn.cursor() as cur:
            cur.execute(query)
            deliveries = cur.fetchall()
            for delivery in deliveries:
                delivery['opening_time'] = str(delivery['opening_time'])
                delivery['closing_time'] = str(delivery['closing_time'])

        if len(deliveries) == 0:
            return '', 404

        return deliveries
    except Exception as ex:
        logging.error(ex, exc_info=True)
        return '', 400



#http:/127.0.0.1:5000/size/search?size=small
@app.route("/size/search")
def size_search():
    try:
        size = request.args.get('size')

        if not size:
            return '', 404

        query = SQL(f"""with get_orders as (
        select c.id, jsonb_agg(
        jsonb_build_object('order_id', o.id, 'comment', o.comment, 'size', o.size, 'package', o.package, 'time_of_creation', o.time_of_creation, 'delivered', o.delivered)) as courier_orders
        from courier c
            join orders o on c.id = o.courier_id where o.size = '{size}'
            group by c.id
        )
        select d.id as delivery_id, d.address, d.opening_time, d.closing_time, d.brand, 
        coalesce(jsonb_agg(json_build_object('courier_id', c.id, 'vehicle', c.vehicle, 'working_days', c.working_days, 'name', c.name, 'age', c.age, 'orders', gor.courier_orders)) filter (where c.id is not null), '[]') as couriers
        from delivery d
        left join delivery_to_courier dc on d.id = dc.delivery_id
        left join courier c on dc.courier_id = c.id
        left join get_orders gor on gor.id = c.id
        group by d.id;""").format(size=Literal(size))

        with create_connection_slave() as conn, conn.cursor() as cur:
            cur.execute(query)
            deliveries = cur.fetchall()
            for delivery in deliveries:
                delivery['opening_time'] = str(delivery['opening_time'])
                delivery['closing_time'] = str(delivery['closing_time'])

        if len(deliveries) == 0:
            return '', 404

        return deliveries
    except Exception as ex:
        logging.error(ex, exc_info=True)
        return '', 400

if __name__ == '__main__':
    app.run(debug=True)