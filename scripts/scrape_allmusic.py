import requests
import json
import csv
import scrape
from datetime import datetime
from bs4 import BeautifulSoup


# Scrape the pitchfork reviews page. Search 3 pages ~ 50 results.
def get_allmusic_newreleases():
    search_url = "https://www.allmusic.com/newreleases"
    GENRE_IGNORE_LIST = ['Country', 'Classical']
    PAGES_TO_SEARCH = 3

    # Get the pages to search through.
    page = requests.get(search_url, headers={'User-agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.content, 'html.parser')
    request_results = soup.find('select', class_='week-filter')
    request_results = request_results.find_all('option')
    search_id_list = list()
    for result in request_results:
        if result.get('value')[0] == '2':
            search_id_list.append(result.get('value'))

    # Search the pages and append to list of album dicts.
    results = list()
    for search_id in search_id_list[:PAGES_TO_SEARCH]:
        search_url = "https://www.allmusic.com/newreleases/%s" % search_id
        page = requests.get(search_url, headers={'User-agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(page.content, 'html.parser')

        request_results = soup.find_all('div', class_='new-release')

        for idx, request_result in enumerate(request_results):
            meta = request_result.find('div', class_='meta-container')
            artist = meta.find('div', class_='artist')
            title = meta.find('div', class_='title')
            genre = meta.find('div', class_='genres')
            url = title.find('a')['href']

            artist_str = artist.get_text().replace('\n', '')[:-1]
            title_str = title.get_text().replace('\n', '')[:-1]
            stars = len(meta.find_all('img', class_='blue star')) + \
                0.5 * len(meta.find_all('img', class_='blue half'))

            # Get primary genre, removing all text after comma.
            if genre:
                genre_str = genre.get_text().replace('\n', '')[:-1]
            if ',' in genre_str:
                genre_str = genre_str[:genre_str.find(',')]

            # Skip albums that meet certain criteria.
            if any(gen in genre_str for gen in GENRE_IGNORE_LIST):
                continue
            if "Various Artists" in artist_str:
                continue

            # Select primary artist for albums with collaborators.
            if ' / ' in artist_str:
                artist_str = artist_str[:artist_str.find(' / ')]

            results.append({'artist': artist_str, 'title': title_str,
                'genre': genre_str, 'rating': stars, 'url': url,
                'source': 'allmusic'})

    return results


# Generate and sort by treblechef recommendation score.
def get_allmusic_scores(album_list):
    for album in album_list:
        if not('sp_popularity' in album):
            album['sp_popularity'] = 0
        date_obj = datetime.strptime(album['sp_date'], "%Y-%m-%dT00:00.000Z")
        time_score = max(60 - (datetime.now() - date_obj).days, 0)
        album['score'] = (album['rating'] / 5) * 60 + \
            album['sp_popularity'] / 100 * 20 + time_score / 60 * 20
        album['score'] = round(album['score'], 3)

    album_list = sorted(album_list, key=lambda k: k['score'], reverse=True)
    return album_list


# WHERE THE SEARCHING TAKES PLACE ######################################

releases = get_allmusic_newreleases()
allmusic_scraper = scrape.AlbumScraper(releases)
releases = allmusic_scraper.exec()
# releases = scrape.get_spotify_albums(releases)
# releases = scrape.get_spotify_artist(releases)
releases = get_allmusic_scores(releases)

# Write results to csv and json files.
with open('results/results_am.csv', mode='w') as csv_file:
    fieldnames = ['artist', 'title', 'genre', 'rating', 'score',
        'url', 'source', 'sp_popularity', 'sp_date',
        'sp_img', 'sp_album_id', 'sp_artist_id']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    csv_writer.writerows(releases)

with open('results/results_am.json', 'w') as json_file:
    json.dump(releases, json_file, indent=4)
