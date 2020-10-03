# SDG Data Sources

## Expert validated data sources

| Index | Description | Folder Name | Link |
| :------: | :------ | :------: | ------: |
| 0. | SDG Ontology compiled by Dr Nuria B. Puig and E. Mauleon| 0_PuigOntology | [Dataset](https://figshare.com/articles/SDG_ontology/11106113/1) | 
| 6. | Terms by Indicator from SDGIO Ontology | 6_SDGIO_Terms | [Link to SDGIO GitHub ](https://github.com/SDG-InterfaceOntology/sdgio) |
##
## Generated data sources

| Index | Description | Folder Name | Link |
| :------: | :------ | :------: | ------: |
| 1. | Mapping from "FP7-4-SD" Project (edited VS and LP) | 1_FP7-4-SD_edited | [Link to Project website](https://www.fp7-4-sd.eu/) |
| 2. | Concepts UN Linked SDG tool extracted from academic publications | 2_LinkedSDG_Concepts | [Link to LinkedSGS Tool](http://linkedsdg.apps.officialstatistics.org/#/) |
| 3. | Concepts extracted from SDG Pathfinder documents extracted via ML | 3_SDGPathfiner_DocumentConcepts | [Document Colletion](https://sdg-pathfinder.org/) ; [Modelling Description](https://ppmi.lt/)  |
| 4. | Keywords from SDG Pathfinder indicated by the SDG Pathfinder tool itself| 4_SDGPathfinder_Keywords| [SDG Pathfinder](https://sdg-pathfinder.org/) | 
| 5. | Concepts UN Linked SDG tool extracted from Administrative Documents | 5_LinkedSDG_DocumentExtracts | [Link to LinkedSGS Tool](http://linkedsdg.apps.officialstatistics.org/#/) |
| 7. | Concepts linked to SDGs from EC Policy Documents | 7_EC_Policy_Doc_Terms | Skrynnyk & Stanciauskas ( 2020 upcoming ) | 
| 9. | Keywords from "Science4SDGs" project | 9_SIRIS_Science4SDGs | [Link to "Science4SDGs" project](http://science4sdgs.sirisacademic.com/) |
##

## ATA data sources

| Index | Description | Folder Name | Link |
| :------: | :------ | :------: | ------: |
| 8. | FOS'es Linked to NABs Areas | 8_NABS_FOS | [Link to Eurostat](https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=CEPA_1994&StrLanguageCode=EN&IntPcKey=4431590&StrLayoutCode=HIERARCHIC) |
| 10. | A boost of SDG relevant FOS'es compiled by PPMI researchers | 10_PPMI_boost | [PPMI](https://ppmi.lt)|
#

***
# Ontology Construction Procedure

Assigned labels from raw data sources are assembled in two steps:
1. Assembling terms `AssemblingTerms.py`\
**Assembles terms from `raw_data/0_add/` data sources.**
    * *Term label conflicts from sources `00_add_validated/` are ignored meaning if `term_1` is assigned to `SDG_1` by `source_1` and to `SDG_2` by `source_2` **&rarr;** `term_1` is assigned to both.*
    * *Conflicts for term labels from `01_add_generated/` data sources are managed in two ways:* 
        - *If the conflict is between validated and generated term label **&rarr;** generated term label is discarded while validated one remains.*
        - *If the conflict is between generated & generated **&rarr;** both are discarded.*

    **&rarr;** **produces** `InterimTerms.json`
    ```python
    {
        'SDG_1': {
            'term_1': ['source_1', 'source_2', ...],
            'term_2': ['source_1', 'source_3', ...]
            ...
        }
        ...
    }
    ```
2. Assembling OSDG Ontology `AssemblingOntology.py`\
    **Assembles FOS from `InterimTerms.json` and `02_add_all_to_all/` data sources.**
    * 2.1. *Terms from `InterimTerms.json` are matched to  MAG Fields of Study subset `FOSMAP.json` which contains over 150 thousand fields.*
    * 2.2. *Matched FOS are added to the final ontology `FOS-Ontology.json` .*
    * 2.3. *`02_add_all_to_all/` FOS are added to the final ontology `FOS-Ontology.json` .*
    * 2.4 *Final ontology `FOS-Ontology.json` is adjusted based on `1_replace/` and `2_remove/` .*


    **&rarr;** **produces** `OSDG-Ontology.json`
    ```python
    {
        'SDG_1': ['fos_id_1', 'fos_id_2', ...],
        'SDG_2': ['fos_id_3', 'fos_id_4', ...]
        ...
    }
    ```

 

****
# Raw Data structure
* `raw_data/`
    * `0_add/`
        * `00_add_validated/`\
        **Expert validated term labels**\
        **&rarr;** each data source must produce:
            *`*_ProcessedKeyTerms.json`*
            ```python
            {
                'SDG_1': ['term_1', 'term_2', ...], 
                'SDG_2': ['term_3', 'term_4', ...],
                ...
            }
            ```
        * `01_add_generated/`\
        **Expert validated term labels**\
        **&rarr;** each data source must produce:
            *`*_ProcessedKeyTerms.json`*
            ```python
            {
                'SDG_1': ['term_1', 'term_2', ...], 
                'SDG_2': ['term_3', 'term_4', ...],
                ...
            }
            ```
        * `02_add_all_to_all/`\
        **Expert validated FOS labels**\
        **&rarr;** each data source must produce:
            *`*_ProcessedFOS.json`*
            ```python
            {
                'SDG_1': [['fos_id_1', 'fos_name_1'], ['fos_id_2', 'fos_name_2'], ...], 
                'SDG_2': [['fos_id_3', 'fos_name_3'], ['fos_id_4', 'fos_name_4'], ...],
                ...
            }
            ```
    * `1_replace/`\
    **Mapping for FOS SDG label reassignment from `SDG_a` to `SDG_b`**\
    **&rarr;** each data source must produce:
        *`*_ReplaceFOS.json`*
        ```python
        {
            'fos_id_1': [['SDG_1', 'SDG_2'], ...], 
            'fos_id_2': [['SDG_3', 'SDG_4'], ...],
            ...
        }
        ```
    * `2_remove/`\
    **FOS to remove from sdg assigned FOS lists**\
    **&rarr;** each data source must produce:
        *`*_RemoveFOS.json`*
        ```python
        {
            'SDG_1': ['fos_id_1', 'fos_id_2', ...], 
            'SDG_2': ['fos_id_1', 'fos_id_3', ...],
            ...
        }
        ```
    * `Blacklist`\
    **Irrelevant FOS**\
    **&rarr;** each data source must produce:
        *`*_Blacklist.csv`*
        | fos_id | fos_name |
        | :------  | :-------- |
        | fos_id_1 | fos_name_1 |
        | fos_id_2 | fos_name_2 |
        | ... | ...|




