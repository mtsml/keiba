CREATE TABLE horse (
    horse_id        VARCHAR     PRIMARY KEY,
    horse_name      VARCHAR,
    birthday        DATE,
    trainer_id      VARCHAR,
    owner_id        VARCHAR,
    breeder_id      VARCHAR,
    birthplace      VARCHAR,
    selling_price   INTEGER,
    mother_horse_id VARCHAR,
    father_horse_id VARCHAR
);