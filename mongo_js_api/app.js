import express from 'express'
import bodyParser from 'body-parser'
import { MongoClient, ObjectId } from 'mongodb'
import { createClient } from 'redis'
import { config } from 'dotenv'
import winston from 'winston'
import LokiTransport from 'winston-loki'
import { collectDefaultMetrics, Counter, register } from 'prom-client'
import promBundle from 'express-prom-bundle'



config()

const { MONGO_USER, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT, MONGO_DB, EXPRESS_PORT, REDIS_HOST, REDIS_PORT, LOKI_HOST, LOKI_PORT } = process.env

const client = new MongoClient(`mongodb://${MONGO_USER}:${MONGO_PASSWORD}@${MONGO_HOST}:${MONGO_PORT}`)
const db = client.db(MONGO_DB)

const logger = winston.createLogger({
    level: 'debug',
    format: winston.format.json(),
    transports: [
        new winston.transports.Console(),
        new LokiTransport({ host: `http://${LOKI_HOST}:${LOKI_PORT}`, json: true, labels: { job: 'node-express' } })
    ]
})

collectDefaultMetrics({ register })
const metricsMiddleware = promBundle({
    includeMethod: true,
    includePath: true,
    metricType: 'summary',
    percentiles: []
})

const courierReqCounter = new Counter({
    name: 'courier_requests_counter',
    help: 'Requests of all couriers data',
    labelNames: ['table']
})

const vehicleReqCounter = new Counter({
    name: 'search_by_vehicle_requests_counter',
    help: 'Requests of couriers by vehicle',
    labelNames: ['by_vehicle']
})

const redisClient = await createClient({ url: `redis://${REDIS_HOST}:${REDIS_PORT}` })
    .on('error', err => logger.error('Redis Client Error', err))
    .connect()

const app = express()
app.use(bodyParser.json())
app.use(metricsMiddleware)
const appPort = EXPRESS_PORT

app.get('/', (_, res) => {
    res.send('')
})

app.get('/couriers', async (req, res) => {
    try {
        const vehicle = req.query['vehicle']

        if ( vehicle == null) { 
            logger.debug(`Couriers all data requested`)
            const all_couriers = await db
                .collection('couriers')
                .find({}, { limit: 10 })
                .toArray()

            courierReqCounter.labels({ table: 'couriers' }).inc()
            return res.json(all_couriers)
        }
        else {
            logger.debug(`Couriers with vehicle ${vehicle} requested`)
            vehicleReqCounter.labels({ by_vehicle: vehicle }).inc()
            const cachedMovies = JSON.parse(await redisClient.get('courier:' + vehicle))
            if (cachedMovies) {
                logger.debug(`Got couriers with vehicle ${vehicle} from cache`)
                return res.json(cachedMovies)
            }
            logger.debug(`No couriers with vehicle ${vehicle} in cache`)
            const couriers = await db
                .collection('couriers')
                .find({ vehicle: vehicle }, { limit: 10 })
                .toArray()
            redisClient.set('courier:' + vehicle, JSON.stringify(couriers), { EX: 10 })
            return res.json(couriers)
            }

    } catch (err) {
        logger.error(err)
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
        logger.error(err)
        res.sendStatus(400)
    }
})

app.post('/courier/update', async (req, res) => {
    try {
        let { id, vehicle, working_days, name, age, orders } = req.body
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
        logger.error(err)
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
        logger.error(err)
        res.sendStatus(400)
    }
})

app.get('/metrics', async (_, res) => {
    try {
        res.set('Content-Type', register.contentType)
        res.end(await register.metrics())
    } catch (ex) {
        logger.error(err)
        res.sendStatus(500)
    }
})


app.listen(appPort, () => {
    logger.info(`express listening on port ${EXPRESS_PORT}`)
})


//примеры апдейтов в mongo
// db.movieDetails.updateOne({ title: 'some_title' }, { $set: {runtime: 104, 'imdb.rating': 8.3 } })
// db.movieDetails.updateOne({ title: 'some_title' }, { $set: {'actors.0': 'some_new_actor' } })
// db.movieDetails.updateOne({ title: 'some_title', actors: 'some_new_actor' }, { $set: {'actors.$': 'new_actor' } })
// db.movieDetails.updateOne({ title: 'some_title', 'producres.name': 'Walt Disney' }), {$set: {'producers.$.country': 'USA'}}

