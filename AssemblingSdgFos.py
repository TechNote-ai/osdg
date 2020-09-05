from multiprocessing import cpu_count
from tqdm import tqdm
from utils import process_fosname, levenshtein_ratio, sws

import concurrent.futures
import json
import pandas as pd
import re

with open("CombinedOntology.json", "r") as file_:
    sdg_terms = json.loads(file_.read())

with open("FOSMAP.json", "r") as file_:
    fos_map = json.loads(file_.read())
fos_to_match = [(fos_id, process_fosname(fos_name)) for fos_id, fos_name in fos_map.items()]


"""
    Matching with Fields of Study from MS Academic (v10-10-2019)
    Match criteria:
        all tokens from a concept must be present in FOS name
        levenstein similarity between concept and FOS name must be > 0.85
"""


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
                matched_fos.append([fos_id, fos_name])

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

sdg_matched_fos = dict()
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

sdg_labels = sorted(sdg_matched_fos.keys(), key=lambda x: int(re.findall(r'\d+', x)[0]))
sdg_matched_fos = {
    sdg_label: {
        fos: sdg_matched_fos[sdg_label][fos] for fos in sorted(sdg_matched_fos[sdg_label].keys())
    } for sdg_label in sdg_labels
}

with open("SdgMatchedFos.json", "w") as file_:
    json.dump(sdg_matched_fos, file_)


sdg_fos = dict()
for sdg_label, sdg_term_data in sdg_matched_fos.items():
    foses = set()
    for term_data in list(sdg_term_data.values()):
        foses.update(term_data['matched_FOS_ids'])
    sdg_fos[sdg_label] = sorted(list(foses))

print('\n\n\t--- Percentage of matched fos ---')
for sdg_label, sdg_term_data in sdg_matched_fos.items():
    c = sum(not term_data["matched_FOS_ids"] for term_data in sdg_term_data.values())
    print(f'\t{sdg_label} - {100 - int(c * 100 / len(sdg_term_data))}%')

print("\n\t--- Final FOS Count ---")
for sdg_label, foses in sdg_fos.items():
    print(f'\t{sdg_label} - {len(foses)}')

with open('SdgFos.json', 'r') as file_:
    sdg_fos_old = json.load(file_)

with open('SdgFos_ver-min-1.json', 'w') as file_:
    json.dump(sdg_fos_old, file_)

with open("SdgFos.json", "w") as file_:
    json.dump(sdg_fos, file_)

# Compare SDGFos.json to the last version
update_info = {
    'sdg': [], 
    'count_old': [], 'count_new': [], 
    'added_ids': [], 'added_names': [],
    'removed_ids': [], 'removed_names': []
}
for sdg_label in sorted(set(list(sdg_fos.keys()) + list(sdg_fos_old.keys())), key=lambda x: int(re.findall(r'\d+', x)[0])):
    sdg_update_info = dict()
    
    try:
        fos_old = sdg_fos_old[sdg_label]
    except KeyError:
        fos_old = []
    try:
        fos_new = sdg_fos[sdg_label]
    except KeyError:
        fos_new = []

    fos_add = list(set(fos_new).difference(fos_old))
    fos_remove = list(set(fos_old).difference(fos_new))

    update_info['sdg'].append(sdg_label)
    update_info['count_old'].append(len(fos_old))
    update_info['count_new'].append(len(fos_new))
    update_info['added_ids'].append(fos_add)
    update_info['added_names'].append(list(map(lambda x: fos_map[x], fos_add)))
    update_info['removed_ids'].append(fos_remove)
    update_info['removed_names'].append(list(map(lambda x: fos_map[x], fos_remove)))
    
pd.DataFrame(update_info).to_excel('UPDATE_INFO.xlsx', index=False)
