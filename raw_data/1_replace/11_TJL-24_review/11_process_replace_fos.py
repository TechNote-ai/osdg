import json
import pandas as pd
import re


df = pd.read_excel('osdg_fos_paper_citation_counts_REPLACE_v2_ed_VS.xlsx')

replace_fos = dict()
for fos_id, replace_from, to_sdg in df[['fos_id', 'sdgs', 'replace_to']].values:
    replace_from = map(lambda sdg_nr: f'SDG_{sdg_nr}', re.findall(r'\d+', replace_from))
    to_sdg_nr = re.findall(r'\d+', to_sdg)[0]
    to_sdg = f"SDG_{to_sdg_nr}"
    if fos_id not in replace_fos.keys():
        replace_fos[fos_id] = []
    for from_sdg in replace_from:
        replace_fos[fos_id].append([from_sdg, to_sdg])

with open('11_ReplaceFOS.json', 'w') as file_:
    json.dump(replace_fos, file_)
