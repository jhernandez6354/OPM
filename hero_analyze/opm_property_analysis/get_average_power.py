# 根据output_auto的属性数据生成队伍的平均战力

import pandas as pd

df = pd.read_excel('output_auto.xlsx',header=0)
df_hero = df.loc[:, df.columns.intersection(['_level', 'team_power'])]
df1 = df['team_power'].groupby(df['_level']).mean()
df1.to_excel('average_team_power.xlsx')
