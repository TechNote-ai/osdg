# SDG Data Sources

## Expert validated data sources

| Index | Description | Folder Name | Link |
| :------: | :------ | :------: | ------: |
| 0. | SDG Ontology compiled by Dr Nuria B. Puig and E. Mauleon| 0_PuigOntology | [Dataset](https://figshare.com/articles/SDG_ontology/11106113/1) | 
| 6. | Terms by Indicator from SDGIO Ontology | 6_SDGIO_Terms | [Link to SDGIO GitHub ](https://github.com/SDG-InterfaceOntology/sdgio) |

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


## ATA data sources

| Index | Description | Folder Name | Link |
| :------: | :------ | :------: | ------: |
| 8. | FOS'es Linked to NABs Areas | 8_NABS_FOS | [Link to Eurostat](https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=CEPA_1994&StrLanguageCode=EN&IntPcKey=4431590&StrLayoutCode=HIERARCHIC) |
| 10. | A boost of SDG relevant FOS'es compiled by PPMI researchers | 10_PPMI_boost | [PPMI](https://ppmi.lt)|

#
# General Ontology Construction Procedure

Raw data from each source is checked for obvious formatting errors. Then it is deduplicated, so a term can only appear be assigned to **ONE** SDG. 
Then each data source is cleaned and adpated to the General Ontology with its own dedicated Script. Data from each source is merged into the General Ontology. 
Items from the General Ontology are then matched to the MAG Fields of Study to produce SDG-FOS Ontology. 


