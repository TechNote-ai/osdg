#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 09:43:00 2020

@author: lukas
"""

import pandas as pd
import json
import ast



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
df = pd.read_excel( "OECD_SDG_betas.xlsx" )
#%%
"""
File includes TOP 1000 positive and negative beta coeficients from the regression models for both unigrams and ngrams
We will take top 200 ngrams and top 100 unigrams
"""

unigrams = list( df["Keywords_Positive"])
ngrams = list( df["Ngrams_Positive"])

sdg_words_raw = {}

for index, item in enumerate( unigrams ) :
    
    unigram_short =  [v[0] for v in sorted( ast.literal_eval( item ) , key = lambda kv : kv[1] , reverse = True )[0:50] ]
    ngram_short =  [v[0] for v in sorted( ast.literal_eval( ngrams[ index ] ) , key = lambda kv : kv[1] , reverse = True )[0:250] ]
    plh = unigram_short + ngram_short
    
    key = "SDG_" + str(index+1)
    
    sdg_words_raw[ key ] = pre_proc( plh )
    
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
bad_sdg3_terms = set( [ "data type" , 
                      "date signature" , 
                      "date start" , 
                      "date start date" , 
                      "deliverable list" , 
                      "deliverable wp" , 
                      "demonstrator dissemination" , 
                      "description deliverable" , 
                      "developed new" , 
                      "development new" , 
                      "dissemination activities" , 
                      "dissemination report" , 
                      "document version" , 
                      "ec contribution" ] )

sdg3_plh = [ i for i in sdg_words["SDG_3"] if i not in bad_sdg3_terms] 
sdg_words[ "SDG_3" ] = sdg3_plh

#%%
js = json.dumps( sdg_words )
file = open( "3_ProcessedKeyTerms.json" , "w")
file.write( js )
file.close()