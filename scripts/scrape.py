import spotipy
import textdistance
from spotipy.oauth2 import SpotifyClientCredentials

# Create a spotipy object to query spotify. Requires exporting
# SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET as environment variables.
# https://spotipy.readthedocs.io/en/2.11.2/
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


# The parent class that provides spotify utils to scrape album information.
class AlbumScraper:

    def __init__(self, album_list):
        self.album_list = album_list

    def run(self):
        self.get_spotify_albums()
        self.get_spotify_artist()
        return self.album_list

    # Given a list of album dicts, search popularity of the artist.
    def get_spotify_artist(this):
        for album in this.album_list:
            sp_result = sp.artist(album['sp_artist_id'])
            album['sp_popularity'] = sp_result['popularity']

    # Given a list of album dicts, search details about the album on spotify.
    # Remove elements from the list that cannot be found on spotify.
    def get_spotify_albums(this):
        album_list_new = list()
        for album in this.album_list:
            # Spotify results.
            q = "%s %s" % (album['artist'], album['title'])
            sp_results = sp.search(q, type='album', limit=1)
            sp_results = sp_results['albums']['items']

            # Ignore results that are not found on spotify.
            # Assume the first result is correct?
            if not(sp_results):
                continue
            sp_resp = sp_results[0]

            # Ignore results that do not have a precise release date.
            if sp_resp['release_date_precision'] != 'day':
                continue

            # Ignore results that are short-length releases.
            if sp_resp['total_tracks'] <= 2:
                continue

            # Ignore results that are too different from intended search.
            # A token based string diff is used between album title and artist.
            txt_diff1 = textdistance.jaccard.normalized_distance(
                album['artist'].lower(), sp_resp['artists'][0]['name'].lower())
            txt_diff2 = textdistance.jaccard.normalized_distance(
                album['title'].lower(), sp_resp['name'].lower())
            if(txt_diff1 + txt_diff2 > 1):
                continue

            # Get spotify album image.
            image_str = None
            for img_obj in sp_resp['images']:
                if img_obj['height'] == 300:
                    image_str = img_obj['url']

            album['sp_date'] = "%sT00:00.000Z" % sp_resp['release_date']
            album['sp_album_id'] = sp_resp['id']
            album['sp_img'] = image_str
            album['sp_artist_id'] = sp_resp['artists'][0]['id']
            album_list_new.append(album)

        this.album_list = album_list_new
