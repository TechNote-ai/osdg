import json
import pandas as pd


fname = '23_RemoveFOS.json'

remove_fos = dict()

df = pd.read_excel('sdg-fos_restructuring-v3_to-remove.xlsx')

for _, vals in df.iterrows():
    sdg, fos_id = vals['sdg'], str(vals['fos_id'])
    if sdg not in remove_fos.keys():
        remove_fos[sdg] = set()
    remove_fos[sdg].add(fos_id)

for sdg, foses in remove_fos.items():
    remove_fos[sdg] = list(foses)


with open(fname, 'w') as file_:
    json.dump(remove_fos, file_)






