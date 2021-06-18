import pandas as pd

import optuna.integration.lightgbm as lgb
from sklearn.model_selection import train_test_split
import lightgbm

from db.db import Db


db = Db()
conn = db.get_connection()

sql = '''
WITH
    past_race AS (
        SELECT 
            rhm1.race_id,
			rhm1.horse_id,
			rhm2.chakujun,
			rhm2.odds,
			rhm2.weight,
            RANK() OVER(
                PARTITION BY rhm1.race_id, rhm1.horse_id 
                ORDER BY r2.race_date desc
            ) AS past_race_rank
        FROM 
            race_horse_map rhm1 
            INNER JOIN race r1
                ON r1.race_id = rhm1.race_id
            INNER JOIN race_horse_map rhm2
                ON rhm1.horse_id = rhm2.horse_id
            INNER JOIN race r2
                ON rhm2.race_id = r2.race_id
                AND r2.race_date < r1.race_date
        WHERE
            r1.race_name ~ 'エプソム'
    ),
    past_3_race AS (
        --  直近3レースの必要な情報を横持ちに変換
        SELECT
			race_id,
            horse_id,
            MAX(CASE
                    WHEN past_race_rank = 1 THEN weight
                    ELSE NULL
                END
            ) weight_p1,
            MAX(CASE
                    WHEN past_race_rank = 2 THEN weight
                    ELSE NULL
                END
            ) weight_p2,
            MAX(CASE
                    WHEN past_race_rank = 3 THEN weight
                    ELSE NULL
                END
            ) weight_p3,
            MAX(CASE
                    WHEN past_race_rank = 1 THEN odds
                    ELSE NULL
                END
            ) odds_p1,
            MAX(CASE
                    WHEN past_race_rank = 2 THEN odds
                    ELSE NULL
                END
            ) odds_p2,
            MAX(CASE
                    WHEN past_race_rank = 3 THEN odds
                    ELSE NULL
                END
            ) odds_p3,
            MAX(CASE
                    WHEN past_race_rank = 1 THEN chakujun
                    ELSE NULL
                END
            ) chakujun_p1,
            MAX(CASE
                    WHEN past_race_rank = 2 THEN chakujun
                    ELSE NULL
                END
            ) chakujun_p2,
            MAX(CASE
                    WHEN past_race_rank = 3 THEN chakujun
                    ELSE NULL
                END
            ) chakujun_p3
        FROM
            past_race
        WHERE
            past_race_rank < 4
        GROUP BY
			race_id,
            horse_id
		HAVING
			COUNT(*) = 3
    )

SELECT
	CASE WHEN chakujun <= 3 THEN 1 ELSE 0 END fukushou,
	chakujun,
-- 	horse_name,
	p3r.*
FROM
    past_3_race p3r
    INNER JOIN horse USING(horse_id)
    INNER JOIN race_horse_map rhm
		ON rhm.race_id = p3r.race_id
		AND rhm.horse_id = p3r.horse_id
ORDER BY
    chakujun
'''

_df = pd.read_sql(con=conn, sql=sql)
df = pd.get_dummies(_df)
