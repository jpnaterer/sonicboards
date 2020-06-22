import pymongo
import langdetect
import collections
import pandas
import re
import csv
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import chi2
from sklearn.feature_extraction import text as sk_text

# Examples
# https://towardsdatascience.com/multi-class-text-classification-with-scikit-learn-12f1e60e0a9f
# https://stackabuse.com/text-classification-with-python-and-scikit-learn/
# https://www.toptal.com/machine-learning/nlp-tutorial-text-classification
# https://www.analyticsvidhya.com/blog/2018/04/a-comprehensive-guide-to-understand-and-implement-text-classification-in-python/

stop_words = ['html', 'craig', 'moreau', 'michael', 'hart', 'olive',
    'karl', 'olson', 'chorus', 'chords', 'verse', 'solo', 'jesse', 'jan',
    'potter', 'david', 'partridge', 'carolyn', 'ch', 'lyrics', 'kosic',
    'leroux', 'outro', 'crowe', 'allison', 'http', 'selina', 'robbie',
    'jamieanderson', 'dave', 'com', 'hankewich', 'sauer', 'montreal',
    'trinidad', 'canada', 'michelle', 'creber', 'soulkeeper', 'celia',
    'writer', 'guy', 'wilfred', 'kozub', 'meryem', 'saci', 'geoff',
    'panting', 'kendall', 'patrick', 'composed', 'performed', 'lo116',
    'pre', 'thanks', 'lynne', 'hanson', 'choruses', 'verses', 'frazer',
    'kinley', 'judy', 'jeanie', 'intro', 'instrumental', 'dan', 'legault',
    'oisin', 'legault', 'davies', 'tucker', 'colleen', 'capo', 'boland',
    'capitalicide', 'reg', 'im', 'shes', 'lisa', 'northern', 'haggard',
    'ii', 'pearce', 'qui', 'hook', 'gary', 'cho', 'socan', 'por', 'te',
    'que', 'dont', 'ain', 'mona']
stop_words = sk_text.ENGLISH_STOP_WORDS.union(stop_words)


# Make text lowercase, remove words containing numbers, and replace apostrophes
def clean_text_func(text):
    text = text.lower()
    text = re.sub(r"\w*\d\w*", "", text)
    text = re.sub("ʼ", "'", text)
    return text


def get_lyrics():

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
    print(count)
    print(len(res))

    # create pandas data frame
    df = pandas.DataFrame()
    df['lyrics'] = [r["lyrics"] for r in res]
    df['genre'] = [r["genre"][0] for r in res]

    df['lyrics'] = df['lyrics'].apply(clean_text_func)
    return df


def get_genre_features(df):
    tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2',
        ngram_range=(1, 2), stop_words=stop_words)
    features = tfidf.fit_transform(df['lyrics']).toarray()

    N = 10
    g_out = dict()
    genres = set([d for d in df["genre"]])
    for g in genres:
        features_chi2 = chi2(features, df['genre'] == g)
        indices = np.argsort(features_chi2[0])
        feature_names = np.array(tfidf.get_feature_names())[indices]
        unigrams = [v for v in feature_names if len(v.split(' ')) == 1]
        print("# '{}':".format(g))
        print(" . {}".format('\n . '.join(unigrams[-N:])))
        g_out[g] = unigrams[-N:]

    return g_out


# https://www.youtube.com/watch?v=xvqsFTUsOmc
# https://github.com/adashofdata/nlp-in-python-tutorial
def get_dtm(df):
    # Generate document term matrix with count vectorizer.
    cv = CountVectorizer(stop_words=stop_words)
    data_cv = cv.fit_transform(df['lyrics']).toarray()
    data_dtm = pandas.DataFrame(data_cv, columns=cv.get_feature_names())
    top_dict = dict()
    for c in data_dtm.columns:
        top = data_dtm[c].sort_values(ascending=False).head(30)
        top_dict[c] = list(zip(top.index, top.values))
    print(top_dict)


df = get_lyrics()
g_out = get_genre_features(df)

with open('results/lyrics_keywords.csv', 'w') as f:
    dict_writer = csv.writer(f, delimiter=',')
    dict_writer.writerow(g_out.keys())
    dict_writer.writerows(zip(*g_out.values()))
