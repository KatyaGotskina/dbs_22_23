from flask import Flask, request
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Literal
import logging
import os 
from dotenv import load_dotenv
from datetime import datetime



load_dotenv()
pg_connection_parameters = {
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
    'database': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD')
}


for key in pg_connection_parameters:
    if pg_connection_parameters[key] is None:
        logging.error(f'{key} is None')


def create_pg_connection():
    conn = psycopg2.connect(**pg_connection_parameters,
                            cursor_factory=RealDictCursor)
    conn.autocommit = True
    return conn


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route("/")
@app.route("/deliveries")
def get_delivery():
    try:
        query = """select * from delivery_view;"""
        with create_pg_connection() as conn, conn.cursor() as cur:
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
        print()
        a = datetime.strptime(body['opening_time'], '%H:%M:%S').time()
        print(a, f'type : {type(a)}')
        print()
        opening_time = Literal(datetime.strptime(body['opening_time'], '%H:%M:%S').time())
        closing_time = Literal(datetime.strptime(body['closing_time'], '%H:%M:%S').time())
        query = SQL("""
        insert into delivery(address, opening_time, closing_time, brand) 
        values({address}, {opening_time}, {closing_time}, {brand})
        returning id, address, opening_time, closing_time, brand
        """).format(closing_time=closing_time, address=Literal(body['address']), opening_time=opening_time, brand=Literal(body['brand']))

        with create_pg_connection() as conn, conn.cursor() as cur:
            cur.execute(query)
            delivery = cur.fetchone()
            delivery['opening_time'] = str(delivery['opening_time'])
            delivery['closing_time'] = str(delivery['closing_time'])

        return delivery
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

        with create_pg_connection() as conn, conn.cursor() as cur:
            cur.execute(query)
            deleted_rows = cur.fetchall()

        if len(deleted_rows) == 0:
            return '', 404

        return '', 204
    except Exception as ex:
        logging.error(ex, exc_info=True)
        return '', 400

if __name__ == '__main__':
    app.run(debug=True)
