import data
from surprise import Reader, Dataset, SVD, evaluate, KNNBasic

prods = data.get_prods()
actions = data.get_actions()
buyers = data.get_buyers()

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
dataset = Dataset.load_from_df(actions[["user_id", "context_product"]], reader)

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
