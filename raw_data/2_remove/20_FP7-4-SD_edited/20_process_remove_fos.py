import json
import pandas as pd

df = pd.read_csv('bad_fos.csv')
df = df.drop_duplicates(['sdg', 'fos_id'])

remove_fos = dict()
for sdg_label, fos_id, _ in df.values:
    if sdg_label not in remove_fos.keys():
        remove_fos[sdg_label] = []
    remove_fos[sdg_label].append(str(fos_id))

with open('20_RemoveFOS.json', 'w') as file_:
    json.dump(remove_fos, file_)
