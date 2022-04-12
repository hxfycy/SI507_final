from requests_oauthlib import OAuth1
import requests
from secret import secret
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import os
import json
from flask import Flask, render_template, request

# Secret var
SPOT_ID = secret.SPOTIPY_CLIENT_ID
SPOT_SECRET = secret.SPOTIPY_CLIENT_SECRET
twi_key = secret.Twitter_API_Key
twi_secret = secret.Twitter_API_Key_Secret
twi_bearer_token = secret.Twitter_Bearer_Token
twi_token = secret.Twitter_Access_Token
twi_token_secret = secret.Twitter_Access_Token_Secret

search_url = "https://api.twitter.com/2/tweets/search/recent"

CACHE_FILENAME = ''
# query_params = {'query': '#MarchMadness'}

def open_cache():
    '''Method to open the cache file if exists, otherwise, return empty dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    '''Method to save the current cache to disk.
    '''
    fw = open(CACHE_FILENAME,"w")
    fw.write(json.dumps(cache_dict))
    fw.close()

def bearer_oauth(r):
    '''Method required by bearer token authentication.
    '''
    r.headers["Authorization"] = f"Bearer {twi_bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def get_tweet(query):
    ''' cal for twitter API, search for a query
    '''
    query_params = {'query' : query}
    #query_params1 = {'query': '#MarchMadness'}
    twi_response = connect_to_endpoint(search_url,query_params)
    print(json.dumps(twi_response, indent=4, sort_keys=True))
    # recent_tweet = twi_response[0]['text']
    # rint(recent_tweet)
    return twi_response

def get_spotify(query):
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOT_ID, client_secret=SPOT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    results = sp.search(q='artist:' + query, type='artist')
    artist_uri = results['artists']['items'][0]['uri']

    albums = sp.artist_albums(artist_uri, album_type='album')
    song_counts = {}
    album_name = ''
    track_total = ''
    for item in albums['items']:
        for key, value in item.items():
            if key == 'name':
                album_name = value
            if key == 'total_tracks':
                track_total = value
            song_counts[album_name] = track_total
    artist = albums['items'][0]['artists'][0]['name']
   # song_counts['artist'] = search_terms
    print('spotify_save_results', song_counts)
    del song_counts['']
    return song_counts
    
def request_query(url, params=None):
    '''request for a query with cache
    '''
    if params != None:
        zcode = params
        cache_idx = url + zcode
        if cache_idx in CACHE_DICT:
            print('Data Hit in Cache', cache_idx)
            print(CACHE_DICT[cache_idx])
            return CACHE_DICT[cache_idx]
        else:
            print('Fetching data from API')
            data = get_spotify(params)
            print('spotify_fetch', data)
            CACHE_DICT[cache_idx] = data
            print(CACHE_DICT[cache_idx])
            save_cache(CACHE_DICT)
            return CACHE_DICT[cache_idx]

def graph_bfs(G,node):
    visited = []
    queue = [] 
    visited.append(node)
    queue.append(node)

    while queue:          # Creating loop to visit each node
        m = queue.pop(0) 
        print (m, end = " ") 

    for neighbour in G[m]:
      if neighbour not in visited:
        visited.append(neighbour)
        queue.append(neighbour)
    return visited

def main():
    # json_response = connect_to_endpoint(search_url, query_params)
    search_term = 'LaLaLand'
    json_response = get_tweet(search_term)
    spotify_response = get_spotify(search_term)
    # print(json.dumps(json_response, indent=4, sort_keys=True))

CACHE_DICT = open_cache()
if __name__ == "__main__":
    main()