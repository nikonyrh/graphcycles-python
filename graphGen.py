import io
import sys
import numpy as np
import json
import random
import hashlib

class Graph:
    def __init__(self, size):
        self.size = size
        
        self.n_chars = int(np.ceil(np.log(size + 1)/np.log(16)))
        self.node_name_pattern = ('%%0%dx' % self.n_chars) * 2
        
        first_node = self.node_name(0,0)
        
        self.active  = set([first_node])
        self.visited = set()
        self.links   = {}
        
        self.visit(first_node)
    
    def node_name(self, i, j=None):
        if j is None:
            j = i[1]
            i = i[0]
        
        if i < 0 or j < 0 or i >= self.size or j >= self.size:
            return None
        
        return self.node_name_pattern % (i+1,j+1)
    
    def all_nodes(self):
        r = range(0,self.size)
        return sorted([self.node_name(i,j) for i in r for j in r])
    
    def link(self, a, b):
        if a == b:
            return
        
        if a not in self.links:
            self.links[a] = set()
        
        self.links[a].add(b)
    
    def active_nodes(self):
        return list(self.active)
    
    def neighbours(self, node_name):
        i = int(node_name[0:self.n_chars], 16) - 1
        j = int(node_name[self.n_chars:(2*self.n_chars)], 16) - 1
        
        result = []
        for di in range(-1,2):
            for dj in range(-1,2):
                name = self.node_name(i+di, j+dj)
                if name is not None:
                    result.append(name)
        
        return set(result)
    
    def active_neighbours(self, node_name):
        return list(self.neighbours(node_name) & self.active)
    
    def visited_neighbours(self, node_name):
        return list(self.neighbours(node_name) & self.visited)
    
    def visit(self, node_name):
        assert(node_name in self.active)
        assert(node_name not in self.visited)
        
        self.active.remove(node_name)
        self.visited.add(node_name)
        
        for node in self.neighbours(node_name):
            if node not in self.visited:
                self.active.add(node)
    
    def get_links(self):
        return {i: sorted(list(self.links[i])) for i in self.links.keys()}
    
    def dump(self):
        nodes = self.all_nodes()
        links = self.get_links()
        
        return {nodes[i]: links[nodes[i]] if nodes[i] in links else [] for i in range(len(nodes))}


def main(argv=[]):
    r       = range(4,200)
    p       = 2.5
    sizes   = [int(0.5 + i**p / r[0]**(p-1)) for i in r]
    n_iter  = 1
    
    rand = lambda i: random.randint(0, i-1)
    
    #print sizes; return
    
    for size in sizes:
        n_extra_links = int(3 + (0.5*size)**0.9)
        n_unlinks     = int(1 + (0.1*size)**0.7)
        
        for iter in range(0,n_iter):
            graph = Graph(size)
            
            while True:
                nodes   = graph.active_nodes()
                n_nodes = len(nodes)
                
                if n_nodes == 0:
                    break
                
                i    = random.randint(0, n_nodes-1)
                node =  nodes[i]
                
                neighbours    = graph.visited_neighbours(node)
                n_neighbours  = len(neighbours)
                
                assert(n_neighbours > 0)
                j = rand(n_neighbours)
                graph.link(node, neighbours[j])
                graph.visit(node)
            
            nodes   = graph.all_nodes()
            n_nodes = len(nodes)
            
            for i in range(0,n_extra_links):
                graph.link(nodes[rand(n_nodes)], nodes[rand(n_nodes)])
            
            for i in range(0, n_unlinks):
                node = nodes[rand(n_nodes)]
                
                if node in graph.links:
                    del graph.links[node]
            
            result = json.dumps(graph.dump(), sort_keys=True)
            #print result; return
            
            h = hashlib.sha1(result).hexdigest()
            with io.open('graphs/%06d_%s.json' % (size, h[0:8]), 'w', encoding='utf-8') as out:
                out.write(unicode(result))
    

if __name__ == '__main__':
    main(sys.argv)

