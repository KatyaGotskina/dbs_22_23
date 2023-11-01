drop table if exists courier, delivery, orders, delivery_to_courier, courier_to_orders;

CREATE TABLE courier
(
	id int primary key generated always as identity, 
	vehicle text,
	working_days text,
	name text not null,
	age date not null
);

CREATE TABLE delivery 
(
	id int primary key generated always as identity,
	address text, 
	opening_time time, 
	closing_time time,
	brand text not null 
);

CREATE TABLE orders
(
	id int primary key generated always as identity,
	urgency bool, 
	comment text,
	size text,
	package text,
	time_of_creation timestamp, 
	delivered timestamp,
	courier_id int references courier,
	delivery_id int references delivery
);

INSERT INTO delivery(address, opening_time, closing_time, brand)
values ('Ленина, 22', '10:00', '08:00', 'PizzaHouse'),
	   ('Демократическая, 13', '9:00', '23:00', 'Жар-пицца'),
	   ('Воскресенская, 21', '12:00', '21:00', 'Новая Мода'), 
	   ('Новая, 1', '8:00', '24:00', 'Додо-пицца'),
       ('Воскресенская, 211', '12:00', '21:00', 'Старая Мода'), 
       ('Воскресенская, 32', '12:00', '21:00', 'Модный дом'), 
	   ('Общинная, 54', '9:00', '21:00', 'Ozon');
	   
insert into courier(vehicle, working_days, name, age)
values ('Мотоцикл', 'пн, вт, чт, сб', 'Данил Олегович', '01-03-1990'),
       ('Велосипед', 'ср, чт, пн, вс', 'Антон Александрович', '11-07-1996'),
       ('Машина', 'пн, ср, чт, сб, вс', 'Александр Антонович', '06-21-2001'),
       ('Ходит пешком', 'ср, пн, вс', 'Артем Николаевич', '08-17-1995'),
       ('Машина', 'пн, вт, ср, пн, сб, вс', 'Николай Артемович', '07-12-2002'),
       ('Самокат', 'вт, пн, вс', 'Владимир Олегович', '10-01-1995');
       
insert into orders(urgency, comment, size, package, time_of_creation, delivered, courier_id, delivery_id)
values (true, 'put the order in front of the door', 'large', 'box','January 8 13:02:15 2023 EET', 'January 8 14:34:17 2023 EET', 2, 1),
       (true, 'Позвоните за 5 минут', 'small', 'plastic bag', 'March 13 02:13:07 2022 EAT', 'March 14 12:25:36 2022 EAT', 3, 1),
       (true, null, 'big', 'polyethylene', 'February 23 14:07:23 2023 EAT', 'February 23 15:09:21 2023 EAT', 4, 2),
       (true, 'Прошу доставить с максимальной сохранностью', 'tiny', 'polyethylene','May 25 20:23:01 2023 EAT', 'May 26 10:01:38 2023 EAT', 1, 5),
       (true, null, 'small', 'box', 'December 14 11:02:15 2023 EET', 'December 14 15:34:17 2023 EET', 3, 5);
       
create  table delivery_to_courier
(
	delivery_id int references delivery,
	courier_id int references courier
);

insert  into delivery_to_courier(delivery_id, courier_id)
values (1, 1), (1, 2), (2, 2), (2, 3), (3, 4), (1, 4), (5, 4), (5, 1), (4, 3), (3, 6);


select brand, address, opening_time, closing_time, name, age, working_days, 
vehicle, urgency, time_of_creation, delivered, size, package, comment
from delivery d
	join delivery_to_courier dc on d.id = dc.delivery_id
	join courier c on c.id = dc.courier_id
	JOIN orders o ON o.courier_id = c.id;

select change_work_days();