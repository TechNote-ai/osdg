import pandas as pd
import json


replacables_symbols = ["&", "-", '"', "  "]
replacables_words = ["and", "or", "for", "&", "of", "sdg", "oecd", "arctic"]


def pre_proc(list_o_tuples):
    """
    Keeps only the keywords longer than 4 characters ;
    Strips non Alphanumeric chars ;
    Removes basic interluding words ( "and" , "of" , etc. ) ;
    Deduplicates
    """

    processed = []
    alpha = "abcdefghijklmnopqrstuvwxyz0123456789 "
    for id_, item in list_o_tuples:
        item = item.replace("_", " ")
        item = item.lower()

        for c in replacables_symbols:
            item = item.replace(c, " ")
        item_p = item.split()
        item = " ".join(i for i in item_p if i not in replacables_words)

        if all(c in alpha for c in item):
            if item.startswith(" "):
                item = item[1:]
            if item.endswith(" "):
                item = item[:-1]
            if len(item) > 4:
                if item not in processed:
                    processed.append((id_, item))
    return processed


dfl = pd.read_excel("SDG FOS updated 06 01.xlsx").to_dict(orient="records")

sdg_words = {}

for row in dfl:
    if str(row['SDG number']) != "nan":
        sdg = f"SDG_{int(row['SDG number'])}"
        if sdg not in sdg_words.keys():
            sdg_words[sdg] = []
        sdg_words[sdg].append((row['FOS number'], row["FOS name"]))


counter = 0
print("Key Words Identified before cleaning : ")
for key, value in sdg_words.items():
    print(key, " : ", len(value))
    counter += len(value)

print("Overall : ", counter)

for key, value in sdg_words.items():
    sdg_words[key] = pre_proc(set(value))

with open("10_ProcessedFOS.json", "w") as file_:
    file_.write(json.dumps(sdg_words))

counter = 0
print("Key Words Identified after cleaning: ")
for key, value in sdg_words.items():
    print(key, " : ", len(value))
    counter += len(value)

print("Overall : ", counter)
