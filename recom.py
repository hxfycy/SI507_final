from graph import spot_graph
import json


def get_songlist(query_artist):
    spotify_response = request_query_with_cache('spotify','Beyonce') 