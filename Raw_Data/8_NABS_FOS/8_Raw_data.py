#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 15 15:47:41 2020

@author: lukas
"""
import json
from tqdm import tqdm

replacables_symbols = ["&" , "-"  , '"' ,  "  "]
replacables_words = ["and" , "or" , "for", "&" , "of" , "sdg" , "oecd" , "arctic"]

def pre_proc( list_o_strings ):
    """
    Keeps only the keywords longer than 4 characters ;
    Strips non Alphanumeric chars ;
    Removes basic interluding words ( "and" , "of" , etc. ) ;
    Deduplicates
    """

    processed = []
    alpha = "abcdefghijklmnopqrstuvwxyz0123456789 "
    for item in list_o_strings :
        item = item.replace("_" , " ")
        item = item.lower()

        for c in replacables_symbols:
            item = item.replace( c , " " )
        item_p = item.split()
        item = " ".join(i for i in item_p if i not in replacables_words)

        if all( c in alpha for c in item ) :
            if item.startswith( " " ) :
                item = item[ 1: ]
            if item.endswith( " " ) :
                item = item[:-1]
            if len(item) >  4 :
                if item not in processed:
                    processed.append( item )
    return processed


file = open("EnvFOS.json" , "r")
input_data = json.loads( file.read() )
file.close()

file = open("FOSMAP.json"  , "r")
fos_map = json.loads( file.read() )
file.close()


map = {'Protection of atmosphere and climate' : "SDG_13",
        'Protection of ambient air': "SDG_11",
        'Solid waste': "SDG_11",
        'Protection of ambient water' : "SDG_14",
        'Protection of soil and groundwater' : "SDG_6",
        'Noise and vibration' : "SDG_11",
        'Protection of species and habitats' : "SDG_15",
        'Protection against natural hazards' : "SDG_11",
        'Radioactive pollution' : "SDG_11" }

sdg_words_raw = {}

for key , value in input_data.items() :
    sdg = map[ key ]
    if sdg not in sdg_words_raw.keys() :
        sdg_words_raw[ sdg ] = []
    plh = [fos_map[i] for i in value if i in fos_map.keys()]

    sdg_words_raw[ sdg ] += plh

counter = 0
print("Key Words Identified before cleaning : " )
for key , value in sdg_words_raw.items() :
    print( key , " : ", len(value))
    counter += len(value)

print("Overall : ", counter)

#%%
for key , value in sdg_words_raw.items() :
    sdg_words_raw[ key ] = pre_proc( value )

#%%
"""
Deduplicating keywords
"""
word_freq_dict = {}
for val in list(sdg_words_raw.values()) :
    for v in val :
        if v not in word_freq_dict :
            word_freq_dict[ v ] = 1
        else:
            word_freq_dict[ v ] += 1

#%%
sdg_words = {}
for key , value in sdg_words_raw.items() :
    plh = [ i  for i in value if word_freq_dict[i] < 2]
    sdg_words[ key ] = plh

#%%
js = json.dumps( sdg_words )
file = open( "8_ProcessedKeyTerms.json" , "w")
file.write( js )
file.close()

counter = 0
print("Key Words Identified after cleaning: " )
for key , value in sdg_words.items() :
    print( key , " : ", len(value))
    counter += len(value)

print("Overall : ", counter)
