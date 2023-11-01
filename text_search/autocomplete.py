from flask import Flask, request, jsonify, send_file
import psycopg2
import os
from psycopg2.extras import RealDictCursor, Json
from dotenv import load_dotenv
from psycopg2.sql import SQL, Literal
import logging
from flask_cors import CORS


load_dotenv()
app = Flask(__name__)
CORS(app)

pg_connection_parameters = {
    'host': os.getenv('POSTGRES_HOST') or 'localhost',
    'port': os.getenv('POSTGRES_PORT'),
    'database': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

def create_pg_connection():
    conn = psycopg2.connect(**pg_connection_parameters,
                            cursor_factory=RealDictCursor)
    conn.autocommit = True
    return conn


@app.route('/')
def autocomplete_page():
    try:
        return send_file("app.html")
    except Exception as ex:
        logging.error(repr(ex), exc_info=True)
        return {'message': 'Bad Request'}, 400


@app.route('/autocomplete')
def autocomplete():
    try:
        word = request.args.get('word')

        query = SQL("select * from delivery where brand %> {word}").format(word=Literal(word))

        with create_pg_connection() as conn, conn.cursor() as cur:
            cur.execute(query)
            deliveries = cur.fetchall()
        return jsonify(list(map(lambda row: row['brand'], deliveries)))
    except Exception as ex:
        logging.error(repr(ex), exc_info=True)
        print(ex)
        return {'message': 'Bad Request'}, 400

@app.route("/levenshtein", methods=["POST"])
def levenshtein():
    request_data = request.get_json()
    word = request_data.get('word', '')
    if not word:
        return {'message': 'Bad Request'}, 400
    query = SQL("select * from delivery where levenshtein(brand, {word}) <= 2;").format(word=Literal(word))
    with create_pg_connection() as conn, conn.cursor() as cur:
            cur.execute(query)
            deliveries = cur.fetchall()
    return jsonify(list(map(lambda row: row['brand'], deliveries)))

@app.route("/get_courier", methods=["POST"])
def get_courier():
    request_data = request.get_json()
    days = request_data.get('day', '')
    if not days:
        return {'message': 'Bad Request'}, 400
    query = SQL("SELECT * FROM courier WHERE working_days && {days};").format(days=Literal(days))
    with create_pg_connection() as conn, conn.cursor() as cur:
            cur.execute(query)
            couriers = cur.fetchall()
    for courier in couriers:
        del courier['id']
    return jsonify(couriers)

@app.route("/get_courier_contacts", methods=["POST"])
def get_courier_contacts():
    request_data = request.get_json()

    body = request.get_json()
    # Лучше будет так 
    """
    phone = body.get('phone')
    email = body.get('email')
    """

    if not request_data:
        return {'message': 'Bad Request'}, 400
    query = SQL('select * from courier where contacts @> "[%s]"')
    # Лучше будет так 
    """query = SQL('select * from courier where contacts @> {"phone": %s} or contacts @> {"email": %s}')"""
    with create_pg_connection() as conn, conn.cursor() as cur:
            cur.execute(query, (Json(request_data), ))
            couriers = cur.fetchall()
    for courier in couriers:
        del courier['id']
    return jsonify(couriers)

if __name__ == '__main__':
    app.run(debug=True)
