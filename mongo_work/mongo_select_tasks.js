//1. Найти все фильмы с актером Percy Kilbride
db.movieDetails.find({ actors: { $in: ['Percy Kilbride'] } })

//2. Найти все фильмы с tomato изображениями fresh, rotten
db.movieDetails.find(
    { $or: [{ 'tomato.image': 'fresh'}, { 'tomato.image': 'rotten'}] }
)

// 3. Найти все фильмы без режиссера Andrés Indriðason
db.movieDetails.find({
    director: { $ne: 'Andrés Indriðason' }
})

// 4. Найти все фильмы без стран Germany, Sweden, Hong Kong
db.movieDetails.find({
    countries: { $nin: ['Germany', 'Sweden', 'Hong Kong'] }
})

// 5. Найти все фильмы с условием year > 1906 and year < 2000
db.movieDetails.find({
    year: { $gt: 1906, $lt: 2000}
})

//6. Найти все фильмы с условием imdb.rating >= 1.7 and imdb.rating <= 7.8
db.movieDetails.find({
    $and: [
        {'imdb.rating': { $gte: 1.7}}, {'imdb.rating': { $lte: 7.8}}
    ]
})

// 7. Найти все фильмы с условием 
// (countries = Japan or (awards.wins > 62 and awards.wins < 146)) and (tomato.image = fresh or (tomato.fresh > 63 and tomato.fresh < 230))
db.movieDetails.find({
    $and: [
        { $or: [
            { countries: { $in: ['Japan']} }, {'awards.wins': { $gt: 62, $lt: 146}}
        ]},
        {
            $or: [
                {'tomato.image': 'fresh'}, {'tomato.fresh': { $gt: 63, $lt: 230}}
            ]
        }
    ]
})

// 8. Для фильмов со страной Japan вывести топ 9 режиссеров с наибольшим количеством номинаций

db.movieDetails.aggregate([
    { $match: { countries: { $in: ['Japan'] } } },
    { $group: {  }},
    { $limit: 9 }
])

// 9. Для фильмов с рейтингом PG вывести топ 9 сценаристов с наибольшим средним tomato рейтингом
db.movieDetails.aggregate([
    { $match: { countries: { $in: ['Japan'] } } },
])

