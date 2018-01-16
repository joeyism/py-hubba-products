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
#for i in range(3):
#    prods["category"+str(i)] = prods["category"].str.split("__").str[i]


prods = prods.drop_duplicates()
prods2 = prods.groupby(["name"]).agg({
    "category": {
        "joined_category": lambda x: " ".join([y if isinstance(y, str) else str(y) for y in x ]),
        "count": lambda x: len(x)
    },
    "id1": {"no_of_rows": "count"}
}).reset_index()
prods2.columns = ["name"] + list(prods2.columns.droplevel(0)[1:])

del prods["category"]

### Actions
for col in actions.columns:
    if actions[col].dtype == np.object:
        unique = actions[col].describe()["unique"]
        if unique == 1:
            top = actions[col].describe()["top"]
            nan_1_and_0(actions[col], top)

actions["context_product"] = actions["context_page_path"].str.split("/").str[-1]
actions.rename(columns={"id": "actions_id"}, inplace = True)

actions2 = actions[["user_id", "context_product", "action"]].groupby(["user_id", "context_product"]).count().reset_index()

### Buyers
buyers2 = buyers.groupby(["owner"]).nunique()
del buyers2["owner"]
buyers2 = buyers2.reset_index()

buyers3 = buyers.groupby(["owner"]).count().reset_index()

buyers2 = buyers3[["owner", "_id"]].merge(buyers2[["owner", "description", "value"]], on="owner")
del buyers3
buyers2.columns = ["owner", "no_of_rows", "no_of_products", "no_of_categories"]


#actions["user_id"] == buyers["owner"]
# 5a4978af403d1a5afc74484a

#prods["name"] == actions["context_product"]
# mastrad-paris-pro-gourmet-hotcold-whipper-sst-0.5l

df = actions2.merge(buyers2, left_on="user_id", right_on="owner", how="left").merge(prods2, left_on="context_product", right_on="name", how="left")

# for missing in prods2, scrape site
for name in df.loc[df["name"].isnull()]["context_product"].unique():
    actions_row = actions.loc[actions["context_product"] == name].iloc[0]
    url = actions_row["context_page_url"]
    #TODO: scrape and add to prods


