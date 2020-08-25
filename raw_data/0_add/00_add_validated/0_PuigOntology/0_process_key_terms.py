#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 17:39:53 2020

@author: lukas
"""
import json


data = {}

file = open("Ontology.csv" , "r" , encoding = "latin1")
for line in file :
    parts = line[:-1].split(";")
    if len(parts) == 1:
        break
    else: 
       if  parts[1] != "clasification" :
            if parts[1] in data:    
                data[ parts[1] ].append( parts[0] )
            else:
                data[ parts[1] ] = [ parts[0] ]
file.close()

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
data_proc = {}

for key , value in data.items() :
    key2 = key.replace("SDG" , "SDG_")
    data_proc[ key2 ] = pre_proc( value )


#%%
js = json.dumps( data_proc )
file = open("0_ProcessedKeyTerms.json" , "w")
file.write( js )
file.close()
