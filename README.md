# Project Description
A flask-based recommendation system with the data fetched from the Spotify, according to the user's input.

# Required Packages:
spotipy, flask, plotly, requests

# How to run: 
Run the final_proj.py
There're several interaction options: Get Top track of one artist, Get Recommendation of the artist, and check the recent twitter comments of one artist & track.

# Routes:
/-> index route
/recommend_result -> recommend & top track results
/twitter_res -> twitter comments

# Data Source
All the Data comes from Spotify and Twitter API, I also cached several datas in the "final.json" and one built graph in "graph.json"

# Data Structures:
A graph will be built for every searched artist, each node will represent one popular track, the link will be built according to the similarity between two tracks, the similarity is evaluated by the "energy", "liveness", "valence" info of each track. The recommendation will use bread-first search to get the recommendation result with nearest distance. 

