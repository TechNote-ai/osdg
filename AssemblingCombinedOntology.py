from collections import OrderedDict

import json
import os
import re


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


# Gather *_ProcessedSDGFOS -----
sdg_fos_add_validated, sdg_fos_add_generated = dict(), dict()
fos_sources = dict()

# Validated
for directory in add_validated_data_paths:
    try:
        processed_sdg_fos_fname = list(filter(lambda oname: '_ProcessedKeyTerms.json' in oname, os.listdir(directory)))[0]
        with open(f'{directory}/{processed_sdg_fos_fname}', 'r') as file_:
            processed_sdg_fos = json.load(file_)
        processed_sdg_fos = {sdg_label: processed_sdg_fos[sdg_label] for sdg_label in sorted(processed_sdg_fos.keys())}
    except IndexError:
        print('Sdg Fos are not processed in {directory}')
        continue

    for sdg_label, foses in processed_sdg_fos.items():
        if sdg_label not in sdg_fos_add_validated.keys():
            sdg_fos_add_validated[sdg_label] = set()
        sdg_fos_add_validated[sdg_label].update(foses)

        # Update fos sources
        if sdg_label not in fos_sources.keys():
            fos_sources[sdg_label] = OrderedDict()
        for fos in sdg_fos_add_validated[sdg_label]:
            if fos not in fos_sources[sdg_label].keys():
                fos_sources[sdg_label][fos] = []
            fos_sources[sdg_label][fos].append(directory.split('/')[-1])

# All to all    # TODO leave it for matching? if not, it goes into assembling sdg_fos_script. Must be checked for conflicts when assembling generated
for directory in add_all_to_all_data_paths:
    try:
        processed_sdg_fos_fname = list(filter(lambda oname: '_ProcessedFos.json' in oname, os.listdir(directory)))[0]
        with open(f'{directory}/{processed_sdg_fos_fname}', 'r') as file_:
            processed_sdg_fos = json.load(file_)
        processed_sdg_fos = {sdg_label: processed_sdg_fos[sdg_label] for sdg_label in sorted(processed_sdg_fos.keys())}
    except IndexError:
        print('Sdg Fos are not processed in {directory}')
        continue

    for sdg_label, foses in processed_sdg_fos.items():
        foses = list(map(lambda x: x[1], foses))    # TODO All to all has ids and might move to Assemblign SdgFos script
        if sdg_label not in sdg_fos_add_validated.keys():
            sdg_fos_add_validated[sdg_label] = set()
        sdg_fos_add_validated[sdg_label].update(foses)

        # Update fos sources
        if sdg_label not in fos_sources.keys():
            fos_sources[sdg_label] = OrderedDict()
        for fos in sdg_fos_add_validated[sdg_label]:
            if fos not in fos_sources[sdg_label].keys():
                fos_sources[sdg_label][fos] = []
            fos_sources[sdg_label][fos].append(directory.split('/')[-1])

sdg_fos_add_validated = {
    sdg_label: sorted(list(sdg_fos_add_validated[sdg_label]))
    for sdg_label in sorted(sdg_fos_add_validated, key=lambda x: int(re.findall(r'\d+', x)[0]))
    }

with open(f'{INTER_ADD_PATH}/ValidatedSdgFos.json', 'w') as file_:
    json.dump(sdg_fos_add_validated, file_)


# Generated
gen_fos_sources = dict()

for directory in add_generated_data_paths:
    try:
        processed_sdg_fos_fname = list(filter(lambda oname: '_ProcessedKeyTerms.json' in oname, os.listdir(directory)))[0]
        with open(f'{directory}/{processed_sdg_fos_fname}', 'r') as file_:
            processed_sdg_fos = json.load(file_)
        processed_sdg_fos = {sdg_label: processed_sdg_fos[sdg_label] for sdg_label in sorted(processed_sdg_fos.keys())}
    except IndexError:
        print('SDG FOS are not processed in {directory}')
        continue

    for sdg_label, foses in processed_sdg_fos.items():
        if sdg_label not in sdg_fos_add_generated.keys():
            sdg_fos_add_generated[sdg_label] = set()
        sdg_fos_add_generated[sdg_label].update(foses)

        # Update gen fos source
        for fos in sdg_fos_add_generated[sdg_label]:
            if fos not in fos_sources[sdg_label].keys():
                fos_sources[sdg_label][fos] = []
            fos_sources[sdg_label][fos].append(directory.split('/')[-1])

fos_dist = OrderedDict()
for foses in sdg_fos_add_generated.values():
    for fos in foses:
        if fos not in fos_dist.keys():
            fos_dist[fos] = 1
        else:
            fos_dist[fos] += 1

multi_sdg_fos = sorted([fos for fos, freq in fos_dist.items() if freq > 1])     # TODO add to file to keep track

for sdg_label, foses in sdg_fos_add_generated.items():
    foses = foses.difference(multi_sdg_fos)
    for v_sdg_label, v_foses in sdg_fos_add_validated.items():
        if v_sdg_label != sdg_label:
            foses = foses.difference(v_foses)
    sdg_fos_add_generated[sdg_label] = foses

    # Update fos source for both validated and generated
    if sdg_label in gen_fos_sources.keys():
        for fos_name, sources in gen_fos_sources[sdg_label].items():
            if fos_name in sdg_fos_add_generated[sdg_label]:
                if fos_name not in fos_sources[sdg_label].keys():
                    fos_sources[sdg_label][fos_name] = []
                fos_sources[sdg_label][fos_name] += sources

sdg_fos_add_generated = {
    sdg_label: sorted(list(sdg_fos_add_generated[sdg_label]))
    for sdg_label in sorted(sdg_fos_add_generated, key=lambda x: int(re.findall(r'\d+', x)[0]))
    }

with open(f'{INTER_ADD_PATH}/GeneratedSdgFos.json', 'w') as file_:
    json.dump(sdg_fos_add_generated, file_)

# Combined Validated and Generated Sdg Fos
sdg_ontology_combined = OrderedDict()

sdg_labels = sorted(set(list(sdg_fos_add_validated.keys()) + list(sdg_fos_add_generated.keys())), key=lambda x: int(re.findall(r'\d+', x)[0]))
for sdg_label in sdg_labels:
    sdg_ontology_combined[sdg_label] = OrderedDict()
    validated_fos = sdg_fos_add_validated[sdg_label] if sdg_label in sdg_fos_add_validated.keys() else []
    generated_fos = sdg_fos_add_generated[sdg_label] if sdg_label in sdg_fos_add_generated.keys() else []

    for fos in sorted(list(set(validated_fos + generated_fos))):
        if fos not in sdg_ontology_combined[sdg_label].keys():
            sdg_ontology_combined[sdg_label][fos] = dict()
        sdg_ontology_combined[sdg_label][fos] = sorted(fos_sources[sdg_label][fos], key=lambda x: int(re.findall(r'\d+', x)[0]))

with open("CombinedOntology.json", "w") as file_:
    file_.write(json.dumps(sdg_ontology_combined))
