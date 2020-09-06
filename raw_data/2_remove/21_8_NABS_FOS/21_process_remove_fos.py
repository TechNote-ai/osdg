import json
import pandas as pd

df = pd.read_excel('NABS_FOS_update_2020-08-20_NOT-RELEVANT__ed_VS.xlsx')
not_relevant_fos = df['fos_number'].unique().tolist()
remove_fos = {
    f'SDG_{sdg_nr}': list(map(lambda fos_id: str(fos_id), not_relevant_fos))
    for sdg_nr in range(1, 18)
}

with open('21_RemoveFOS.json', 'w') as file_:
    json.dump(remove_fos, file_)
