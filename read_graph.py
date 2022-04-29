from graph import spot_graph
from final_proj import request_query_with_cache, open_cache
CACHE_DICT = {}
CACHE_FILENAME = 'final.json'
GRAPH_FILENAME = 'graph.json'


CACHE_DICT = open_cache()
beyonce_cache = request_query_with_cache('spotify', 'Beyonce') # read cached track info
exam_graph = spot_graph(beyonce_cache, GRAPH_FILENAME) # read cached track graph

for key, value in exam_graph.graph.items():
    print(key, ' : ', value)