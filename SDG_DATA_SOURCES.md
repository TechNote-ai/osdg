# SDG Data Sources

The ontology of terms used in the O-SDG Tool is derived from the following data sources:

| Index | Description | Folder Name | Link |
| ------ | ------ | ------ | ------ |
| 0. | SDG Ontology compiled by Dr Nuria B. Puig and E. Mauleon| 0_PuigOntology | [Dataset](https://figshare.com/articles/SDG_ontology/11106113/1) | 
| 1. | Mapping from "FP7-4-SD" Project (edited VS and LP) | 1_FP7-4-SD_edited | [Link to Project website](https://www.fp7-4-sd.eu/) |
| 2. | Concepts UN Linked SDG tool extracted from academic publications | 2_LinkedSDG_Concepts | [Link to LinkedSGS Tool](http://linkedsdg.apps.officialstatistics.org/#/) |
| 3. | Concepts extracted from SDG Pathfinder documents extracted via ML | 3_SDGPathfiner_DocumentConcepts | [Document Colletion](https://sdg-pathfinder.org/) ; [Modelling Description](https://ppmi.lt/)  |
| 4. | Keywords from SDG Pathfinder indicated by the SDG Pathfinder tool itself| 4_SDGPathfinder_Keywords| [SDG Pathfinder](https://sdg-pathfinder.org/) | 
| 5. | Concepts UN Linked SDG tool extracted from Administrative Documents | 5_LinkedSDG_DocumentExtracts | [Link to LinkedSGS Tool](http://linkedsdg.apps.officialstatistics.org/#/) |
| 6. | Terms by Indicator from SDGIO Ontology | 6_SDGIO_Terms | [Link to SDGIO GitHub ](https://github.com/SDG-InterfaceOntology/sdgio) |
| 7. | Concepts linked to SDGs from EC Policy Documents | 7_EC_Policy_Doc_Terms | Skrynik & Stanciauskas ( 2020 upcoming ) | 

# General Ontology Construction Procedure

Raw data from each source is checked for obvious formatting errors. Then it is deduplicated, so a term can only appear be assigned to **ONE** SDG. 
Then each data source is cleaned and adpated to the General Ontology with its own dedicated Script. Data from each source is merged into the General Ontology. 
Items from the General Ontology are then matched to the MAG Fields of Study to produce SDG-FOS Ontology. 


