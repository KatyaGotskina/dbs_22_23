db.couriers.drop()

db.createCollection('couriers', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            properties: {
                vehicle: {
                    bsonType: 'string'
                },
                working_days: {
                    bsonType: 'array',
                    items: {
                        bsonType: 'string'
                    }
                },
                name: {
                    bsonType: 'string'
                },
                age: {
                    bsonType: 'date'
                },
                orders: {
                    bsonType: 'array',
                    items: {
                        bsonType: 'object',
                        properties: {
                            urgency: { bsonType: 'bool' },
                            comment: { bsonType: 'string' },
                            size: { bsonType: 'string' },
                            package: { bsonType: 'string' },
                            time_of_creation: { bsonType: 'date' },
                            delivered: { bsonType: 'date' }
                        }
                    }
                }
            },
            additionalProperties: true,
            required: ['name', 'age']
        }
    }
})

db.couriers.insertMany([{
    vehicle: 'Мотоцикл',
    working_days: ['пн', 'ср', 'чт', 'вс'],
    name: 'Данил Олегович',
    age: new Date('01-03-1990'),
    orders: [
        {
            urgency: true, 
            comment: 'put the order in front of the door', 
            size: 'large', package: 'box', 
            time_of_creation: new Date('January 8, 2023 13:02:15 GMT+0200'), 
            delivered: new Date ('January 8, 2023 14:34:17 GMT+0200')
        },
        {
            urgency: true, 
            comment: 'Позвоните за 5 минут', 
            size: 'small', package: 'plastic bag', 
            time_of_creation: new Date('March 13, 2022 02:13:07 GMT+0200'), 
            delivered: new Date ('March 14, 2022 12:25:36 GMT+0200')
        },
        {
            urgency: true, 
            size: 'big', 
            package: 'polyethylene', 
            time_of_creation: new Date('February 23, 2023 14:07:23 GMT+0200'), 
            delivered: new Date('February 23, 2023 15:09:21 GMT+0200')
        }
    ]
},
{
    vehicle: 'Велосипед',
    working_days: ['вт', 'ср', 'пт', 'сб'],
    name: 'Антон Александрович',
    age: new Date('11-07-1996'),
    orders: [
        {
            urgency: true, 
            comment: 'Прошу доставить с максимальной сохранностью', 
            size: 'tiny', 
            package: 'polyethylene', 
            time_of_creation: new Date('May 25, 2023 20:23:01 GMT+0200'),
            delivered: new Date('May 26, 2023 10:01:38 GMT+0200')
        },
        { 
            urgency: true, 
            size: 'small', 
            package: 'box', 
            time_of_creation: new Date('December 14, 2023 11:02:15 GMT+0200'), 
            delivered: new Date('December 14, 2023 15:34:17 GMT+0200')
        }
    ]
}])