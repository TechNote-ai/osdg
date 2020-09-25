from collections import OrderedDict
from utils import sdg_label_sort

import json
import os


INTER_ADD_PATH = 'raw_data/0_add'

add_validated_data_paths = [
    f'{INTER_ADD_PATH}/00_add_validated/{directory_name}'
    for directory_name in os.listdir(f'{INTER_ADD_PATH}/00_add_validated')
    if '.' not in directory_name
    ]

add_generated_data_paths = [
    f'{INTER_ADD_PATH}/01_add_generated/{directory_name}'
    for directory_name in os.listdir(f'{INTER_ADD_PATH}/01_add_generated')
    if '.' not in directory_name
    ]

add_all_to_all_data_paths = [
    f'{INTER_ADD_PATH}/02_add_all_to_all/{directory_name}'
    for directory_name in os.listdir(f'{INTER_ADD_PATH}/02_add_all_to_all')
    if '.' not in directory_name
    ]


# Gather *_ProcessedKeyTerms -----
sdg_terms_add_validated, sdg_terms_add_generated = dict(), dict()
term_sources = dict()

# Validated
for directory in add_validated_data_paths:
    try:
        processed_sdg_terms_fname = list(filter(lambda oname: '_ProcessedKeyTerms.json' in oname, os.listdir(directory)))[0]
        with open(f'{directory}/{processed_sdg_terms_fname}', 'r') as file_:
            processed_sdg_terms = json.load(file_)
        processed_sdg_terms = {sdg_label: processed_sdg_terms[sdg_label] for sdg_label in sorted(processed_sdg_terms.keys())}
    except IndexError:
        print(f'Sdg Terms are not processed in {directory}')
        continue

    for sdg_label, terms in processed_sdg_terms.items():
        if sdg_label not in sdg_terms_add_validated.keys():
            sdg_terms_add_validated[sdg_label] = set()
        sdg_terms_add_validated[sdg_label].update(terms)

        # Update term sources
        if sdg_label not in term_sources.keys():
            term_sources[sdg_label] = OrderedDict()
        for term in sdg_terms_add_validated[sdg_label]:
            if term not in term_sources[sdg_label].keys():
                term_sources[sdg_label][term] = []
            term_sources[sdg_label][term].append(directory.split('/')[-1])

# All to all    # TODO leave it for matching? if not, it goes into assembling sdg_fos_script. Must be checked for conflicts when assembling generated
for directory in add_all_to_all_data_paths:
    try:
        processed_sdg_fos_fname = list(filter(lambda oname: '_ProcessedFOS.json' in oname, os.listdir(directory)))[0]
        with open(f'{directory}/{processed_sdg_fos_fname}', 'r') as file_:
            processed_sdg_fos = json.load(file_)
        processed_sdg_fos = {sdg_label: processed_sdg_fos[sdg_label] for sdg_label in sorted(processed_sdg_fos.keys())}
    except IndexError:
        print(f'Sdg FOS are not processed in {directory}')
        continue

    for sdg_label, foses in processed_sdg_fos.items():
        terms = list(map(lambda x: x[1], foses))    # TODO All to all has ids and might move to Assemblign SdgFos script
        if sdg_label not in sdg_terms_add_validated.keys():
            sdg_terms_add_validated[sdg_label] = set()
        sdg_terms_add_validated[sdg_label].update(terms)

        # Update term sources
        if sdg_label not in term_sources.keys():
            term_sources[sdg_label] = OrderedDict()
        for term in sdg_terms_add_validated[sdg_label]:
            if term in terms:
                if term not in term_sources[sdg_label].keys():
                    term_sources[sdg_label][term] = []
                term_sources[sdg_label][term].append(directory.split('/')[-1])

sdg_terms_add_validated = {
    sdg_label: sorted(list(sdg_terms_add_validated[sdg_label]))
    for sdg_label in sorted(sdg_terms_add_validated.keys(), key=sdg_label_sort)
    }

