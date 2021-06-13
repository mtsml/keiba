CREATE TABLE race_horse_map_backup (
    backup_id       INTEGER,
    race_id         BIGINT,
    horse_id        BIGINT,
    sex             VARCHAR,
    age             INTEGER,
    odds            NUMERIC,
    umaban          INTEGER,
    wakuban         INTEGER,
    chakujun        INTEGER,
    jockey_id       INTEGER,
    jockey_weight   INTEGER,
    race_time       TIME,
    weight          SMALLINT,
    agari           NUMERIC,
    passing_order   VARCHAR,
    prize           INTEGER,
    PRIMARY KEY (race_id, horse_id)
);
