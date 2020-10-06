import requests
import json
import csv
import os
import scrape
from datetime import datetime
from bs4 import BeautifulSoup

CURRENT_YEAR = datetime.today().year


# Scrape the pitchfork reviews page. Search 5 pages ~ 50 results.
def get_pitchfork_newreleases():
    albums = list()
    PAGES_TO_SEARCH = 5

    # Search the pages and append to list of album dicts.
    search_urls = ["https://pitchfork.com/reviews/albums/?page=%d" % i
        for i in range(1, PAGES_TO_SEARCH + 1)]
    for search_url in search_urls:
        albums.extend(scrape_page(search_url))

    return albums


# Scrape an individual pitchfork page.
def scrape_page(search_url):
    page = requests.get(search_url, headers={'User-agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')
    request_results = soup.find('body')

    # Scrape page for script that contains a "window.App" dict.
    request_results = request_results.find_all('script')
    for request_result in request_results:
        t = request_result.contents[0]
        if(t[:10] == "window.App"):
            script_results = json.loads(t[11:-1])
            script_results = (script_results['context']['dispatcher']
                ['stores']['ReviewsStore']['items'])
            break

    albums = list()
    for result in script_results.values():
        album_year = (result['tombstone']['albums']
            [0]['album']['release_year'])
        if album_year is None:
            continue
        if len(result['artists']) == 0:
            continue
        if CURRENT_YEAR - album_year > 1 or result['tombstone']['bnr']:
            continue

        artist_str = result['artists'][0]['display_name'].strip()
        title_str = result['title']
        rating_str = result['tombstone']['albums'][0]['rating']['rating']
        url = 'https://pitchfork.com%s' % result['url']

        genre_str = None
        if result['genres']:
            genre_str = result['genres'][0]['display_name']

        # Title Fix. Remove " EP" from end of string. Helps Spotipy.
        if title_str[-3:] == ' EP':
            title_str = title_str[:-3]

        albums.append({'artist': artist_str, 'title': title_str,
            'genre': genre_str, 'rating': float(rating_str),
            'url': url, 'source': 'pitchfork'})
    return albums


# Generate and sort by treblechef recommendation score.
def get_pitchfork_scores(album_list):
    for album in album_list:
        if not('sp_popularity' in album):
            album['sp_popularity'] = 0
        date_obj = datetime.strptime(album['sp_date'], "%Y-%m-%dT00:00.000Z")
        time_score = max(60 - (datetime.now() - date_obj).days, 0)
        album['score'] = (album['rating'] / 10) * 60 + \
            album['sp_popularity'] / 100 * 20 + time_score / 60 * 20
        album['score'] = round(album['score'], 3)

    album_list = sorted(album_list, key=lambda k: k['score'], reverse=True)
    return album_list


# WHERE THE SEARCHING TAKES PLACE ######################################

albums = get_pitchfork_newreleases()
pitchfork_scraper = scrape.AlbumScraper(albums)
albums = pitchfork_scraper.run()
albums = get_pitchfork_scores(albums)

# Sort by treblechef recommendation score.
albums = sorted(albums, key=lambda k: k['score'], reverse=True)

# Write results to csv and json files.
script_loc = os.path.dirname(os.path.realpath(__file__))
with open(script_loc + '/results/results_pf.csv', mode='w+') as csv_file:
    fieldnames = ['artist', 'title', 'genre', 'rating', 'score',
        'url', 'source', 'sp_popularity', 'sp_date',
        'sp_img', 'sp_album_id', 'sp_artist_id']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    csv_writer.writerows(albums)

with open(script_loc + '/results/results_pf.json', 'w+') as json_file:
    json.dump(albums, json_file, indent=4)
