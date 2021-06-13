CREATE TABLE horse (
    horse_id        BIGINT     PRIMARY KEY,
    birthday        DATE,
    trainer_id      VARCHAR,
    owner_id        VARCHAR,
    breeder_id      VARCHAR,
    birthplace      VARCHAR,
    selling_price   INTEGER
);