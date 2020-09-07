from multiprocessing import cpu_count
from tqdm import tqdm
from utils import process_fosname, levenshtein_ratio, sws, sdg_label_sort

import concurrent.futures
import json
import os
import pandas as pd


def process_add_all_to_all_fos():
    path = 'raw_data/0_add/02_add_all_to_all'
    processed_fos = dict()
    add_all_to_all_data_paths = [
        f'{path}/{directory_name}'
        for directory_name in os.listdir(path)
        if '.' not in directory_name
        ]
    for directory in add_all_to_all_data_paths:
        try:
            processed_sdg_fos_fname = list(filter(lambda oname: '_ProcessedFOS.json' in oname, os.listdir(directory)))[0]
        except IndexError:
            print('Sdg FOS are not processed in {directory}')
            continue
        with open(f'{directory}/{processed_sdg_fos_fname}', 'r') as file_:
            processed_sdg_fos = json.load(file_)
        for sdg_label, fos in processed_sdg_fos.items():
            if sdg_label not in processed_fos.keys():
                processed_fos[sdg_label] = set()
            processed_fos[sdg_label].update(map(lambda x: tuple(x), fos))
    processed_fos = map(lambda fos: (str(fos[0]), fos[1]), processed_fos)

    return processed_fos


def process_replace_fos():
    replace_fos = []

    path = 'raw_data/1_replace'
    add_replace_data_paths = sorted([
        f'{path}/{directory_name}'
        for directory_name in os.listdir(path)
        if '.' not in directory_name
        ], key=lambda x: int(x.split('/')[1].split('_')[0]))

    for directory in add_replace_data_paths:
        try:
            processed_replace_fos_fname = list(filter(lambda oname: '_ReplaceFOS.json' in oname, os.listdir(directory)))[0]
        except IndexError:
            print('Sdg replace FOS are not processed in {directory}')
            continue
        with open(f'{directory}/{processed_replace_fos_fname}', 'r') as file_:
            processed_replace_fos = json.load(file_)
        replace_fos += list(processed_replace_fos.items())
    replace_fos = map(lambda rp_fos: (str(rp_fos[0]), rp_fos[1]), replace_fos)

    return replace_fos


def process_remove_fos():
    remove_fos = dict()

    path = 'raw_data/2_remove'
    add_remove_data_paths = [
        f'{path}/{directory_name}'
        for directory_name in os.listdir(path)
        if '.' not in directory_name
        ]
    for directory in add_remove_data_paths:
        try:
            processed_remove_fos_fname = list(filter(lambda oname: '_RemoveFOS.json' in oname, os.listdir(directory)))[0]
        except IndexError:
            print('Sdg remove FOS are not processed in {directory}')
            continue
        with open(f'{directory}/{processed_remove_fos_fname}', 'r') as file_:
            processed_remove_fos = json.load(file_)

        for sdg_label, fos_ids in processed_remove_fos.items():
            if sdg_label not in remove_fos.keys():
                remove_fos[sdg_label] = set()
            remove_fos[sdg_label].update(map(lambda fos_id: str(fos_id), fos_ids))

    return remove_fos


with open("CombinedOntology.json", "r") as file_:
    sdg_terms = json.loads(file_.read())

with open('FOSMAP_700.json', 'r') as file_:
    fos_map_700 = json.load(file_)

with open("FOSMAP.json", "r") as file_:
    fos_map = json.loads(file_.read())
fos_to_match = [(fos_id, process_fosname(fos_name)) for fos_id, fos_name in fos_map.items()]


"""
    Matching with Fields of Study from MS Academic (v10-10-2019)
    Match criteria:
        all tokens from a concept must be present in FOS name
        levenstein similarity between concept and FOS name must be > 0.85
"""
sdg_matched_fos = dict()


