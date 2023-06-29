-- начальная миграция

START TRANSACTION ;

-- Котировки ------------------------------------------------------

DROP TABLE IF EXISTS quotes ;

CREATE TABLE quotes (
    iid           serial not null primary key,
    date          timestamp not null,
    company_name  text not null,
    price         float
) ;

comment on table quotes is 'Котировки' ;
comment on column quotes.date is 'Дата' ;
comment on column quotes.company_name
        is 'Название компании' ;
comment on column quotes.price
        is 'Цена за акцию' ;
-- -----------------------------------------------------------------------------------------------------------

COMMIT TRANSACTION ;