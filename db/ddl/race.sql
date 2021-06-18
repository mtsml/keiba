/*
  レースの情報
*/
CREATE TABLE race (
    race_id         VARCHAR     PRIMARY KEY,
    race_name       VARCHAR,
    race_date       DATE,
    weather         VARCHAR,
    distance        INTEGER,
    racecourse      VARCHAR,
    race_condition  VARCHAR,
    track_type      VARCHAR,
    track_condition VARCHAR,
    mawari          VARCHAR
);

COMMENT ON COLUMN race.race_id         IS 'ID';
COMMENT ON COLUMN race.race_name       IS '名称';
COMMENT ON COLUMN race.race_date       IS '開催年月日';
COMMENT ON COLUMN race.weather         IS '天候';
COMMENT ON COLUMN race.distance        IS '距離';
COMMENT ON COLUMN race.racecourse      IS '開催地';
COMMENT ON COLUMN race.race_condition  IS '出走条件';
COMMENT ON COLUMN race.track_type      IS 'トラックの種類（芝 / ダ）';
COMMENT ON COLUMN race.track_condition IS '馬場状態';
COMMENT ON COLUMN race.mawari          IS '回り方向（右 / 左）';
