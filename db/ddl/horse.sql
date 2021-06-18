/*
  馬の情報
*/
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

COMMENT ON COLUMN horse.horse_id        IS 'ID';
COMMENT ON COLUMN horse.horse_name      IS '名称';
COMMENT ON COLUMN horse.birthday        IS '生年月日';
COMMENT ON COLUMN horse.trainer_id      IS '調教師のID';
COMMENT ON COLUMN horse.owner_id        IS '馬主のID';
COMMENT ON COLUMN horse.breeder_id      IS '生産者のID';
COMMENT ON COLUMN horse.birthplace      IS '産地';
COMMENT ON COLUMN horse.selling_price   IS 'セリ取引価格';
COMMENT ON COLUMN horse.mother_horse_id IS '母馬のID';
COMMENT ON COLUMN horse.father_horse_id IS '父馬のID';
