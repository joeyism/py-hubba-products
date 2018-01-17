import pandas as pd
import numpy as np
from collections import defaultdict


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

# for missing in prods2, scrape site
#for name in products_missing_from_prods:
#    actions_row = actions.loc[actions["context_product"] == name].iloc[0]
#    url = actions_row["context_page_url"]
#    #TODO: scrape and add to prods

products_missing_df = pd.DataFrame(products_missing_from_prods, columns=["name"])
prods = prods.append(products_missing_df).reset_index(drop=True)
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

positive_actions = ["Liked Product", "Added Product To List", "Followed User", "Followed Brand", "Followed List", "saved product"]

actions2 = actions[["user_id", "context_product", "action"]].groupby(["user_id", "context_product"]).agg({
    "action": {
        "positive_action_count": lambda x: len([y for y in x if y in positive_actions])
        }
    }).reset_index()
actions2.columns = ["user_id", "context_product"] + list(actions2.columns.droplevel(0)[2:])



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




def action_timeline(user_id, product):
    return actions.loc[(actions["user_id"] == user_id) & (actions["context_product"] == product), ["user_id", "context_product", "action"]]

actions_per_user = actions2[["user_id", "positive_action_count"]].groupby("user_id").sum().reset_index() #55.335 actions
actions_per_product = actions2[["context_product", "positive_action_count"]].groupby("context_product").sum().reset_index()


from surprise import Reader, Dataset, SVD, evaluate, KNNBasic

def get_top_n(predictions, n=10):

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

reader = Reader(rating_scale = (0, 5))
dataset = Dataset.load_from_df(actions2, reader)

algo = SVD()


evaluate(algo, dataset, measures=["RMSE", "MAE"])
trainset = dataset.build_full_trainset()

algo.fit(trainset)
algo.predict("53ff5739aebb450829000074","affect-health-drinking-chocolate", 15)
algo.predict("53ff5739aebb450829000074","affect-health-drinking-chocolate", 0)

testset = trainset.build_anti_testset()
predictions = algo.test(testset)

top_n = get_top_n(predictions, n=10)

recommendations = {}
# Print the recommended items for each user
for uid, user_ratings in top_n.items():
    recommendations[uid]= [iid for (iid, _) in user_ratings]
