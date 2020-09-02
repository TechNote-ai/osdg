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

dfl = pd.read_excel("SDG FOS updated 06 01.xlsx").to_dict( orient = "records")


number_map = {"1" : "SDG_1" ,
            "2" : "SDG_2",
            "3" : "SDG_3",
            "4" : "SDG_4",
            "5" : "SDG_5",
            "6" : "SDG_6",
            "7" : "SDG_7",
            "8" : "SDG_8",
            "9" : "SDG_9",
            "10" : "SDG_10",
            "11" : "SDG_11",
            "12" : "SDG_12",
            "13" : "SDG_12",
            "14" : "SDG_14",
            "15" : "SDG_15",
            "16" : "SDG_16",
            "17" : "SDG_17",
            }

sdg_words = {}

for row in tqdm(dfl) :
    if str( row['SDG number'] ) != "nan" :
        number = str( int( row['SDG number'] ) )
        sdg = number_map[ number ]
        if sdg not in sdg_words.keys() :
            sdg_words[ sdg ] = []
        sdg_words[ sdg ].append( row["FOS name"] )


counter = 0
print("Key Words Identified before cleaning : " )
for key , value in sdg_words.items() :
    print( key , " : ", len(value))
    counter += len(value)

print("Overall : ", counter)

#%%
for key , value in sdg_words.items() :
    sdg_words[ key ] = pre_proc( set(value) )

#%%
js = json.dumps( sdg_words )
file = open( "10_ProcessedKeyTerms.json" , "w")
file.write( js )
file.close()

counter = 0
print("Key Words Identified after cleaning: " )
for key , value in sdg_words.items() :
    print( key , " : ", len(value))
    counter += len(value)

print("Overall : ", counter)
