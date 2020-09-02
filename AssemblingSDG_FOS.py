from tqdm import tqdm
from utils import process_fosname, levenshtein_ratio, sws
import concurrent.futures
import json


with open("FOSMAP.json", "r") as file_:
    fos_map = json.loads(file_.read())
fosmap_r = {process_fosname(name): id_ for id_, name in fos_map.items()}

with open("CombinedOntology.json", "r") as file_:
    sdg_keywords = json.loads(file_.read())


"""
    Matching with Fields of Study from MS Academic (v10-10-2019)
    Match criteria:
        all tokens from a concept must be present in FOS name
        levenstein similarity between concept and FOS name must be > 0.85
"""


def _match_to_fos(keyword, foses, sources):
    matches_fos_ids, matched_fos_names = [], []

    keyword_parts = list(filter(lambda w: w not in sws, keyword.split()))
    for fos_name, fos_id in fosmap_r.items():
        if all(p in fos_name for p in keyword_parts) and levenshtein_ratio(keyword, fos_name) > 0.85:
            matches_fos_ids.append(fos_id)
            matched_fos_names.append(fos_name)

    return matches_fos_ids, matched_fos_names, sources


sdg_fos_ids, sdg_fos_names = dict(), dict()

for sdg_label, keywords in sdg_keywords.items():
    sdg_matched_ids, sdg_matched_names = dict(), dict()
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=25) as executor:
        futures = []
        for keyword, sources in keywords.items():
            futures.append(executor.submit(
                _match_to_fos,
                keyword, fosmap_r, sources
                ))

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(keywords), desc=f'Processing {sdg_label}'):
            matches_fos_ids, matched_fos_names, sources = future.result()
            sdg_matched_ids[keyword] = {
                "sources": sources,
                "matchedFOS": matches_fos_ids
                }
            sdg_matched_names[keyword] = {
                "sources": sources,
                "matchedFOS": matched_fos_names
                }

    sdg_fos_ids[sdg_label], sdg_fos_names[sdg_label] = sdg_matched_ids, sdg_matched_names


with open("SDGFosIDs.json", "w") as file_:
    json.dump(sdg_fos_ids, file_)

with open("SDGFosNames.json", "w") as file_:
    json.dump(sdg_fos_names, file_)

f_sdg_fos = dict()
for sdg_label, sdg_fos_data in sdg_fos_ids.items():
    foses = set()
    for fos_data in list(sdg_fos_data.values()):
        foses.update(fos_data["matchedFOS"])
    f_sdg_fos[sdg_label] = list(foses)

print('\n\n--- Percentage of matched fos ---')
for sdg_label, sdg_fos_data in sdg_fos_ids.items():
    c = sum(not fos_data["matchedFOS"] for fos_data in sdg_fos_data.values())
    print(sdg_label, 100 - int(c * 100 / len(sdg_fos_data)), "%")

print("\n--- Final FOS Count ---")
for sdg_label, foses in f_sdg_fos.items():
    print(f'\t{sdg_label} - {len(foses)}')

with open('SDGFos.json', 'r') as file_:
    sdg_fos_old = json.load(file_)

with open('SDGFos_ver-min-1.json', 'w') as file_:
    json.dump(sdg_fos_old, file_)

with open("SDGFos.json", "w") as file_:
    json.dump('SDGF')

# --------------------------------------- Compare SDGFos.json to last version
update_info = dict()
for sdg_label in f_sdg_fos.keys():
    sdg_update_info = dict()

    fos_old = sdg_fos_old[sdg_label]
    fos_new = f_sdg_fos[sdg_label]

    fos_add = list(set(fos_new).difference(fos_old))
    fos_remove = list(set(fos_old).difference(fos_new))

    update_info[sdg_label] = {
        'count_old': len(fos_old),
        'count_new': len(fos_new),
        'added': fos_add,
        'removed': fos_remove
    }

with open('sdg_fos_update.json', 'w') as file_:
    file_.write(update_info, file_)