with open(f'{INTER_ADD_PATH}/ValidatedSdgTerms.json', 'w') as file_:
    json.dump(sdg_terms_add_validated, file_)


# Generated
gen_term_sources = dict()

for directory in add_generated_data_paths:
    try:
        processed_sdg_terms_fname = list(filter(lambda oname: '_ProcessedKeyTerms.json' in oname, os.listdir(directory)))[0]
        with open(f'{directory}/{processed_sdg_terms_fname}', 'r') as file_:
            processed_sdg_terms = json.load(file_)
        processed_sdg_terms = {sdg_label: processed_sdg_terms[sdg_label] for sdg_label in sorted(processed_sdg_terms.keys())}
    except IndexError:
        print(f'Sdg Terms are not processed in {directory}')
        continue

    for sdg_label, terms in processed_sdg_terms.items():
        if sdg_label not in sdg_terms_add_generated.keys():
            sdg_terms_add_generated[sdg_label] = set()
        sdg_terms_add_generated[sdg_label].update(terms)

        # Update gen term sources
        for term in sdg_terms_add_generated[sdg_label]:
            if term not in term_sources[sdg_label].keys():
                term_sources[sdg_label][term] = []
            term_sources[sdg_label][term].append(directory.split('/')[-1])

term_dist = OrderedDict()
for terms in sdg_terms_add_generated.values():
    for term in terms:
        if term not in term_dist.keys():
            term_dist[term] = 1
        else:
            term_dist[term] += 1

multi_sdg_terms = [term for term, freq in term_dist.items() if freq > 1]     # TODO add to file to keep track

for sdg_label, terms in sdg_terms_add_generated.items():
    terms = terms.difference(multi_sdg_terms)
    for v_sdg_label, v_terms in sdg_terms_add_validated.items():
        if v_sdg_label != sdg_label:
            terms = terms.difference(v_terms)
    sdg_terms_add_generated[sdg_label] = terms

    # Update fos source for both validated and generated
    if sdg_label in gen_term_sources.keys():
        for term, sources in gen_term_sources[sdg_label].items():
            if term in sdg_terms_add_generated[sdg_label]:
                if term not in term_sources[sdg_label].keys():
                    term_sources[sdg_label][term] = []
                term_sources[sdg_label][term] += sources

sdg_terms_add_generated = {
    sdg_label: sorted(list(sdg_terms_add_generated[sdg_label]))
    for sdg_label in sorted(sdg_terms_add_generated.keys(), key=sdg_label_sort)
    }

with open(f'{INTER_ADD_PATH}/GeneratedSdgTerms.json', 'w') as file_:
    json.dump(sdg_terms_add_generated, file_)

# Combined Validated and Generated Sdg Terms
sdg_ontology_combined = OrderedDict()

ata_sources = [path.split('/')[-1] for path in add_all_to_all_data_paths]
sdg_labels = sorted(set(list(sdg_terms_add_validated.keys()) + list(sdg_terms_add_generated.keys())), key=sdg_label_sort)
for sdg_label in sdg_labels:
    sdg_ontology_combined[sdg_label] = OrderedDict()
    validated_terms = sdg_terms_add_validated[sdg_label] if sdg_label in sdg_terms_add_validated.keys() else []
    generated_terms = sdg_terms_add_generated[sdg_label] if sdg_label in sdg_terms_add_generated.keys() else []

    for term in sorted(list(set(validated_terms + generated_terms))):
        t_sources = sorted(term_sources[sdg_label][term], key=sdg_label_sort)
        if all(src in ata_sources for src in t_sources):
            continue
        if term not in sdg_ontology_combined[sdg_label].keys():
            sdg_ontology_combined[sdg_label][term] = dict()
        sdg_ontology_combined[sdg_label][term] = t_sources

with open("InterimTerms.json", "w") as file_:
    file_.write(json.dumps(sdg_ontology_combined))
