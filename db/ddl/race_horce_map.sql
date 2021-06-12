CREATE TABLE race_horse_map (
    race_id         INTEGER     REFERENCES race(race_id),
    horse_id        INTEGER,
    odds            NUMERIC,
    umaban          INTEGER,
    wakuban         INTEGER,
    chakujun        INTEGER,
    jockey_id       INTEGER,
    race_time       TIME,
    weight          SMALLINT,
    agari           NUMERIC,
    passing_order   VARCHAR,
    PRIMARY KEY (race_id, horse_id)
);
