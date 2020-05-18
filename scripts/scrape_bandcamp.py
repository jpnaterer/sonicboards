import requests
import json
import csv
import scrape
from datetime import datetime

# http://www.citizenshipcounts.ca/guide/regions1/canadas-5-regions
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
        x = requests.post(url, json=json_obj)
        request_results = x.json()

        for result in request_results['items']:
            # Skip albums that have genre within the ignore list.
            genre_str = result['genre']
            if genre_str in GENRES_TO_IGNORE:
                continue

            artist_str = result['artist']
            title_str = result['title']
            url_str = result['tralbum_url']

            results.append({'artist': artist_str, 'title': title_str,
                'genre': genre_str, 'region': region_str, 'url': url_str})

    return results


def get_bandcamp_scores(results):
    for r in results:
        if not('sp_popularity' in r):
            r['sp_popularity'] = 0
        date_obj = datetime.strptime(r['sp_date'], "%Y-%m-%dT00:00.000Z")
        time_score = max(60 - (datetime.now() - date_obj).days, 0)
        r['score'] = r['sp_popularity'] / 100 * 40 + time_score / 60 * 60
        r['score'] = round(r['score'], 3)

    # Sort by treblechef recommendation score.
    results = sorted(results, key=lambda k: k['score'], reverse=True)
    return results


# WHERE THE SEARCHING TAKES PLACE ######################################

# Retrieve primary locations by popularity.
releases_full = list()
for tag_str in ['toronto', 'montreal', 'vancouver']:
    print("Scraping Bandcamp %s" % tag_str)
    results = get_bandcamp_releases(tag_str)
    releases_full.extend(results)

# Retrieve secondary locations by date.
for region_str, location_id in LOCATION_CODES.items():
    print("Scraping Bandcamp %s" % region_str)
    results = get_bandcamp_releases('canada', page_count=10,
        location_id=location_id, region_str=region_str, sort_str='date')

    # Ensure the location is not yet in the current list.
    url_list = [r['url'] for r in releases_full]
    for result in results:
        if result['url'] not in url_list:
            releases_full.append(result)

    # Retrieve remaining secondary locations by popularity.
    results = get_bandcamp_releases('canada', page_count=1,
        location_id=location_id, region_str=region_str, sort_str='pop')

    # Ensure the location is not yet in the current list.
    url_list = [r['url'] for r in releases_full]
    for result in results:
        if result['url'] not in url_list:
            releases_full.append(result)

# Write results to a csv file before the spotify search for debugging.
# with open('results/canada_pre.csv', mode='w') as csv_file:
#    fieldnames = ['artist', 'title', 'genre', 'url', 'region']
#    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#    csv_writer.writeheader()
#    csv_writer.writerows(releases_full)

print('Fetching Spotify Information', end='', flush=True)
current_time = datetime.now()
releases_full = scrape.get_spotify_albums(releases_full)
releases_full = scrape.get_spotify_artist(releases_full)
releases_full = get_bandcamp_scores(releases_full)
print(", Completed in %ds" % (datetime.now() - current_time).seconds)

# Write results to csv and json files.
with open('results/canada.csv', mode='w') as csv_file:
    fieldnames = ['artist', 'title', 'genre', 'url',
        'region', 'score', 'sp_popularity',
        'sp_date', 'sp_img', 'sp_album_id', 'sp_artist_id']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    csv_writer.writeheader()
    csv_writer.writerows(releases_full)

with open('results/canada.json', 'w') as json_file:
    json.dump(releases_full, json_file, indent=4)
