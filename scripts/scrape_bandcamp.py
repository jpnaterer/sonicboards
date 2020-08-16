import requests
import json
import csv
import time
import os
import scrape
from datetime import datetime

# A dict of numerical location codes used by the bandcamp API.
LOCATION_CODES = {'novascotia': 6091530, 'ottawa': 6094817, 'pei': 6113358,
    'newbrunswick': 6087430, 'saskatchewan': 6141242, 'newfoundland': 6354959,
    'victoria': 6174041, 'edmonton': 5946768, 'calgary': 5913490,
    'manitoba': 6065171, 'ontario': 6093943, 'quebec': 6115047,
    'britishcolumbia': 5909050, 'alberta': 5883102}


def get_bandcamp_releases(tag_str, page_count=10,
        location_id=0, region_str=None, sort_str='pop'):
    url = 'https://bandcamp.com/api/hub/2/dig_deeper'
    GENRES_TO_IGNORE = ['metal', 'podcasts', 'classical', 'latin',
        'spoken word', 'comedy', 'kids', 'audiobooks']

    # If no region input, assume it is the same as the input tag.
    if not(region_str):
        region_str = tag_str

    # Search by popularity not date, to remove bandcamp bloat.
    results = list()
    for i in range(1, page_count + 1):
        json_obj = {"filters": {"format": "all", "location": location_id,
            "sort": sort_str, "tags": [tag_str]}, "page": i}

        # Attempt search, if fail, wait 5s to try again.
        x = requests.post(url, json=json_obj)
        if (not x.ok):
            print("*** Failed Search, Continuing in 5s ***")
            time.sleep(5)
            x = requests.post(url, json=json_obj)
        request_results = x.json()

        for result in request_results['items']:
            # Skip albums that have genre within the ignore list.
            genre_str = result['genre']
            if genre_str in GENRES_TO_IGNORE:
                continue
            # Skip albums that have not released, aka, are up for pre-order.
            if result['is_preorder']:
                continue

            artist_str = result['artist']
            title_str = result['title']
            url_str = result['tralbum_url']

            results.append({'artist': artist_str, 'title': title_str,
                'genre': genre_str, 'region': region_str, 'url': url_str})

        # Stop searching for pages if we reach the final page.
        if(not request_results['more_available']):
            break

    return results


# A utility function to effectively search each region w/o duplicates.
def get_bandcamp_releases_util(album_list,
        tag_str='canada', location_id=0, region_str=None):

    # Complete one large recent release search and one small popular search.
    if region_str is None:
        res1 = get_bandcamp_releases(tag_str, page_count=10, sort_str='date')
        res2 = get_bandcamp_releases(tag_str, page_count=1, sort_str='pop')
    else:
        res1 = get_bandcamp_releases('canada', page_count=10,
            location_id=location_id, region_str=region_str, sort_str='date')
        res2 = get_bandcamp_releases('canada', page_count=1,
            location_id=location_id, region_str=region_str, sort_str='pop')

    # Ensure the url is not yet in the current list.
    url_list = [r['url'] for r in album_list]
    for result in res1:
        if result['url'] not in url_list:
            album_list.append(result)
    url_list = [r['url'] for r in album_list]
    for result in res2:
        if result['url'] not in url_list:
            album_list.append(result)

    return album_list


# Generate recommendation scores. These are likely overwritten when the
# data json files are transferred into the mongo database.
def get_bandcamp_scores(album_list):
    for r in album_list:
        if not('sp_popularity' in r):
            r['sp_popularity'] = 0
        date_obj = datetime.strptime(r['sp_date'], "%Y-%m-%dT00:00.000Z")
        time_score = max(60 - (datetime.now() - date_obj).days, 0)
        r['score'] = r['sp_popularity'] / 100 * 40 + time_score / 60 * 60
        r['score'] = round(r['score'], 3)
    album_list = sorted(album_list, key=lambda k: k['score'], reverse=True)
    return album_list


# WHERE THE SEARCHING TAKES PLACE ######################################

# Retrieve primary locations by popularity.
album_list = list()
for tag_str in ['toronto', 'montreal', 'vancouver']:
    print("Scraping Bandcamp %s" % tag_str)
    album_list = get_bandcamp_releases_util(album_list, tag_str)

# Retrieve secondary locations by date.
for region_str, location_id in LOCATION_CODES.items():
    print("Scraping Bandcamp %s" % region_str)
    album_list = get_bandcamp_releases_util(album_list,
        tag_str='canada', location_id=location_id, region_str=region_str)


# Write results to a csv file before the spotify search for debugging.
# with open('results/canada_pre.csv', mode='w') as csv_file:
#    fieldnames = ['artist', 'title', 'genre', 'url', 'region']
#    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#    csv_writer.writeheader()
#    csv_writer.writerows(album_list)

print('Fetching %d Spotify Results' % len(album_list), end='', flush=True)
current_time = datetime.now()
bandcamp_scraper = scrape.AlbumScraper(album_list)
album_list = bandcamp_scraper.run()
album_list = get_bandcamp_scores(album_list)
print(", Completed in %ds" % (datetime.now() - current_time).seconds)

# Write results to csv and json files.
script_loc = os.path.dirname(os.path.realpath(__file__))
with open(script_loc + '/results/canada.csv', mode='w+') as csv_file:
    fieldnames = ['artist', 'title', 'genre', 'url',
        'region', 'score', 'sp_popularity',
        'sp_date', 'sp_img', 'sp_album_id', 'sp_artist_id']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    csv_writer.writeheader()
    csv_writer.writerows(album_list)

with open(script_loc + '/results/canada.json', 'w+') as json_file:
    json.dump(album_list, json_file, indent=4)
