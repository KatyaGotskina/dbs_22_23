import express from 'express'
import bodyParser from 'body-parser'
import { MongoClient, ObjectId } from 'mongodb'
import { config } from 'dotenv'

config()

const { MONGO_USER, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT, MONGO_DB, EXPRESS_PORT } = process.env

const client = new MongoClient(`mongodb://${MONGO_USER}:${MONGO_PASSWORD}@${MONGO_HOST}:${MONGO_PORT}`)
const db = client.db(MONGO_DB)

const app = express()
app.use(bodyParser.json())
const appPort = EXPRESS_PORT

app.get('/', (_, res) => {
    res.send('')
})

app.get('/movies', async (_, res) => {
    try {
        const movies = await db
            .collection('movieDetails')
            .find({}, { limit: 10, sort: { _id: -1 } })
            .toArray()

        res.json(movies)
    } catch (err) {
        console.log(err)
        res.sendStatus(400)
    }
})

app.post('/movies/create', async (req, res) => {
    try {
        const { title, year, runtime, countries, genres, director, writers, actors } = req.body
        const { insertedId } = await db
            .collection('movieDetails')
            .insertOne({ title, year, runtime, countries, genres, director, writers, actors })

        res.json({ id: insertedId })
    } catch (err) {
        console.log(err)
        res.sendStatus(400)
    }
})

app.post('/movies/update', async (req, res) => {
    try {
        const { id, title, year, runtime, countries, genres, director, writers, actors } = req.body
        const result = await db
            .collection('movieDetails')
            .updateOne(
                { _id: new ObjectId(id) },
                { $set: { title, year, runtime, countries, genres, director, writers, actors } }
            )

        if (result.matchedCount === 0) {
            res.sendStatus(404)
        } else {
            res.sendStatus(204)
        }
    } catch (err) {
        console.log(err)
        res.sendStatus(400)
    }
})

app.delete('/movies/delete', async (req, res) => {
    try {
        const { id } = req.body
        const { deletedCount } = await db.collection('movieDetails').deleteOne({ _id: new ObjectId(id) })

        if (deletedCount === 0) {
            res.sendStatus(404)
        } else {
            res.sendStatus(204)
        }
    } catch (err) {
        console.log(err)
        res.sendStatus(400)
    }
})

app.listen(appPort, () => {
    console.log(`app listening on port ${appPort}`)
})


//примеры апдейтов в mongo
db.movieDetails.updateOne({ title: 'some_title' }, { $set: {runtime: 104, 'imdb.rating': 8.3 } })
db.movieDetails.updateOne({ title: 'some_title' }, { $set: {'actors.0': 'some_new_actor' } })
db.movieDetails.updateOne({ title: 'some_title', actors: 'some_new_actor' }, { $set: {'actors.$': 'new_actor' } })
db.movieDetails.updateOne({ title: 'some_title', 'producres.name': 'Walt Disney' }), {$set: {'producers.$.country': 'USA'}}

