import pandas as pd

import optuna.integration.lightgbm as lgb
from sklearn.model_selection import train_test_split
import lightgbm

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
	--jockey_id::text,	
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

print(df_new.columns)
pass

y = df_new['chakujun']
# x = df_new.drop(['chakujun', 'weather', 'track_condition', 'sex', 'birthplace'], axis=1)
x = df_new.drop(['chakujun'], axis=1)

X_train, X_test, y_train, y_test = train_test_split(x, y)
# X_train, x_val, y_train, y_val = train_test_split(X_train, y_train)

# train_set, test_set = train_test_split(keiba_data, test_size=0.2, random_state=0)

# #訓練データを説明変数データ(X_train)と目的変数データ(y_train)に分割
# X_train = train_set.drop('rank', axis=1)
# y_train = train_set['rank']

# #モデル評価用データを説明変数データ(X_test)と目的変数データ(y_test)に分割
# X_test = test_set.drop('rank', axis=1)
# y_test = test_set['rank']

# 学習に使用するデータを設定
lgb_train = lightgbm.Dataset(X_train, y_train)
lgb_eval = lightgbm.Dataset(X_test, y_test, reference=lgb_train)

params = {
        'task': 'train',
        'boosting_type': 'gbdt',
        # 'objective': 'binary',
		'objective': 'multiclass',
        'num_class': 19,
        # 'metric': {'auc'},
		# 'min_data' : 1
}

model = lightgbm.train(params,
        train_set=lgb_train, # トレーニングデータの指定
        valid_sets=lgb_eval, # 検証データの指定
        # verbose_eval=10
)

model.save_model('model_multiclass3.txt')
