import pandas as pd

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
	jockey_id::text,
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
df.columns