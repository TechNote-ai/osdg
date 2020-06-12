## Methodology
OSDG aims to:
- integrate various existing attempts to classify research according to SustainableDevelopment Goals,
- make this process open, transparent and user-friendly.

OSDG integrates the existing research into a comprehensive approach, and does so in a way that evades the shortcomings of former individual approaches and duplication of research efforts.

<p align="center">
  <img src="/images/Methodology-visual_0511_Updated.png" alt="OSDG_Logo" width="400"/>
</p>

## About the project
In short, OSDG builds an **integrated ontology** from the feature sets identified in previous research, and then matches the ontology items to the topics from [Microsoft Academic](https://academic.microsoft.com/home).
OSDG takes relevant text features (such as ontology items, features from machine-learning models or extracted keywords) from the previous research, cleans them and merges them into a comprehensive, constantly-growing OSDG ontology. The ontology items are mapped to the ever-growing list of topics/Fields of Study in the Microsoft Academic Graph (MAG).
By doing this, we:
- expand the ontology – acquire more key terms associated with the relevant MAG Topics, natively called Fields of Study (FOS);
- capture more nuanced relationships between individual terms and latent concepts.

## How does OSDG work?
OSDG processes user queries in the following steps:
1) It tags the user query with FOS’es from Microsoft Academic Graph (MAG);
2) It cross-references the FOS’es assigned to the user query with the OSDG Ontology and determines which SDGs (if any) are relevant for the query;  
3) The relevance of a SDG to a query is interpreted as being “Strong” or “Moderate” depending on a specific threshold that is specifically adjusted for each SDG by testing the tool on a set of 16 000 scientific publication abstracts).

Head to the Search page to put our methodology to practical use. If you see something that requires improvement or you would like to contact our data team, please state your enquiry using our contact form.
## References and inspiration

The list of data sources used in the current version of the OSDG Tool are [here](https://github.com/TechNote-ai/osdg/blob/master/OSDG_DATA_SOURCES.md). OSDG leverages the data from [Microsoft Academic](https://academic.microsoft.com/home):

1) Sinha, A., Shen, Z., Song, Y., Ma, H., Eide, D., Hsu, B.-J. & Wang, K. (2015). AnOverview of Microsoft Academic Service (MAS) and Applications. Proceedings of the24th International Conference on World Wide Web (p./pp. 243--246), Republic andCanton of Geneva, Switzerland: International World Wide Web Conferences SteeringCommittee. ISBN: 978-1-4503-3473-0. doi:10.1145/2740908.27428398.
2) Wang, K., Shen, Z., Huang, C., Wu, C., Eide, D., Dong, Y., Qian, J., Kanakia, A., Chen,A.C., & Rogahn, R. (2019). A Review of Microsoft Academic Services for Science ofScience Studies. Frontiers in Big Data, 2. doi:10.3389/FDATA.2019.00045
