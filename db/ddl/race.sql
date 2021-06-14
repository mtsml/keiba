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
