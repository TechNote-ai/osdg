#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 10:16:21 2020

@author: lukas
"""


import pandas as pd
import json

#%%
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
dfl = pd.read_excel( "LinkedSDG_Data.xlsx" ).to_dict(orient="records")

sdg_words_raw = {}
for row in dfl :
    if str(row["Goal"]) != "nan" :
        sdg = row["Goal"].replace("Goal " , "SDG_")
        if sdg not in sdg_words_raw.keys() :
            sdg_words_raw[ sdg ] = []
        if str(row["Concept"]) != "nan" :
            sdg_words_raw[ sdg ].append( row["Concept"].lower() )
        if str(row["Keyword"]) != "nan" :
            sdg_words_raw[ sdg ].append( row["Keyword"].lower() )        
    
for key , value in list(sdg_words_raw.items()) :
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
file = open( "2_ProcessedKeyTerms.json" , "w")
file.write( js )
file.close()
