from tqdm import tqdm

import json
import pandas as pd


FNAME_PROCESSED_KEY_TERMS = "8_ProcessedFOS.json"


replacables_symbols = ["&", "-", '"', "  "]
replacables_words = ["and", "or", "for", "&", "of", "sdg", "oecd", "arctic"]


def pre_proc(list_o_tuples):
    processed = []
    alpha = "abcdefghijklmnopqrstuvwxyz0123456789 "
    for id_, item in list_o_tuples:
        item = item.replace("_", " ")
        item = item.lower()

        for c in replacables_symbols:
            item = item.replace(c, " ")
        item_p = item.split()
        item = " ".join(i for i in item_p if i not in replacables_words)

        if all(c in alpha for c in item):
            if item.startswith(" "):
                item = item[1:]
            if item.endswith(" "):
                item = item[:-1]
            if len(item) > 4:
                if item not in processed:
                    processed.append((id_, item))
    return processed


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

    for sdg_label, foses in sdg_fos.items():
        sdg_fos[sdg_label] = pre_proc(foses)

    print('-' * 100)
    counter = 0
    with open('update_info.txt', 'w') as file_:
        print('SDG\tCount\n')
        file_.write('SDG\tCount')
        for sdg_label in sorted(sdg_fos.keys(), key=lambda x: int(x.split('_')[1])):
            foses = sdg_fos[sdg_label]
            print(f'{sdg_label}\t{len(foses)}')
            file_.write(f'{sdg_label}\t{len(foses)}\n')
            counter += len(foses)
        print(f'\nOverall : {counter}')
        file_.write(f'Overall : {counter}')

    with open(FNAME_PROCESSED_KEY_TERMS, 'w') as file_:
        json.dump(sdg_fos, file_)
