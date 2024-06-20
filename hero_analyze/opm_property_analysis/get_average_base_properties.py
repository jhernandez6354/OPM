import pandas as pd


df = pd.read_excel('output_auto.xlsx',header=0)
df.drop(df.columns.difference(['_level', 'hp_base', 'atk_base', 'def_base', 'hp', 'atk', 'def', 'power']), axis=1,inplace=True)
df_base = df.groupby('_level').mean().reset_index()
df_base.to_excel('output_base.xlsx')