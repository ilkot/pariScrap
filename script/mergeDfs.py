import pandas as pd
from itertools import product
import glob

#%%merge data
localPath = "D:/github/pariScrap/data/"
files = [f for f in glob.glob(localPath+"*.csv")]
cols_2_drop = ['status','scrapDate']


df_merged_houses=pd.DataFrame()
for f in files:
    temp_data = pd.read_csv(f,index_col=[0])
    df_merged_houses=df_merged_houses.append(temp_data)
    

df_merged_houses_undup = df_merged_houses.drop_duplicates(subset=["id"])

cols = ["price","postCode1","postCode2"]
df_merged_houses_undup["lval"] = df_merged_houses_undup[cols].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
df_merged_houses_undup.sort_values(by="lval",inplace=True)


df_merged_houses_undup=df_merged_houses_undup.reset_index().drop(['index'],axis=1)
df_merged_houses_undup["adCount"] = 1

valCountLval = df_merged_houses_undup["lval"].value_counts().reset_index()
valCountLval = valCountLval[valCountLval["lval"]>1]

# write back each ad to their count number
for i1,i2 in product(range(len(valCountLval["index"])),range(len(df_merged_houses_undup["lval"]))): 
     if valCountLval["index"][i1] == df_merged_houses_undup["lval"][i2]:
         df_merged_houses_undup["adCount"][i2] = valCountLval["lval"][i1]
         
    
merged_houses_clean = df_merged_houses_undup.drop_duplicates(subset=["lval"])

#%%