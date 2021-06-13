CREATE TABLE race_horse_map (
    race_id         BIGINT     REFERENCES race(race_id),
    horse_id        BIGINT,
    sex             VARCHAR,
    age             INTEGER,
    odds            NUMERIC,
    umaban          INTEGER,
    wakuban         INTEGER,
    chakujun        INTEGER,
    jockey_id       INTEGER,
    jockey_weight   NUMERIC,
    race_time       TIME,
    weight          SMALLINT,
    agari           NUMERIC,
    passing_order   VARCHAR,
    prize           INTEGER,
    PRIMARY KEY (race_id, horse_id)
);
