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
            processed_fos[sdg_label].update(map(lambda x: (str(x[0]), x[1]), fos))

    return processed_fos


def process_replace_fos():
    replace_fos = []

    path = 'raw_data/1_replace'
    add_replace_data_paths = sorted([
        f'{path}/{directory_name}'
        for directory_name in os.listdir(path)
        if '.' not in directory_name
    ],
        key=lambda x: int(x.split('/')[-1].split('_')[0]))

    for directory in add_replace_data_paths:
        try:
            processed_replace_fos_fname = list(filter(lambda oname: '_ReplaceFOS.json' in oname, os.listdir(directory)))[0]
        except IndexError:
            print('Sdg replace FOS are not processed in {directory}')
            continue
        with open(f'{directory}/{processed_replace_fos_fname}', 'r') as file_:
            processed_replace_fos = json.load(file_)
        for fos_id, moves in processed_replace_fos.items():
            for move in moves:
                replace_fos.append((str(fos_id), move))
    
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


with open("InterimTerms.json", "r") as file_:
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
with open("MatchedFOS.json", "w") as file_:
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
    print(f'{sdg_label} - {len(foses)}')
    fos_ids = list(map(lambda fos: fos[0], foses))
    if sdg_label not in sdg_fos.keys():
        sdg_fos[sdg_label] = set()
    sdg_fos[sdg_label].update(fos_ids)


"""
    Replacing 1_replace/ FOS
"""
data_replaced_fos = {'fos_id': [], 'fos_name': [], 'from_sdg': [], 'to_sdg': []}
processed_replace_fos = process_replace_fos()
for fos_id, move in processed_replace_fos:
    fos_name = fos_map_700.get(fos_id, '')
    from_sdg, to_sdg = move
    try:
        sdg_fos[from_sdg].remove(fos_id)
    except KeyError:
        from_sdg = ''
    sdg_fos[to_sdg].add(fos_id)

    data_replaced_fos['fos_id'].append(fos_id)
    data_replaced_fos['fos_name'].append(fos_name)
    data_replaced_fos['from_sdg'].append(from_sdg)
    data_replaced_fos['to_sdg'].append(to_sdg)


df_replaced = pd.DataFrame(data_replaced_fos)
df_replaced.to_excel('raw_data/1_replace/ReplacedFOS.xlsx', index=False)

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

df_removed = pd.DataFrame(data_removed_fos).sort_values(['sdg_label', 'fos_name'])
df_removed.to_excel('raw_data/2_remove/RemovedFOS.xlsx', index=False)

"""
    Writing to file
"""
for sdg_label, fos_ids in sdg_fos.items():
    sdg_fos[sdg_label] = sorted(fos_ids)

print("\n\t--- Final FOS Count ---")
for sdg_label, foses in sdg_fos.items():
    print(f'\t{sdg_label} - {len(foses)}')

with open('OSDG-Ontology.json', 'r') as file_:
    sdg_fos_old = json.load(file_)

with open('OSDG-Ontology_ver-min-1.json', 'w') as file_:
    json.dump(sdg_fos_old, file_)

with open("OSDG-Ontology.json", "w") as file_:
    json.dump(sdg_fos, file_)

# Representative OSDG-Ontology
data_ontology = {'SDG label': [], 'FOS-ID': [], 'FOS-Name': [], 'Link to MAG': []}
for sdg_label, fos_ids in sdg_fos.items():
    sdg_nr = int(sdg_label.split('_')[1])
    for fos_id in fos_ids:
        fos_name = fos_map_700.get(fos_id, None)
        mag_link = f'https://academic.microsoft.com/topic/{fos_id}'
        data_ontology['SDG label'].append(sdg_nr)
        data_ontology['FOS-ID'].append(fos_id)
        data_ontology['FOS-Name'].append(fos_name)
        data_ontology['Link to MAG'].append(mag_link)

