import os
import pandas as pd

df_blacklist = pd.DataFrame(columns=['fos_id', 'fos_name', 'source'])

for directory in filter(lambda dir: '.' not in dir, os.listdir()):
    try:
        blacklist_fos_fname = list(filter(lambda oname: '_BlacklistFOS.csv' in oname, os.listdir(directory)))[0]
        df = pd.read_csv(f'{directory}/{blacklist_fos_fname}')
        assert list(df.columns) == ['fos_id', 'fos_name'], "*_BlacklistFOS.csv column names must be ['fos_id', 'fos_name']"
    except IndexError:
        print('Sdg Terms are not processed in {directory}')
        continue
    except AssertionError as e:
        print(f'In directory {directory}\n{e}')
        continue
    
    df['source'] = directory
    
    df_blacklist = pd.concat([df_blacklist, df], axis=0)

df_blacklist.sort_values(['fos_id', 'source'], inplace=True)

df_blacklist.to_csv('Blacklist.csv', index=False)
