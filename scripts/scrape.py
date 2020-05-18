import spotipy
from datetime import datetime
from spotipy.oauth2 import SpotifyClientCredentials

# Create a spotipy object to query spotify. Requires exporting
# SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET as environment variables.
# https://spotipy.readthedocs.io/en/2.11.2/
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


# Given a list of album dicts, search popularity of the artist.
def get_spotify_artist(album_list):
    for album in album_list:
        sp_result = sp.artist(album['sp_artist_id'])
        album['sp_popularity'] = sp_result['popularity']
        # result['sp_genres'] = sp_result['genres']
    return album_list


# Given a list of album dicts, search details about the album on spotify.
# Remove elements from the list that cannot be found on spotify.
def get_spotify_albums(album_list_in):
    album_list = list()
    for album in album_list_in:
        # Spotify results.
        q = "%s %s" % (album['artist'], album['title'])
        sp_results = sp.search(q, type='album', limit=5)
        sp_results = sp_results['albums']['items']

        # Remove elements from the list that are not found on spotify.
        # Assume the first result is correct?
        if not(sp_results):
            continue
        sp_result = sp_results[0]

        # Get spotify album image
        image_str = None
        for img_obj in sp_result['images']:
            if img_obj['height'] == 300:
                image_str = img_obj['url']

        # Remove list elements outside of past two months.
        if sp_result['release_date_precision'] != 'day':
            continue
        date_obj = datetime.strptime(sp_result['release_date'], '%Y-%m-%d')
        if (datetime.now() - date_obj).days > 60:
            continue

        album['sp_date'] = "%sT00:00.000Z" % sp_result['release_date']
        album['sp_album_id'] = sp_result['id']
        album['sp_img'] = image_str
        album['sp_artist_id'] = sp_result['artists'][0]['id']
        album_list.append(album)

    return album_list
