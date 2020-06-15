import pymongo
import langdetect
import collections
import pandas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import chi2
import numpy as np
from sklearn.feature_extraction import text as sk_text
import csv

# Get songs that contain lyrics and have no associated language.
connect = pymongo.MongoClient()
collection = connect.sonicboards.canada_songs
q = {"lyrics": {"$exists": True}, "lang": {"$exists": False}}
res = list(collection.find(q))

# Use langdetect library to detect lyric language.
for r in res:
    try:
        r["lang"] = langdetect.detect(r["lyrics"])
    except langdetect.lang_detect_exception.LangDetectException:
        r["lang"] = None

# Update language field in local database.
for r in res:
    v = {"$set": {"lang": r["lang"]}}
    collection.update_one({"_id": r["_id"]}, v)

# Merge canada songs and canada albums collections.
q = [{"$match": {"lyrics": {"$exists": True}, "lang": "en"}},
    {"$lookup": {"from": "canada", "localField": "album_id",
    "foreignField": "_id", "as": "album"}},
    {"$project": {"genre": "$album.genre", "lyrics": 1, "title": 1}},
    {"$match": {"genre": {"$nin": ["", "blues"]}}}]
res = collection.aggregate(q)
res = list(res)

count = collections.Counter([r["genre"][0] for r in res])
genres = set([r["genre"][0] for r in res])
print(count)
print(len(res))

# remove digits from string
for r in res:
    r['lyrics'] = ''.join([i for i in r['lyrics'] if not i.isdigit()])
    r['lyrics'] = r['lyrics'].replace("ʼ", "'")

df = pandas.DataFrame()
df['lyrics'] = [r["lyrics"] for r in res]
df['genre'] = [r["genre"][0] for r in res]

stop_words = ['html', 'craig', 'moreau', 'michael', 'hart', 'olive',
    'karl', 'olson', 'chorus', 'chords', 'verse', 'solo', 'jesse', 'jan',
    'potter', 'david', 'partridge', 'carolyn', 'ch', 'v2', 'lyrics',
    'leroux', 'outro', 'crowe', 'allison', 'http', 'selina', 'robbie',
    'jamieanderson', 'dave', 'com', 'hankewich', 'sauer', 'montreal',
    'trinidad', 'canada', 'michelle', 'creber', 'soulkeeper', 'celia',
    'writer', 'guy', 'wilfred', 'kozub', 'meryem', 'saci', 'geoff', 'cho',
    'panting', 'kendall', 'patrick', 'composed', 'performed', 'lo116',
    'pre', 'thanks', 'lynne', 'hanson', 'choruses', 'verses', 'frazer',
    'kinley', 'judy', 'jeanie', 'intro', 'instrumental', 'dan', 'legault',
    'oisin', 'legault', 'davies', 'tucker', 'colleen', 'capo', 'boland',
    'capitalicide', 'reg', 'im', 'shes', 'lisa', 'northern', 'haggard']
stop_words = sk_text.ENGLISH_STOP_WORDS.union(stop_words)
tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2',
    ngram_range=(1, 2), stop_words=stop_words)
features = tfidf.fit_transform(df.lyrics).toarray()
labels = df.genre

N = 10
g_out = dict()
for g in genres:
    features_chi2 = chi2(features, labels == g)
    indices = np.argsort(features_chi2[0])
    feature_names = np.array(tfidf.get_feature_names())[indices]
    unigrams = [v for v in feature_names if len(v.split(' ')) == 1]
    bigrams = [v for v in feature_names if len(v.split(' ')) == 2]
    print("# '{}':".format(g))
    print(" . {}".format('\n . '.join(unigrams[-N:])))
    g_out[g] = unigrams[-N:]
    # print("  . Correlated bigrams:\n. {}".format('\n. '.join(bigrams[-N:])))

with open('results/lyrics_keywords.csv', 'w') as f:
    dict_writer = csv.writer(f, delimiter=',')
    dict_writer.writerow(g_out.keys())
    dict_writer.writerows(zip(*g_out.values()))
