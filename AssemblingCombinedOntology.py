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

sdg_ontology_combined = {"SDG_1" : {} , 
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
                        "SDG_17" : {} , }


for d in directories :
    file_name = [i for i in os.listdir( "./Raw_Data/"+d+"/") if "_ProcessedKeyTerms.json" in i ][0]
    file = open( "./Raw_Data/"+d+"/"+file_name , "r")
    data = json.loads( file.read() )
    file.close()
    
    for key , value in data.items() :
        for v in value :
            if v not in sdg_ontology_combined[ key ].keys() :
                sdg_ontology_combined[ key ][ v ] =[ d ]
            else:
                sdg_ontology_combined[ key ][ v ].append( d )
                
#%%
js = json.dumps( sdg_ontology_combined )
file = open("CombinedOntology.json" , "w")
file.write( js )
file.close()