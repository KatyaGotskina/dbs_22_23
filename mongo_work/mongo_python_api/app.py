from flask import Flask, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from json import loads


client = MongoClient("mongodb://mongo:mongo@localhost:37112")
app = Flask(__name__)

@app.route('/')
def hello_word():
    movie_deteils = client.test.movieDetails
    movie = movie_deteils.find_one({"rated": "R"})
    return jsonify(loads(dumps(movie)))

if __name__ == '__main__':
    app.run(debug=True)