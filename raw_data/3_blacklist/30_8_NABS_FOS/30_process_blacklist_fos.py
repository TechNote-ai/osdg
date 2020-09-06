import pandas as pd

df = pd.read_excel('NABS_FOS_update_2020-08-20_NOT-RELEVANT__ed_VS.xlsx')[['fos_number', 'fos_name']]
df.columns = ['fos_id', 'fos_name']

df.to_csv('30_BlacklistFOS.csv', index=False)
