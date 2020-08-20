#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 16:51:39 2020

@author: lukas
"""

import json
import os

#%%

directories = [i for i in os.listdir("./Raw_Data/") if "." not in i]

sdg_ontology_combined = {
    "SDG_1" : {} , 
    "SDG_2" : {} , 
    "SDG_3" : {} , 
    "SDG_4" : {} , 
    "SDG_5" : {} , 
    "SDG_6" : {} , 
    "SDG_7" : {} , 
    "SDG_8" : {} , 
    "SDG_9" : {} , 
    "SDG_10" : {} , 
    "SDG_11" : {} , 
    "SDG_12" : {} , 
    "SDG_13" : {} , 
    "SDG_14" : {} , 
    "SDG_15" : {} , 
    "SDG_16" : {} , 
    "SDG_17" : {} , 
    }


for directory in directories :
    file_name = [ i for i in os.listdir( "./Raw_Data/" + directory + "/" ) if "_ProcessedKeyTerms.json" in i ][0]
    with open( f'./Raw_Data/{directory}/{file_name}', 'r' ) as file_:
        processed_key_terms = json.loads( file_.read() )
    
    for sdg_label , key_terms in processed_key_terms.items() :
        for term in key_terms :
            if term not in sdg_ontology_combined[ sdg_label ].keys() :
                sdg_ontology_combined[ sdg_label ][ term ] = []
            sdg_ontology_combined[ sdg_label ][ term ].append( directory )
                
#%%
with open("CombinedOntology.json" , "w") as file_:
    file_.write( json.dumps( sdg_ontology_combined ) )
