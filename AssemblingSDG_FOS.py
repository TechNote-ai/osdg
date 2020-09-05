from multiprocessing import cpu_count
from tqdm import tqdm
from utils import process_fosname, levenshtein_ratio, sws

import concurrent.futures
import json
import re

with open("CombinedOntology.json", "r") as file_:
    sdg_keywords = json.loads(file_.read())

with open("FOSMAP.json", "r") as file_:
    fos_map = json.loads(file_.read())
fos_to_match = [(fos_id, process_fosname(fos_name)) for fos_id, fos_name in fos_map.items()]


"""
    Matching with Fields of Study from MS Academic (v10-10-2019)
    Match criteria:
        all tokens from a concept must be present in FOS name
        levenstein similarity between concept and FOS name must be > 0.85
"""


def _match_keywords_to_fos(sdg_label, keywords, fos_to_match, sws, use_pbar, total):
    sdg_matched_ids, sdg_matched_names = dict(), dict()
    if use_pbar:
        step = total // len(keywords)
        total = step * len(keywords)
        p_bar = tqdm(keywords, desc=f'Processing {sdg_label}', total=total, leave=True)
    for keyword, sources in keywords:
        matches_fos_ids, matched_fos_names = [], []
        keyword_parts = list(filter(lambda w: w not in sws, keyword.split()))
        for fos_id, fos_name in fos_to_match:
            if all(p in fos_name for p in keyword_parts) and levenshtein_ratio(keyword, fos_name) > 0.85:
                matches_fos_ids.append(fos_id)
                matched_fos_names.append(fos_name)

        sdg_matched_ids[keyword] = {
            "sources": sources,
            "matchedFOS": matches_fos_ids
            }
        sdg_matched_names[keyword] = {
            "sources": sources,
            "matchedFOS": matched_fos_names
            }
        if use_pbar:
            p_bar.update(step)

    return sdg_label, sdg_matched_ids, sdg_matched_names


n_workers = cpu_count() - 1

sdg_fos_ids, sdg_fos_names = dict(), dict()
for sdg_label, keywords in sdg_keywords.items():
    keywords = list(keywords.items())
    keyword_batches = []
    bs = (len(keywords) + n_workers - 1) // n_workers
    for i in range(n_workers):
        batch = keywords[i*bs:(i+1)*bs]
        if keyword_batch:
            keyword_batches.append(batch)
    with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = []
        for i, batch in enumerate(keyword_batches):
            use_pbar = (i==len(keyword_batches)-2)
            futures.append(executor.submit(
                _match_keywords_to_fos,
                sdg_label, batch, fos_to_match[:], sws, 
                use_pbar=use_pbar, total=len(keywords)
            ))

        for future in concurrent.futures.as_completed(futures):
            sdg_label, matched_fos_ids, matched_fos_names = future.result()
            if sdg_label not in sdg_fos_ids.keys():
                sdg_fos_ids[sdg_label] = dict()
            if sdg_label not in sdg_fos_names.keys():
                sdg_fos_names[sdg_label] = dict()
            sdg_fos_ids[sdg_label].update(matched_fos_ids)
            sdg_fos_names[sdg_label].update(matched_fos_names)


with open("SDGFosIDs.json", "w") as file_:
    json.dump(sdg_fos_ids, file_)

with open("SDGFosNames.json", "w") as file_:
    json.dump(sdg_fos_names, file_)

f_sdg_fos = dict()
for sdg_label, sdg_fos_data in sdg_fos_ids.items():
    foses = set()
    for fos_data in list(sdg_fos_data.values()):
        foses.update(fos_data["matchedFOS"])
    f_sdg_fos[sdg_label] = sorted(list(foses))

print('\n\n\t--- Percentage of matched fos ---')
for sdg_label, sdg_fos_data in sdg_fos_ids.items():
    c = sum(not fos_data["matchedFOS"] for fos_data in sdg_fos_data.values())
    print(f'\t{sdg_label} - {100 - int(c * 100 / len(sdg_fos_data))}%')

print("\n\t--- Final FOS Count ---")
for sdg_label, foses in f_sdg_fos.items():
    print(f'\t{sdg_label} - {len(foses)}')

with open('SDGFos.json', 'r') as file_:
    sdg_fos_old = json.load(file_)

with open('SDGFos_ver-min-1.json', 'w') as file_:
    json.dump(sdg_fos_old, file_)

with open("SDGFos.json", "w") as file_:
    json.dump(f_sdg_fos, file_)

# Compare SDGFos.json to the last version
update_info = dict()
for sdg_label in sorted(set(list(f_sdg_fos.keys()) + list(sdg_fos_old.keys())), key=lambda x: re.findall(r'\d+', x)[0]):
    sdg_update_info = dict()
    
    try:
        fos_old = sdg_fos_old[sdg_label]
    except KeyError:
        fos_old = []
    try:
        fos_new = f_sdg_fos[sdg_label]
    except KeyError:
        fos_new = []

    fos_add = list(set(fos_new).difference(fos_old))
    fos_remove = list(set(fos_old).difference(fos_new))

    update_info[sdg_label] = {
        'count_old': len(fos_old),
        'count_new': len(fos_new),
        'added': fos_add,
        'removed': fos_remove
    }

with open('sdg_fos_update.json', 'w') as file_:
    json.dump(update_info, file_)
