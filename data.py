import pandas as pd
import numpy as np
import os
filedir = os.path.dirname(os.path.abspath(__file__))


prods = pd.read_csv(filedir + "/prods.csv")
actions = pd.read_csv(filedir + "/actions.csv")
buyers = pd.read_csv(filedir + "/buyers.csv")


def nan_1_and_0(df, only_value):
    df.loc[df == only_value] = 1
    df.fillna(0)


prods.columns = ["id1", "id2", "id3", "create_date", "description", "deleted", "deleteddate", "product_name", "id4", "id5", "name", "picture", "surl", "updated_date", "deleted_date", "category"]

for unused_col in ["deleteddate", "surl"]:
    del prods[unused_col]


prods = prods.drop_duplicates()


### Actions
for col in actions.columns:
    if actions[col].dtype == np.object:
        unique = actions[col].describe()["unique"]
        if unique == 1:
            top = actions[col].describe()["top"]
            nan_1_and_0(actions[col], top)

actions["context_product"] = actions["context_page_path"].str.split("/").str[-1]
actions.rename(columns={"id": "actions_id"}, inplace = True)

### Modify
products_missing_from_prods = list(set(actions["context_product"].values) - set(prods["name"].values))

products_missing_df = pd.DataFrame(products_missing_from_prods, columns=["name"])
prods = prods.append(products_missing_df).reset_index(drop=True)
prods = prods.drop_duplicates()


prods2 = prods.groupby(["name"]).agg({
    "category": {
        "joined_category": lambda x: " ".join([y if isinstance(y, str) else str(y) for y in x ]),
        "count": lambda x: len(x)
    },
    "id1": {"no_of_rows": "count"},
    "picture": {"picture": "first"},
    "description": {"description": "first"},
    "product_name": {"product_name": "first"},
}).reset_index()
prods2.columns = ["name"] + list(prods2.columns.droplevel(0)[1:])

del prods["category"]

positive_actions = ["Liked Product", "Added Product To List", "Followed User", "Followed Brand", "Followed List", "saved product"]

actions2 = actions.groupby(["user_id", "context_product"]).agg({
    "action": {
        "positive_action_count": lambda x: len([y for y in x if y in positive_actions])
        }
    }).reset_index()
actions2.columns = ["user_id", "context_product"] + list(actions2.columns.droplevel(0)[2:])



buyers2 = buyers.groupby(["owner"]).nunique()
del buyers2["owner"]
buyers2 = buyers2.reset_index()

buyers3 = buyers.groupby(["owner"]).agg({
    "_id": {"_id": "count"},
    "description": {"description": "first"},
    "name": {"name": "first"}
}).reset_index()
buyers3.columns = ["owner"] + list(buyers3.columns.droplevel(0)[1:])

buyers2 = buyers3[["owner", "_id", "description"]].merge(buyers2[["owner", "description", "value", "name"]], on="owner")
del buyers3
buyers2.columns = ["owner", "no_of_rows", "description", "no_of_products", "no_of_categories", "name"]



df = actions2.merge(buyers2, left_on="user_id", right_on="owner", how="left").merge(prods2, left_on="context_product", right_on="name", how="left")




def action_timeline(user_id, product):
    return actions.loc[(actions["user_id"] == user_id) & (actions["context_product"] == product), ["user_id", "context_product", "action"]]

actions_per_user = actions2[["user_id", "positive_action_count"]].groupby("user_id").sum().reset_index() #55.335 actions
actions_per_product = actions2[["context_product", "positive_action_count"]].groupby("context_product").sum().reset_index()





def get_prods():
    return prods2

def get_actions():
    return actions2

def get_buyers():
    return buyers2



