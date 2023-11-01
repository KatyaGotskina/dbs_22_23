
-- using invert index
select * from delivery where to_tsvector('russian', brand) @@ to_tsquery('russian', 'пицца');
-- using ingram index
select * from delivery where brand %> 'до';
select * from delivery where brand %> 'мод';
