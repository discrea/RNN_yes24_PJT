import pandas as pd
# pd.set_option('display.unicode.east_asian_width',True)
# row 생략 없이 출력
pd.set_option('display.max_rows', None)
# col 생략 없이 출력
pd.set_option('display.max_columns', None)

df = pd.read_csv('/Users/san/work/python/Deep_Learning/LSTM_DNN_PJT/data_backup/address_info',index_col=0)
print(df)
print(df.info())
cat_df_m = df[['medium_category','page_amount']].groupby(['medium_category']).sum()
print(cat_df_m)