import pandas as pd
import numpy as np

prods = pd.read_csv("prods.csv")
actions = pd.read_csv("actions.csv")
buyers = pd.read_csv("buyers.csv")


def nan_1_and_0(df, only_value):
    df.loc[df == only_value] = 1
    df.fillna(0)


### Prods

# ['_id', 'b', 'c', 'createdat', 'd', 'deleted', 'deleteddate', 'n', 'o', 'p', 'slug', 'sp', 'surl', 'updatedat', 'deletedat', 'value']
prods.columns = ["id1", "id2", "id3", "create_date", "description", "deleted", "deleteddate", "product_name", "id4", "id5", "name", "picture", "surl", "updated_date", "deleted_date", "category"]

# remove columns with all NaNs
for unused_col in ["deleteddate", "surl"]:
    del prods[unused_col]

# Split categories by __, and store
for i in range(3):
    prods["category"+str(i)] = prods["category"].str.split("__").str[i]


prods2 = prods.groupby(["id1"]).agg({"category": lambda x: " ".join([y if isinstance(y, str) else str(y) for y in x ])}).reset_index()

prods3 = prods.groupby("id1").count()

### Actions
for col in actions.columns:
    if actions[col].dtype == np.object:
        unique = actions[col].describe()["unique"]
        if unique == 1:
            top = actions[col].describe()["top"]
            nan_1_and_0(actions[col], top)

actions["context_product"] = actions["context_page_path"].str.split("/").str[-1]

#actions["user_id"] == buyers["owner"]
# 5a4978af403d1a5afc74484a

#prods["name"] == actions["context_product"]
# mastrad-paris-pro-gourmet-hotcold-whipper-sst-0.5l

df = actions.merge(buyers, left_on="user_id", right_on="owner").merge(prods, left_on="context_product", right_on="name")