df_ontology = pd.DataFrame(data_ontology).sort_values(['SDG label', 'FOS-Name', 'FOS-ID'])
df_ontology['SDG label'] = df_ontology['SDG label'].apply(lambda sdg_nr: f'SDG_{sdg_nr}')

df_ontology.to_excel('OSDG-Ontology.xlsx', index=False)


"""
    Comparing to the last SdgFOS.json version
"""
with open('raw_data/0_add/02_add_all_to_all/8_NABS_FOS/8_ProcessedFOS.json', 'r') as file_:
    nabs = json.load(file_)

with open('raw_data/0_add/02_add_all_to_all/10_PPMI_boost/10_ProcessedFOS.json', 'r') as file_:
    boost = json.load(file_)

data = {
    'sdg': [],
    'add_or_remove': [],
    'fos_id': [], 'fos_name': [],
    'sources': [], 'isinReplaced': [], 'isinRemoved':[]
}
for sdg_label in sorted(set(list(sdg_fos.keys()) + list(sdg_fos_old.keys())), key=sdg_label_sort):
    old_foses = sdg_fos_old.get(sdg_label, [])
    new_foses = sdg_fos.get(sdg_label, [])

    added_foses = list(set(new_foses).difference(old_foses))
    removed_foses = list(set(old_foses).difference(new_foses))

    # Added
    for fos_id in added_foses:
        fos_name = fos_map_700[fos_id]
    
        sources = set()
        for mterm, mterm_data in sdg_matched_fos[sdg_label].items():
            if fos_id in mterm_data['matched_FOS_ids']:
                sources.update(mterm_data['sources'])

        # 8 Nabs & 10 boost aka ATA
        nabs_fos_ids = list(map(lambda fos: fos[0], nabs.get(sdg_label, [])))
        boost_fos_ids = list(map(lambda fos: fos[0], boost.get(sdg_label, [])))
        if fos_id in nabs_fos_ids:
            sources.add('8_NABS_FOS')
        if fos_id in boost_fos_ids:
            sources.add('10_PPMI_fos')
            
        # Replaced
        isin_replaced = fos_id in df_replaced[df_replaced.to_sdg == sdg_label].fos_id.astype(str).tolist()
        
        data['sdg'].append(sdg_label)
        data['add_or_remove'].append('add')
        data['fos_id'].append(fos_id)
        data['fos_name'].append(fos_name)
        data['sources'].append(list(sources) if list(sources) else None)
        data['isinReplaced'].append(isin_replaced)
        data['isinRemoved'].append(False)

    # Removed
    for fos_id in removed_foses:
        fos_name = fos_map_700[fos_id]
    
        sources = set()
        for mterm, mterm_data in sdg_matched_fos[sdg_label].items():
            if fos_id in mterm_data['matched_FOS_ids']:
                sources.update(mterm_data['sources'])

        # 8 Nabs & 10 boost aka ATA
        nabs_fos_ids = list(map(lambda fos: fos[0], nabs.get(sdg_label, [])))
        boost_fos_ids = list(map(lambda fos: fos[0], boost.get(sdg_label, [])))
        if fos_id in nabs_fos_ids:
            sources.add('8_NABS_FOS')
        if fos_id in boost_fos_ids:
            sources.add('10_PPMI_fos')
            
        # Replaced
        isin_replaced = fos_id in df_replaced[df_replaced.from_sdg == sdg_label].fos_id.astype(str).tolist()
        isin_removed = fos_id in df_removed[df_removed.sdg_label == sdg_label].fos_id.astype(str).tolist()
        
        data['sdg'].append(sdg_label)
        data['add_or_remove'].append('removed')
        data['fos_id'].append(fos_id)
        data['fos_name'].append(fos_name)
        data['sources'].append(list(sources) if list(sources) else None)
        data['isinReplaced'].append(isin_replaced)
        data['isinRemoved'].append(isin_removed)

df_comparison = pd.DataFrame(data).sort_values(['add_or_remove', 'isinReplaced', 'isinRemoved', 'sdg'])
df_comparison.to_excel('comparison_fos_update.xlsx', index=False)

