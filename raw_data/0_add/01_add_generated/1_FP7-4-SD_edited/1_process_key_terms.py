#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 17:02:48 2020

@author: lukas
"""

import json

#Hand curated list of bad FOS ids
from bad_fos import *
#%%
file = open("WU_projectSDGs.json" , "r")
project_sdgs = json.loads( file.read() )
file.close()

file = open("ProjectFOS.json" , "r")
project_fos = json.loads( file.read() )
file.close()

file = open("FOSMAP.json" , "r")
fos_map = json.loads( file.read() )
file.close()


#%%
"""
Taking Top 5 FOS'es from each project 
Checking if they are not EU project slang related FOS'es (bad_fos)
Assigning them to SDGs and deduplicating
"""
sdg_fos_raw = {}
for key , value in project_sdgs.items() :
    fos = [ i[0] for i in sorted( project_fos[ key ].items() , key = lambda kv:kv[1] , reverse = True)[0:10] if int( i[ 0 ] ) not in bad_fos ]
    for v in value :
        if v not in sdg_fos_raw.keys() :
            sdg_fos_raw[ v ] = set()
        for f in fos :
            sdg_fos_raw[ v ].add( f )
            
for key , value in sdg_fos_raw.items() :
    sdg_fos_raw[ key ] = list( value )

#Data on SDG 17 in this set is very poor quality ; removing it
pop = sdg_fos_raw.pop("SDG_17", None)

#%%
"""
Removing certain some FOS'es that were assigned to projects but do not align well with SDGs
"""
sdg_fos_raw["SDG_1"] = [ i for i in sdg_fos_raw["SDG_1"] if int(i) not in bad_sdg1_fos]            
sdg_fos_raw["SDG_2"] = [ i for i in sdg_fos_raw["SDG_2"] if int(i) not in bad_sdg2_fos]  

sdg_fos_raw["SDG_3"] = [ i for i in sdg_fos_raw["SDG_3"] if int(i) not in bad_sdg3_fos]  
sdg_fos_raw["SDG_4"] = [ i for i in sdg_fos_raw["SDG_4"] if int(i) not in bad_sdg4_fos]  
sdg_fos_raw["SDG_5"] = [ i for i in sdg_fos_raw["SDG_5"] if int(i) not in bad_sdg5_fos]  
sdg_fos_raw["SDG_6"] = [ i for i in sdg_fos_raw["SDG_6"] if int(i) not in bad_sdg6_fos]  

sdg_fos_raw["SDG_7"] = [ i for i in sdg_fos_raw["SDG_7"] if int(i) not in bad_sdg7_fos]  

sdg_fos_raw["SDG_8"] = [ i for i in sdg_fos_raw["SDG_8"] if int(i) not in bad_sdg8_fos]  
sdg_fos_raw["SDG_9"] = [ i for i in sdg_fos_raw["SDG_9"] if int(i) not in bad_sdg9_fos]  
sdg_fos_raw["SDG_10"] = [ i for i in sdg_fos_raw["SDG_10"] if int(i) not in bad_sdg10_fos]  

sdg_fos_raw["SDG_11"] = [ i for i in sdg_fos_raw["SDG_11"] if int(i) not in bad_sdg11_fos]  
sdg_fos_raw["SDG_12"] = [ i for i in sdg_fos_raw["SDG_12"] if int(i) not in bad_sdg12_fos]  
sdg_fos_raw["SDG_13"] = [ i for i in sdg_fos_raw["SDG_13"] if int(i) not in bad_sdg13_fos]  
sdg_fos_raw["SDG_14"] = [ i for i in sdg_fos_raw["SDG_14"] if int(i) not in bad_sdg14_fos]  
sdg_fos_raw["SDG_15"] = [ i for i in sdg_fos_raw["SDG_15"] if int(i) not in bad_sdg15_fos]  
sdg_fos_raw["SDG_16"] = [ i for i in sdg_fos_raw["SDG_16"] if int(i) not in bad_sdg16_fos]  


#%%
"""
Deduplicating FOS
"""
fos_freq_dict = {}
for val in list(sdg_fos_raw.values()) :
    for v in val :
        if v not in fos_freq_dict :
            fos_freq_dict[ v ] = 1
        else:
            fos_freq_dict[ v ] += 1
            
#%%
sdg_fos = {}
for key , value in sdg_fos_raw.items() :
    plh = [ i  for i in value if fos_freq_dict[i] < 2]
    sdg_fos[ key ] = plh

  
#js = json.dumps( sdg_fos )
#file = open("NewWU.json" , "w")
#file.write( js )
#file.close() 
    
#%%
sdg_fos_s = {}
for key , value in sdg_fos_raw.items() :
    plh = [ fos_map[ i ].lower()  for i in value if fos_freq_dict[i] < 2 and i in fos_map.keys() ]
    sdg_fos_s[ key ] = plh
    
    
#%%
js = json.dumps( sdg_fos_s )
file = open("1_ProcessedKeyTerms.json" , "w")
file.write( js )
file.close() 
    
#%%
"""
for key , value in sdg_fos.items() :
    file = open( key+".txt" , "w")
    for v in value :
        line =  v + "\t" + fos_map[ v ] +"\n"
        file.write( line )
    file.close()
"""