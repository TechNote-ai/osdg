#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 15 15:47:41 2020

@author: lukas
"""

import pandas as pd
import json
from tqdm import tqdm

import ast

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

dfl = pd.read_excel("ECPolicyDocs_Ngrams REVISED.xlsx").to_dict( orient = "records")


number_map = {"Goal_1" : "SDG_1" ,
            "Goal_2" : "SDG_2",
            "Goal_3" : "SDG_3",
            "Goal_4" : "SDG_4",
            "Goal_5" : "SDG_5",
            "Goal_6" : "SDG_6",
            "Goal_7" : "SDG_7",
            "Goal_8" : "SDG_8",
            "Goal_9" : "SDG_9",
            "Goal_10" : "SDG_10",
            "Goal_11" : "SDG_11",
            "Goal_12" : "SDG_12",
            "Goal_13" : "SDG_12",
            "Goal_14" : "SDG_14",
            "Goal_15" : "SDG_15",
            "Goal_16" : "SDG_16",
            "Goal_17" : "SDG_17",
            }

sdg_words_raw = {}

for row in tqdm(dfl) :
    number = row['Goal'].split(".")[0]
    sdg = number_map[ number ]
    if sdg not in sdg_words_raw.keys() :
        sdg_words_raw[ sdg ] = []
    sdg_words_raw[ sdg ] = list( ast.literal_eval(row["SDG&EC_NgramsOverlap"]))

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
file = open( "7_ProcessedKeyTerms.json" , "w")
file.write( js )
file.close()

counter = 0
print("Key Words Identified after cleaning: " )
for key , value in sdg_words.items() :
    print( key , " : ", len(value))
    counter += len(value)

print("Overall : ", counter)
