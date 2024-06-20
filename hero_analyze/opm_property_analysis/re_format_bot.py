# Generate the original data of data based on the design data
import pandas as pd

df1 = pd.read_excel('design.xlsx', sheet_name='heroes', header=0)
s1 = df1['HeroId']
df2 = pd.read_excel('design.xlsx', sheet_name='conditions', header=1)
df = pd.DataFrame()

for i in s1:
    _df = df2.copy(deep=True)
    _df.insert(0, '_id', i)
    _df.insert(0, 'bot_id', 100000 + _df['test_id'] * 1000 + i)
    df = pd.concat([df, _df], axis=0)

df.drop(['test_id'], axis=1, inplace=True)
df.to_excel('data.xlsx', index=False)
