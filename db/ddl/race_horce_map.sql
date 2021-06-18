/*
  レースに出走した馬の情報
*/
CREATE TABLE race_horse_map (
    race_id         VARCHAR,
    horse_id        VARCHAR,
    sex             VARCHAR,
    age             INTEGER,
    odds            NUMERIC,
    umaban          INTEGER,
    wakuban         INTEGER,
    chakujun        INTEGER,
    jockey_id       VARCHAR,
    jockey_weight   NUMERIC,
    race_time       TIME,
    weight          SMALLINT,
    agari           NUMERIC,
    passing_order   VARCHAR,
    prize           INTEGER,
    PRIMARY KEY (race_id, horse_id)
);

COMMENT ON COLUMN race_horse_map.race_id       IS 'レースのID';
COMMENT ON COLUMN race_horse_map.horse_id      IS '馬のID';
COMMENT ON COLUMN race_horse_map.sex           IS '性別';
COMMENT ON COLUMN race_horse_map.age           IS '年齢';
COMMENT ON COLUMN race_horse_map.odds          IS 'オッズ';
COMMENT ON COLUMN race_horse_map.umaban        IS '馬番';
COMMENT ON COLUMN race_horse_map.wakuban       IS '枠番';
COMMENT ON COLUMN race_horse_map.chakujun      IS '着順';
COMMENT ON COLUMN race_horse_map.jockey_id     IS 'ジョッキーのID';
COMMENT ON COLUMN race_horse_map.jockey_weight IS '斤量';
COMMENT ON COLUMN race_horse_map.race_time     IS 'タイム';
COMMENT ON COLUMN race_horse_map.weight        IS '馬体重';
COMMENT ON COLUMN race_horse_map.agari         IS '上り';
COMMENT ON COLUMN race_horse_map.passing_order IS '通過';
COMMENT ON COLUMN race_horse_map.prize         IS '賞金';
