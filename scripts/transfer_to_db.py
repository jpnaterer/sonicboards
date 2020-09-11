import pymongo
import json
import os
from datetime import datetime


def add_to_collection(collection, json_file):
    with open(json_file) as f:
        new_data = json.load(f)

    # Load previous albums from database.
    curr_data = list(collection.find())
    curr_urls = [i['url'] for i in curr_data]

    # Insert new albums to database, ensuring no duplicates are added.
    for d in new_data:
        if d['url'] in curr_urls:
            continue
        d['sp_date'] = datetime.strptime(d['sp_date'], "%Y-%m-%dT00:00.000Z")
        collection.insert_one(d)


def update_scores(collection, source_str):
    if source_str == 'pitchfork' or source_str == 'allmusic':
        curr_data = list(collection.find({'source': source_str}))
    else:
        curr_data = list(collection.find())

    for d in curr_data:
        date_obj = d['sp_date']
        if source_str == 'bandcamp':
            time_score = max(60 - (datetime.now() - date_obj).days, 0)
            new_score = d['sp_popularity'] / 100 * 40 + time_score / 60 * 60
        elif source_str == 'allmusic':
            time_score = max(30 - (datetime.now() - date_obj).days, -30)
            new_score = (d['rating'] / 5) * 25 + \
                d['sp_popularity'] / 100 * 35 + time_score / 30 * 40
        elif source_str == 'pitchfork':
            time_score = max(30 - (datetime.now() - date_obj).days, -30)
            new_score = (d['rating'] / 10) * 40 + \
                d['sp_popularity'] / 100 * 20 + time_score / 30 * 40
        new_score = round(max(new_score, 0), 3)

        q_search = {'_id': d['_id']}
        q_update = {'$set': {'score': new_score}}
        collection.update_one(q_search, q_update)


# Establish connection to mongodb and add json files to collections
connect = pymongo.MongoClient()
result_loc = os.path.dirname(os.path.realpath(__file__)) + '/results/'
add_to_collection(connect.sonicboards.canada, result_loc + 'canada.json')
add_to_collection(connect.sonicboards.reviews, result_loc + 'results_pf.json')
add_to_collection(connect.sonicboards.reviews, result_loc + 'results_am.json')

# Load full database and update all scores on popularity and recency.
update_scores(connect.sonicboards.canada, 'bandcamp')
update_scores(connect.sonicboards.reviews, 'pitchfork')
update_scores(connect.sonicboards.reviews, 'allmusic')

# Set update timestamp in config collection.
collection = connect.sonicboards.config
collection.update_one({}, {'$set': {'date': datetime.now()}})

# sudo systemctl start mongod
# robo3t, postman for post requests
# mongoexport --collection=canada --db=sonicboards --out=canada.json
# mongoexport --collection=reviews --db=sonicboards --out=reviews.json
# mongoexport --collection=config --db=sonicboards --out=config.json
# mongoimport --collection=canada --db=sonicboards --file=canada.json
# mongoimport --collection=reviews --db=sonicboards --file=reviews.json
# mongoimport --collection=config --db=sonicboards --file=config.json
