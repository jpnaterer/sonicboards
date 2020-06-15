import requests
import json
import pymongo
from bs4 import BeautifulSoup

# TODO: Create Class from below...
# https://softwareengineering.stackexchange.com/questions/297090/should-i-create-a-class-if-my-function-is-complex-and-has-a-lot-of-variables
# https://stackoverflow.com/questions/33072570/when-should-i-be-using-classes-in-python


class BandCampSongScraper:

    def __init__(self):
        self.album_list = list()
        self.song_list = list()
        self.skip_url_list = list()
        self.connect = pymongo.MongoClient()

    def exec(self):
        self.get_albums_to_add()
        self.get_album_info()
        self.add_songs_to_db()
        self.rem_albums_from_db()

    # Initialize the album list from the local mongo database.
    def get_albums_to_add(self):
        # Collect all albums {id, url} currently in the sonicboards database.
        collection = self.connect.sonicboards.canada
        album_list = list(collection.find({}, {"_id": 1, "url": 1}))

        # Remove previously added albums to prevent re-scraping each web page.
        collection = self.connect.sonicboards.canada_songs
        prev_song_list = list(collection.find({}, {"_id": 0, "album_id": 1}))
        prev_album_list = [a['album_id'] for a in prev_song_list]
        prev_album_list = set(prev_album_list)
        album_list = [a for a in album_list
            if a['_id'] not in prev_album_list]

    # Iterate through album list to find the songs from each url.
    def get_album_info(self):
        for album_idx, album in enumerate(self.album_list[:1000]):
            # Print an update message every 200 queries.
            if(album_idx % 200 == 0):
                print("%d pages searched" % album_idx)

            # Request the webpage retrieved from the album database.
            response = requests.get(album['url'],
                headers={'User-agent': 'Mozilla/5.0'})

            # Search for a javascript dict that contains album information. If
            # no result is found, check if the webpage has been removed.
            start_idx = response.text.find("trackinfo: [")
            if start_idx == -1:
                print("skipping url: %s" % album["url"])
                if "<h2>Sorry, that something isn’t here." in response.text:
                    self.skip_url_list.append(album["url"])
                    continue
                print("*** %s ***" % response.status_code)
                continue

            # Create response text and get album info from javascript dict.
            r = response.text
            start_idx = start_idx + len("trackinfo: [") - 1
            end_idx = start_idx + r[start_idx:].find("],") + 1
            album_info = json.loads(r[start_idx:end_idx])

            # Search for a html table that contains album lyrics.
            start_idx = r.find('<table class=')
            end_idx = start_idx + r[start_idx:].find('</table>') + 8
            soup = BeautifulSoup(r[start_idx:end_idx], 'html.parser')

            # Use util method to scrape song table and add to full song list.
            curr_song_list = self.scrape_song_table(
                soup, album_info, album[["_id"]])
            self.song_list.extend(curr_song_list)

    # A static util method to scrape the html table for song lyrics.
    def scrape_song_table(self, soup, album_info, album_id):
        # Iterate through table rows. Each song corresponds to a row with
        # an additional row if the track has lyrics.
        track_idx = 0
        curr_song_list = list()
        for song_result in soup.find_all('tr'):
            row_class = song_result.get('class')[0]
            if row_class == 'track_row_view':
                song_title = album_info[track_idx]['title']
                song_dur = album_info[track_idx]['duration']
                song_id = album_info[track_idx]['track_id']

                # Get the mp3 file location of the full song.
                url = ""
                if album_info[track_idx]['file']:
                    f_str = list(album_info[track_idx]['file'].keys())[0]
                    url = album_info[track_idx]['file'][f_str]

                # Store information to be added to full song list.
                track_idx = track_idx + 1
                curr_song_list.append({"title": song_title, "file": url,
                    "duration": song_dur, "track_num": track_idx,
                    "album_id": album_id, "bandcamp_id": song_id})

            # If on a lyric row, add lyrics to the last song added.
            if row_class == 'lyricsRow':
                song_lyrics = song_result.find('div').text
                curr_song_list[-1]["lyrics"] = song_lyrics
        return curr_song_list

    # Add song information to local mongo database.
    def add_songs_to_db(self):
        collection = self.connect.sonicboards.canada_songs
        skip_count = 0
        for song in self.song_list:
            try:
                collection.insert_one(song)
            except pymongo.errors.DuplicateKeyError:
                skip_count += 1
        print("%d/%d duplicates skipped" % (skip_count, len(self.song_list)))

    # Remove albums whose webpages who have been removed.
    def rem_albums_from_db(self):
        collection = self.connect.sonicboards.canada
        for url in self.skip_url_list:
            collection.delete_one({"url": url})


bcss = BandCampSongScraper()
bcss.exec()
