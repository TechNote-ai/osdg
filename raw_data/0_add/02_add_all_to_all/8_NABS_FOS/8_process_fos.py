from tqdm import tqdm

import json
import pandas as pd


FNAME_PROCESSED_KEY_TERMS = "8_ProcessedFOS.json"


if __name__ == '__main__':
    fos_data = pd.read_excel('NABS_FOS_update_2020-08-20_ed_VS.xlsx')[['FOS NAME', 'FOS NUMBER', 'SDG']].drop_duplicates()

    # Ignore fos list
    ignore_fos = fos_data[fos_data['SDG'] == 'NOT RELEVANT']['FOS NUMBER'].unique()

    sdg_fos = dict()
    for fos_name, fos_id, sdg_nr in tqdm(fos_data[~fos_data['FOS NUMBER'].isin(ignore_fos)].values):
        sdg_label = f'SDG_{sdg_nr}'
        if sdg_label not in sdg_fos.keys():
            sdg_fos[sdg_label] = []
        sdg_fos[sdg_label].append((str(fos_id), fos_name))

    for sdg_label in sorted(sdg_fos.keys(), key=lambda x: int(x.split('_')[-1])):
        sdg_fos[sdg_label] = sorted(sdg_fos[sdg_label], key=lambda x: x[1])

    with open(FNAME_PROCESSED_KEY_TERMS, 'w') as file_:
        json.dump(sdg_fos, file_)
