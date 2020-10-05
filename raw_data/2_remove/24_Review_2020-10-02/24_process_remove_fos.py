import pandas as pd
import json


remove_fos = dict()

df = pd.read_csv('remove-review_2020-10-02.csv')
for fos_id, _, rm_sdg in df.values:
    fos_id = str(fos_id)
    if rm_sdg not in remove_fos.keys():
        remove_fos[rm_sdg] = []
    remove_fos[rm_sdg].append(fos_id)

with open('24_RemoveFOS.json', 'w') as file_:
    json.dump(remove_fos, file_)

