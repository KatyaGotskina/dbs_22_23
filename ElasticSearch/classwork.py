#--1. Найти все фильмы с рейтингом PG
{
    "query": {
        "term": {"rated": "PG"}
    }
}

#-- 2. Найти все фильмы с режиссерами Steve Carr, Joel Coen, Ethan Coen, Julius Avery
{
    "query": {
        "terms": {
            "director": ["Steve Carr", "Joel Coen", "Ethan Coen", "Julius Avery"]
        }
    }
}

#-- 3. Найти все фильмы без режиссера Hjalmar Söderberg
{
    "query": {
        "bool": {
            "must_not": [
                {
                    "term": {"director": "Hjalmar Söderberg"}
                }
            ]
        }
    }
}

#-- 4. Найти все фильмы без актеров Chae Gil Byung, Louis C.K., Shivarajkumar
{
    "query": {
        "bool": {
            "must_not": {
                "terms": {
                    "actors": [
                        "Chae Gil Byung",
                        "Louis C.K.",
                        "Shivarajkumar"
                    ]
                }
            }
        }
    }
}

#-- 5. Найти все фильмы с условием metacritic > 9 and metacritic < 73
{
    "query": {
        "range": {
            "metacritic": {
                "gt": 9, 
                "lt": 73
            }
        }
    }
}

#-- 6. Найти все фильмы с условием awards.nominations >= 33 and awards.nominations <= 149
{
    "query": {
        "range": {
            "awards.nominations": {
                "gte": 33, 
                "lte": 149
            }
        }
    }
}

#-- 7. Найти все фильмы с условием 
#-- (tomato.image = fresh or (runtime > 92 and runtime < 401)) and (genres = Romance or (tomato.userRating > 2.2 and tomato.userRating < 4))

{
"query": {
    "bool": {
        "must": [
            {
                "bool": {
                    "should": [ {"term": { "tomato.image": "fresh" } }, 
                        {"range": { "runtime": { "gt": 92, "lt": 401} } }
                    ]
                }
            }, 
            {
                "bool": {
                    "should": [ { "term": { "genres": "Romance" } }, 
                        {"range": { "tomato.userRating": { "gt": 2.2,  "lt": 4 } } }
                    ]
                }
            }
        ]
    }
}
}

# -- 8. Для фильмов со страной Spain вывести топ 10 режиссеров с наибольшим количеством наград
{
    "query": {
        "bool": {
            "must": [
                {
                    "exists": {
                        "field": "awards"
                    }
                },
                {
                    "term": {
                        "countries": "Spain"
                    }
                }
            ]
        }
    },
    "aggs": {
        "by_director": {
            "terms": {
                "field": "director",
                "order": {
                    "total_awards": "desc"
                },
                "size": 10
            },
            "aggs": {
                "total_awards": {
                    "sum": {
                        "script": "return doc['awards.wins'].value + doc['awards.nominations'].value"
                    }
                }
            }
        }
    }
}

#-- 9. Для фильмов с tomato изображением fresh вывести топ 4 актеров с наибольшим средним tomato рейтингом
{
    "query": {
        "bool": {
            "must": [
                {
                    "exists": {
                        "field": "tomato"
                    }
                },
                {
                    "term": {
                        "tomato.image": "fresh"
                    }
                }
            ]
        }
    },
    "aggs": {
        "by_actor": {
            "terms": {
                "field": "actors",
                "order": {
                    "avg_rating": "desc"
                },
                "size": 4
            },
            "aggs": {
                "avg_rating": {
                    "avg": {
                        "field": "tomato.rating"
                    }
                }
            }
        }
    }
}

#-- 
{
    "query": {
        "term": {
            "genre": "Romance"
        }
    },
    "aggs": {
        "by_director":{
            "terms": {
                "field": "director",
                "order": {
                    "total_movies": "desc"
                },
                "size": 5
            },
            "aggs": {
                "total_movies": {
                    "sum": {
                        "script": "return 1"
                    }
                }
            }
        }
    },
    "size": 0
}