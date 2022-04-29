from requests_oauthlib import OAuth1
import requests
from secret import secret
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import os
import json
from flask import Flask, render_template, request
from graph import spot_graph
import plotly.graph_objs as go
import itertools

app=Flask(__name__,static_folder="static")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# Secret var
SPOT_ID = secret.SPOTIPY_CLIENT_ID
SPOT_SECRET = secret.SPOTIPY_CLIENT_SECRET
twi_key = secret.Twitter_API_Key
twi_secret = secret.Twitter_API_Key_Secret
twi_bearer_token = secret.Twitter_Bearer_Token
twi_token = secret.Twitter_Access_Token
twi_token_secret = secret.Twitter_Access_Token_Secret

search_url = "https://api.twitter.com/2/tweets/search/recent"
db_name    = 'final.sqlite'
CACHE_FILENAME = 'final.json'
GRAPH_FILENAME = 'graph.json'
CACHE_DICT = {}
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
    '''search one artist's top track 
    '''
    client_credentials_manager = SpotifyClientCredentials(client_id=SPOT_ID, client_secret=SPOT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    results = sp.search(q='artist:' + query, type='artist')
    if (len(results['artists']['items']) ==0):
        return []
    else:
        artist_uri = results['artists']['items'][0]['uri']
    top_track = sp.artist_top_tracks(artist_uri)
    res_list = {}
    index = 0
    for track in top_track['tracks']:
        track_res = sp.audio_features(track['uri'])
        track_fea = {}
        track_fea['album']              = track['album']['name']
        track_fea['name']               = track['name']
        track_fea['popularity']         = track['popularity']
        track_fea['acousticness']       = track_res[0]['acousticness']
        track_fea['danceability']       = track_res[0]['danceability']
        track_fea['energy']             = track_res[0]['energy']
        track_fea['instrumentalness']   = track_res[0]['instrumentalness']
        track_fea['liveness']           = track_res[0]['liveness']
        track_fea['loudness']           = track_res[0]['loudness']
        track_fea['speechiness']        = track_res[0]['speechiness']
        track_fea['tempo']              = track_res[0]['tempo']
        track_fea['valence']            = track_res[0]['valence']
        print(track_fea)
        res_list[str(index)] = track_fea
        index +=1
    return res_list
    
def request_query_with_cache(url, params=None):
    '''request for a query with cache
    '''
    if params != None:
        zcode = params
        cache_idx = url +':'+ zcode
        if cache_idx in CACHE_DICT:
            print('Data Hit in Cache', cache_idx)
            # print(CACHE_DICT[cache_idx])
            return CACHE_DICT[cache_idx]
        else:
            print('Fetching data from API')
            if 'spotify' in url:
                data = get_spotify(params)
                # print('spotify_fetch', data)
                
                if(data != []):
                    CACHE_DICT[cache_idx] = data
                    # print(CACHE_DICT[cache_idx])
                    save_cache(CACHE_DICT)
                else: return []
            elif 'twitter' in url:
                data = get_tweet(params)
                if(data != []):
                    CACHE_DICT[cache_idx] = data
                    save_cache(CACHE_DICT)
                else: return []
            return CACHE_DICT[cache_idx]


def recom_by_artist(query_artist):
    song_list = request_query_with_cache('spotify',query_artist)
    if query_artist == 'Beyonce': # load prestored graph
        song_graph = spot_graph(song_list,GRAPH_FILENAME)
    else: song_graph =spot_graph(song_list)
    recom_list = song_graph.graph_bfs()

    if query_artist == 'Beyonce': # save graph
        song_graph.save_graph(GRAPH_FILENAME)
    
    return recom_list


# just for test
'''
def main():
    reco_list = recom_by_artist ('Beyonce')
    top_list = request_query_with_cache('spotify', 'Whietney Houston')
    # reco_list = recom_by_artist ('Kanye West')
    # recp_list = 
    top_list =request_query_with_cache('spotify','Beyonce')
    # rec = dict(itertools.islice(reco_list.items(),5))
    top_tru = dict(itertools.islice(top_list.items(),5))
    twi_response = request_query_with_cache('twitter','Beyonce')
    text_res = twi_response['data']
    for record in text_res:
        print(record['text'])
    spotify_response = request_query_with_cache('spotify','Beyonce')
'''

@app.route("/")
def index():
    return render_template("recommend_main.html")

@app.route("/recommend_result",methods=['POST'])
def recommend_result():
    query_artist = request.form['name']
    vis_type = request.form['visualization']
    if vis_type == 'Top_song':
        song_list=request_query_with_cache('spotify',query_artist)
        return render_template("recommend_result.html",result=song_list)
    elif vis_type == 'Recom':
        song_list =recom_by_artist(query_artist)
        song_list = dict(itertools.islice(song_list.items(),3))
        return render_template("recommend_result.html",result=song_list)
    elif vis_type == 'Twi':
        twi_res = request_query_with_cache('twitter',query_artist)
        twi_text =twi_res['data']
        return render_template("twitter_res.html",result=twi_text)

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

CACHE_DICT = open_cache()
if __name__=="__main__":
    # main()
    app.run(debug=True)