def _match_terms_to_fos(sdg_label, terms, fos_to_match, sws, use_pbar, total):
    sdg_matched_fos = dict()
    if use_pbar:
        step = total // len(terms)
        total = step * len(terms)
        p_bar = tqdm(terms, desc=f'Processing {sdg_label}', total=total, leave=True)
    for term, sources in terms:
        matched_fos = []
        term_parts = list(filter(lambda w: w not in sws, term.split()))
        for fos_id, fos_name in fos_to_match:
            if all(p in fos_name for p in term_parts) and levenshtein_ratio(term, fos_name) > 0.85:
                matched_fos.append([str(fos_id), fos_name])

        matched_fos = sorted(matched_fos, key=lambda x: x[1])
        matched_fos_ids, matched_fos_names = list(map(lambda x: x[0], matched_fos)), list(map(lambda x: x[1], matched_fos))
        sdg_matched_fos[term] = {
            "sources": sorted(sources),
            "matched_FOS_ids": matched_fos_ids,
            "matched_FOS_names": matched_fos_names
            }

        if use_pbar:
            p_bar.update(step)
    if use_pbar:
        p_bar.close()

    return sdg_label, sdg_matched_fos


n_workers = cpu_count() - 1
for sdg_label, terms in sdg_terms.items():
    terms = list(terms.items())
    term_batches = []
    bs = (len(terms) + n_workers - 1) // n_workers
    for i in range(n_workers):
        batch = terms[i*bs:(i+1)*bs]
        if batch:
            term_batches.append(batch)
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = []
        for i, batch in enumerate(term_batches):
            use_pbar = i == (len(term_batches) - 2)
            futures.append(executor.submit(
                _match_terms_to_fos,
                sdg_label, batch, fos_to_match[:], sws,
                use_pbar=use_pbar, total=len(terms)
            ))

        for future in concurrent.futures.as_completed(futures):
            sdg_label, matched_fos = future.result()
            if sdg_label not in sdg_matched_fos.keys():
                sdg_matched_fos[sdg_label] = dict()
            sdg_matched_fos[sdg_label].update(matched_fos)

sdg_labels = sorted(sdg_matched_fos.keys(), key=sdg_label_sort)
sdg_matched_fos = {
    sdg_label: {
        fos: sdg_matched_fos[sdg_label][fos] for fos in sorted(sdg_matched_fos[sdg_label].keys())
    } for sdg_label in sdg_labels
}
with open("SdgMatchedFOS.json", "w") as file_:
    json.dump(sdg_matched_fos, file_)


sdg_fos = dict()
for sdg_label, sdg_term_data in sdg_matched_fos.items():
    foses = set()
    for term_data in list(sdg_term_data.values()):
        foses.update(term_data['matched_FOS_ids'])
    sdg_fos[sdg_label] = foses

print('\n\n\t--- Percentage of matched FOS ---')
for sdg_label, sdg_term_data in sdg_matched_fos.items():
    c = sum(not term_data["matched_FOS_ids"] for term_data in sdg_term_data.values())
    print(f'\t{sdg_label} - {100 - int(c * 100 / len(sdg_term_data))}%')


"""
    Adding 0_add/02_all_to_all FOS
"""
processed_all_to_all_fos = process_add_all_to_all_fos()
for sdg_label, foses in processed_all_to_all_fos.items():
    fos_ids = list(map(lambda fos: fos[0], foses))
    if sdg_label not in sdg_fos.keys():
        sdg_fos[sdg_label] = set()
    sdg_fos[sdg_label].update(fos_ids)


"""
    Replacing 1_replace/ FOS
"""
data_replaced_fos = {'fos_id': [], 'fos_name': [], 'from_sdg': [], 'to_sdg': []}
processed_replace_fos = process_replace_fos()
for fos_id, moves in processed_replace_fos:
    fos_name = fos_map_700.get(fos_id, '')
    for from_sdg, to_sdg in moves:
        try:
            sdg_fos[from_sdg].remove(fos_id)
        except KeyError:
            from_sdg = ''
        sdg_fos[to_sdg].add(fos_id)

        data_replaced_fos['fos_id'].append(fos_id)
        data_replaced_fos['fos_name'].append(fos_name)
        data_replaced_fos['from_sdg'].append(from_sdg)
        data_replaced_fos['to_sdg'].append(to_sdg)

