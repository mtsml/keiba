import pandas as pd
import pandas_profiling as pdq

import optuna.integration.lightgbm as lgb
from sklearn.model_selection import train_test_split

from db.db import Db


db = Db()
conn = db.get_connection()

sql = '''
select
	chakujun,
	weather,
	track_condition,
	(case when jockey_id = 1014 then 1 else 0 end) fukunaga_flg,
	(case when jockey_id = 5212 then 1 else 0 end) demuro_flg,
	(case when jockey_id = 5339 then 1 else 0 end) rumale_flg,
	(case when jockey_id = 711 then 1 else 0 end) goto_flg,
	(case when jockey_id = 1009 then 1 else 0 end) shibata_flg,	
	sex,
	age,
	odds,
	umaban,
	wakuban,
	jockey_weight,
	weight,
	birthplace	
from race_horse_map
inner join race using(race_id)
inner join horse using(horse_id)
where race_date > '2001-01-01'
'''

df = pd.read_sql(con=conn, sql=sql)
df_new = pd.get_dummies(df)

y = df['chakujun']
x = df.drop(['chakujun'], axis=1)


X_train, X_test, y_train, y_test = train_test_split(x, y)
X_train, x_val, y_train, y_val = train_test_split(X_train, y_train)