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

app.get('/couriers', async (_, res) => {
    try {
        const couriers = await db
            .collection('couriers')
            .find({}, { limit: 10 })
            .toArray()

        res.json(couriers)
    } catch (err) {
        console.log(err)
        res.sendStatus(400)
    }
})

app.post('/courier/create', async (req, res) => {
    try {
        let { vehicle, working_days, name, age, orders } = req.body
        age = new Date(age)
        orders.forEach(order => {
            order.time_of_creation = new Date(order.time_of_creation)
            order.delivered = new Date(order.delivered)
            }
        )
        console.log({ vehicle, working_days, name, age, orders })
        const { insertedId } = await db
            .collection('couriers')
            .insertOne({ vehicle, working_days, name, age, orders })

        res.json({ id: insertedId })
    } catch (err) {
        console.log(err)
        res.sendStatus(400)
    }
})

app.post('/courier/update', async (req, res) => {
    try {
        let { vehicle, working_days, name, age, orders } = req.body
        age = new Date(age)
        orders.forEach(order => {
            order.time_of_creation = new Date(order.time_of_creation)
            order.delivered = new Date(order.delivered)
            }
        )
        const result = await db
            .collection('couriers')
            .updateOne(
                { _id: new ObjectId(id) },
                { $set: { vehicle, working_days, name, age, orders } }
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

app.delete('/courier/delete', async (req, res) => {
    try {
        const { id } = req.body
        const { deletedCount } = await db.collection('couriers').deleteOne({ _id: new ObjectId(id) })

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
// db.movieDetails.updateOne({ title: 'some_title' }, { $set: {runtime: 104, 'imdb.rating': 8.3 } })
// db.movieDetails.updateOne({ title: 'some_title' }, { $set: {'actors.0': 'some_new_actor' } })
// db.movieDetails.updateOne({ title: 'some_title', actors: 'some_new_actor' }, { $set: {'actors.$': 'new_actor' } })
// db.movieDetails.updateOne({ title: 'some_title', 'producres.name': 'Walt Disney' }), {$set: {'producers.$.country': 'USA'}}

