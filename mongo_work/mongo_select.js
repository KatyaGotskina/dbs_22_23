db.movieDetails.distinct('rated')

// where rated = 'PG' and director = 'George Lucas'
db.movieDetails.find({ rated: 'PG', director: 'George Lucas' })

// where year > 2019 and year < 2015
db.movieDetails.find({year: { $gt: 2010, $lt: 2015 }})

// where year between 2010 and 2015 (where year >= 2010 and year >= 2015)
db.movieDetails.find({year: { $gte: 2010, $lte: 2015 }})

// where metacritic >= 90 or imdb.rating >= 9
db.movieDetails.find({ $or: [{ metacritic: { $gte: 90 } }, { 'imdb.rating': { $gte: 9 } }] })

// where (metacritic >= 90 or imdb.rating >= 9) and (countries = 'Soviet Union' or countries = 'Russia')
db.movieDetails.find({ 
    $end: [
        { $or: [{ metacritic: { $gte: 90 } }, { 'imdb.rating': { $gte: 9 } }] },
        { $or: [{ countries: 'Soviet Union'}, {countries: 'Russia'} ]}
] })

// where countries in ('Soviet Union', 'Romania')
db.movieDetails.find({ countries: { $in: ['Soviet Union', 'Romania'] } }) // or $nin: ['Soviet Union', 'Romania']

// where rated <> 'R'
db.movieDetails.find({ rated: { $ne: 'R' } })

// where countries = 'Soviet Union' order by imdb.rating
db.movieDetails.aggregate([
    { $match: { countries: 'Soviet Union' } },
    {
        $sort: {
            'imdb.rating': -1
        }
    }
])

db.movieDetails.distinct('rated')

db.movieDetails.aggregate([
    {
        $match: {
            rated: { $nin: [null, 'APPROVED', 'Approved', 'NOT RATED', 'Not Rated', 'PASSED', 'UNRATED', 'Unrated'] }
        }
    },
    {
        $group: {
            _id: '$rated',
            totalWins: { $sum: '$awards.wins' },
            totalNominations: { $sum: '$awards.nominations' },
            totalFilms: { $sum: 1 },
            avgImdbRating: { $avg: '$imdb.rating' },
            minImdbRating: { $min: '$imdb.rating' },
            maxImdbRating: { $max: '$imdb.rating' }
        }
    },
    { $sort: { totalFilms: -1 } },
    { $limit: 3 }
])

db.movieDetails.aggregate([
    { $unwind: '$countries' },
    { $group: { _id: '$countries', avgMetacritic: { $avg: '$metacritic' }, totalFilms: { $sum: 1 } } },
    {
        $sort: {
            avgMetacritic: -1
        }
    },
    { $limit: 3 }
])

