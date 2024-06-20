# 根据design中的数据生成data_auto的原始数据

import pandas as pd


df1 = pd.read_excel('design.xlsx', sheet_name='heroes', header=0)
s1 = df1['HeroId']
df2 = pd.read_excel('design.xlsx', sheet_name='autobot', header=0)

# PVP转换等级
# df2['_level'] = df2['_level'].apply(lambda v: 240 + int(v / 10))

df = pd.DataFrame()

for i in s1:
    _df = df2.copy(deep=True)
    _df.insert(0, '_id', i)
    df = pd.concat([df, _df], axis=0)

df.to_excel('data_auto.xlsx', index=False)
