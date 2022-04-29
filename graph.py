import json
import random

class spot_graph: # undirected graph
    def __init__(self, data_list, jsonfile=None):
        self.data_list = data_list # original data list
        self.graph = {}
        if jsonfile != None:
            file = open(jsonfile,"r")
            cont = file.read()
            load_graph = json.loads(cont)
            for index in range(len(load_graph)):
                self.graph[index] = load_graph[str(index)]
    
    def add_vertex(self,vertex):
        '''if vertex is not in graph dict, then add vertex to the dictionary'''
        if vertex not in self.graph:
            self.graph[vertex] = []

    def add_edge(self, edge):
        """ assumes that edge is of type set, tuple or list; 
            between two vertices can be multiple edges! 
        """
        edge = set(edge)
        vertex1, vertex2 = tuple(edge)
        for x, y in [(vertex1, vertex2), (vertex2, vertex1)]:
            if x in self.graph:
                self.graph[x].append(y)
            else:
                self.graph[x] = [y]
    
    def build_graph(self, key_list):
        '''build a graph by key_list from data_list, those songs with similar key value in key_list will get connected'''

        for src_idx in range(0,len(self.data_list)):
            # for ver_idx in len(self.data_list):
            self.add_vertex(src_idx)
            for ver_idx in range(src_idx,len(self.data_list)):
                self.add_vertex(ver_idx)
                link = True
                for key in key_list:
                    if abs(self.data_list[str(src_idx)][key]-self.data_list[str(ver_idx)][key])>0.3:
                        link = False
                        # break
                if (link == True) and (ver_idx != src_idx):
                    self.add_edge({src_idx,ver_idx})

    def save_graph(self, jsonfile):
        content_to_write = json.dumps(self.graph)
        file = open(jsonfile,"w")
        file.write(content_to_write)
        file.close()

    def graph_bfs(self):
        root = random.randint(0,len(self.data_list)-1)
        # random.randint(0, 9)
        visited = []
        visited_song = {} # convert node to track name
        queue = [] 
        visited.append(root)
        queue.append(root)

        # first, build the tree according to random root 
        if self.graph == {}:
            key_list = ['valence','energy','liveness']
            self.build_graph(key_list)
        while queue:          # Creating loop to visit each node
            m = queue.pop(0) 
            print (m, end = " ") 

            for neighbour in self.graph[m]:
                if neighbour not in visited:
                    visited.append(neighbour)
                    queue.append(neighbour)

        idx =0
        for item in visited:
            visited_song[idx] = self.data_list[str(item)]
            idx +=1

        return visited_song