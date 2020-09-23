import pandas as pd
import json


data_1 = pd.read_excel("SDG FOS updated 06 01.xlsx").to_dict(orient="records")
data_2 = pd.read_excel("SDG FOS updated 06 12.xlsx").to_dict(orient="records")

sdg_words = {}

for dfl in (data_1, data_2):
	for row in dfl:
	    if str(row['SDG number']) != "nan":
		    sdg = f"SDG_{int(row['SDG number'])}"
		    if sdg not in sdg_words.keys():
		        sdg_words[sdg] = []
		    sdg_words[sdg].append((str(row['FOS number']), row["FOS name"]))


counter = 0
print("Key Words Identified before cleaning : ")
for key, value in sdg_words.items():
    print(key, " : ", len(value))
    counter += len(value)

print("Overall : ", counter)

for sdg_label in sorted(sdg_words.keys(), key=lambda x: int(x.split('_')[-1])):
    sdg_words[sdg_label] = sorted(sdg_words[sdg_label], key=lambda x: x[1])

with open("10_ProcessedFOS.json", "w") as file_:
    file_.write(json.dumps(sdg_words))

counter = 0
print("Key Words Identified after cleaning: ")
for key, value in sdg_words.items():
    print(key, " : ", len(value))
    counter += len(value)

print("Overall : ", counter)
