import pandas as pd
import json


replace_fos = dict()

df = pd.read_csv('replace-review_2020-10-02.csv')
for fos_id, _, from_sdg, to_sdg in df.values:
    fos_id = str(fos_id)
    if fos_id not in replace_fos.keys():
        replace_fos[fos_id] = []
    replace_fos[fos_id].append([from_sdg, to_sdg])

with open('12_ReplaceFOS.json', 'w') as file_:
    json.dump(replace_fos, file_)
