import json
import pandas as pd
import re

df = pd.read_excel('osdg_fos_paper_citation_counts_REMOVE_v2_ed_VS.xlsx')

remove_fos = dict()
for sdg_to_remove, fos_id in df[['remove', 'fos_id']].values:
    sdg_to_remove = map(lambda sdg_nr: f'SDG_{sdg_nr}', re.findall(r'\d+', sdg_to_remove))
    for sdg_label in sdg_to_remove:
        if sdg_label not in remove_fos.keys():
            remove_fos[sdg_label] = []
        remove_fos[sdg_label].append(str(fos_id))

with open('22_RemoveFOS.json', 'w') as file_:
    json.dump(remove_fos, file_)
