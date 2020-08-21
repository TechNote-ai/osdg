#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Friday July 15 18:15:41 2020

@author: SimonasTr
"""

import pandas as pd
import json
from tqdm import tqdm
import os

import ast

FNAME_PROCESSED_KEY_TERMS = "11_ProcessedKeyTerms.json"

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
            "13" : "SDG_13",
            "14" : "SDG_14",
            "15" : "SDG_15",
            "16" : "SDG_16",
            "17" : "SDG_17",
            }

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
        
#%%
upd = open('update_info.txt', 'w')

dfl = pd.read_excel("SDG FOS updated 06 12.xlsx").to_dict( orient = "records")

if FNAME_PROCESSED_KEY_TERMS in os.listdir():
    sdg_words_raw = {}
    with open(FNAME_PROCESSED_KEY_TERMS) as f:
        for key, value in json.load(f).items():
            sdg_words_raw[key] = value
else:
    sdg_words_raw = {}

upd.write('\n' + '_' * 100 + '\n')
upd.write("Key Words Identified before update : \n")
counter = 0
fos_counts = {}
for sdg_nr, foses in sdg_words_raw.items():
    counter += len(foses)
    upd.write(f'{sdg_nr}\t:\t{len(foses)}\n')
    fos_counts[sdg_nr] = {'initial': len(foses)}

upd.write(f'\nOverall : {counter}\n')

#%% Keyword update
for row in tqdm(dfl) :
    if str( row['SDG number'] ) != "nan" :
        number = str( int( row[ 'SDG number' ] ) )
        sdg = number_map[ number ]
        if sdg not in sdg_words_raw.keys() :
            sdg_words_raw[ sdg ] = []
            fos_counts[ sdg ] = {'initial': 0}
        sdg_words_raw[ sdg ].append( row["FOS name"] )

#%%
upd.write('\n' + '_' * 100 + '\n')
upd.write("Key Words Identified after update : \n")
counter = 0
for key , value in sdg_words_raw.items() :
    upd.write(f'{key}\t:\t{len(value)}\n')
    counter += len(value)

upd.write(f'\nOverall : {counter}\n')

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

sdg_words = {}
for key , value in sdg_words_raw.items() :
    plh = [ i  for i in value if word_freq_dict[i] < 2]
    sdg_words[ key ] = plh


upd.write('\n' + '_' * 100 + '\n')
upd.write("Key Words Identified after cleaning : \n")
counter = 0
for sdg_nr , foses in sdg_words.items() :
    upd.write(f'{sdg_nr}\t:\t{len(foses)}\n')
    counter += len(foses)
    fos_counts[sdg_nr]['updated'] = len(foses)
    fos_counts[sdg_nr]['change'] = fos_counts[sdg_nr]['updated'] - fos_counts[sdg_nr]['initial']

upd.write(f'\nOverall : {counter}\n')


upd.write('\n' + '_' * 100 + '\n')
upd.write("Key Words number change after update : \n")
upd.write('SDG\tInitial\tUpdated\tChange\n')
for sdg_nr , counts in fos_counts.items():
    upd.write(f"{sdg_nr}\t{counts['initial']}\t{counts['updated']}\t{counts['change']}\n")

upd.close()

#%%
with open(FNAME_PROCESSED_KEY_TERMS, "w") as json_file:
    json.dump(sdg_words, json_file)