pd.DataFrame(data_replaced_fos).sort_values(['from_sdg', 'to_sdg', 'fos_name']).to_excel(
    'raw_data/1_replace/ReplacedFOS.xlsx', index=False
    )

"""
    Removing 2_remove/ FOS
"""
data_removed_fos = {'sdg_label': [], 'fos_id': [], 'fos_name': []}
removed_fos = dict()
processed_remove_fos = process_remove_fos()
for sdg_label, fos_to_remove in processed_remove_fos.items():
    if sdg_label not in removed_fos.keys():
        removed_fos[sdg_label] = set()

    if sdg_label in sdg_fos.keys():
        removed_fos[sdg_label].update(sdg_fos[sdg_label].intersection(fos_to_remove))
        sdg_fos[sdg_label] = sdg_fos[sdg_label].difference(fos_to_remove)
    else:
        removed_fos[sdg_label] = []

for sdg_label, rm_fos_ids in removed_fos.items():
    for fos_id in rm_fos_ids:
        fos_name = fos_map_700.get(str(fos_id))
        if not fos_name:
            fos_name = ''
        data_removed_fos['sdg_label'].append(sdg_label)
        data_removed_fos['fos_id'].append(fos_id)
        data_removed_fos['fos_name'].append(fos_name)

pd.DataFrame(data_removed_fos).sort_values(['sdg_label', 'fos_name']).to_excel(
    'raw_data/2_remove/RemovedFOS.xlsx', index=False
    )

"""
    Writing to file
"""
for sdg_label, fos_ids in sdg_fos.items():
    sdg_fos[sdg_label] = sorted(fos_ids)

print("\n\t--- Final FOS Count ---")
for sdg_label, foses in sdg_fos.items():
    print(f'\t{sdg_label} - {len(foses)}')

with open('SdgFOS.json', 'r') as file_:
    sdg_fos_old = json.load(file_)

with open('SdgFOS_ver-min-1.json', 'w') as file_:
    json.dump(sdg_fos_old, file_)

with open("SdgFOS.json", "w") as file_:
    json.dump(sdg_fos, file_)


"""
    Comparing to the last SdgFOS.json version
"""
update_info = {
    'sdg': [],
    'new_fos_id': [], 'new_fos_name': [],
    'removed_fos_id': [], 'removed_fos_name': []
}
for sdg_label in sorted(set(list(sdg_fos.keys()) + list(sdg_fos_old.keys())), key=sdg_label_sort):
    try:
        fos_old = sdg_fos_old[sdg_label]
    except KeyError:
        fos_old = []
    try:
        fos_new = sdg_fos[sdg_label]
    except KeyError:
        fos_new = []

    fos_add = list(set(fos_new).difference(fos_old))
    fos_removed = list(set(fos_old).difference(fos_new))

    print('\tSDG\tCOUNT_OLD\tCOUNT_NEW')
    print(f'\t{sdg_label}\t{len(fos_old)}\t{len(fos_new)}')

    for fos_id, fos_name in zip(fos_add, list(map(lambda fos_id: fos_map_700.get(fos_id, '__unknown__'), fos_add))):
        update_info['sdg'].append(sdg_label)
        update_info['new_fos_id'].append(fos_id)
        update_info['new_fos_name'].append(fos_name)
        update_info['removed_fos_id'].append('')
        update_info['removed_fos_name'].append('')

    for fos_id, fos_name in zip(fos_removed, list(map(lambda fos_id: fos_map_700.get(fos_id, '__unknown__'), fos_removed))):
        update_info['sdg'].append(sdg_label)
        update_info['new_fos_id'].append('')
        update_info['new_fos_name'].append('')
        update_info['removed_fos_id'].append(fos_id)
        update_info['removed_fos_name'].append(fos_name)

pd.DataFrame(update_info).sort_values(['sdg', 'new_fos_name', 'removed_fos_name']).to_excel(
    'UPDATE_INFO.xlsx', index=False
    )
