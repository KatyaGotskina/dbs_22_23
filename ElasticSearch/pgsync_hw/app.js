import express from 'express'
import bodyParser from 'body-parser'
import { Client } from '@elastic/elasticsearch'

const client = new Client({
    node: 'http://localhost:41554'
})

const app = express()
app.use(bodyParser.json())
const appPort = 3000

app.get('/', (_, res) => {
    res.send('Hello')
})

// по нечеткому соответствию
app.get('/courier', async (req, res) => {
    try {
        const vehicle = req.query['vehicle']
        var result = ''

        if (vehicle == null) { 
            result = await client.search({index: 'courier'})
        }
        else {
            result = await client.search({
                index: 'courier',
                query: {
                    match: {
                        vehicle: {
                            query: vehicle
                        }
                    }
                }
            })
        }

        res.json(result.hits.hits)
    } catch (err) {
        console.log(err)
        res.sendStatus(400)
    }
})

// по синонимам и словоформам
app.get('/orders', async (req, res) => {
    try {
        const size = req.query['size']
        var result = ''
        if (size == null) { 
            result = await client.search({index: 'orders'})
        }
        else {
            result = await client.search({
                index: 'orders',
                query: {
                    match: {
                        size: {
                            query: size
                        }
                    }
                }
            })
        }

        res.json(result.hits.hits)
    } catch (err) {
        console.log(err)
        res.sendStatus(400)
    }
})

// по части слова (через ngram)
app.get('/delivery', async (req, res) => {
    try {
        const brand = req.query['brand']
        var result = ''
        if (brand == null) { 
            result = await client.search({index: 'delivery'})
        }
        else {
            result = await client.search({
                index: 'delivery',
                query: {
                    match: {
                        brand: {
                            query: brand
                        }
                    }
                }
            })
        }

        res.json(result.hits.hits)
    } catch (err) {
        console.log(err)
        res.sendStatus(400)
    }
})

app.listen(appPort, () => {
    console.log(`app listening on port ${appPort}`)
})
