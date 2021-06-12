CREATE TABLE race (
    race_id         BIGINT     PRIMARY KEY,
    weather         VARCHAR,
    distance        INTEGER,
    racecourse      VARCHAR,
    race_condition  VARCHAR,
    track_type      VARCHAR,
    track_condition VARCHAR,
    mawari          VARCHAR
);
