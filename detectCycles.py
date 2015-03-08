import sys
import json
import glob
import time
import numpy as np
import scipy.sparse


def main(argv=[]):
    matrix_types = {
        # These are a lot slower than other alternatives
        #'lil': lambda A: scipy.sparse.lil_matrix(A),
        #'dok': lambda A: scipy.sparse.dok_matrix(A),
        
        'arr': lambda A: np.array(A), # This will waste lots of memory on larger networks
        'bsr': lambda A: scipy.sparse.bsr_matrix(A),
        'csc': lambda A: scipy.sparse.csc_matrix(A),
        'csr': lambda A: scipy.sparse.csr_matrix(A)
    }
    
    print ';'.join(['#'] + sorted(matrix_types.keys()) + ['has_cycles'])
    
    for fname in sorted(glob.glob('graphs/*.json')):
        # Load the graph
        with open(fname) as file:
            graph = json.load(file)
        
        nodes   = graph.keys()
        n_nodes = len(nodes)
        node2id = {nodes[i]: i for i in range(n_nodes)}
        id2node = {i: nodes[i] for i in range(n_nodes)}
        
        # Create the sparse state-transition matrix
        matrix = []
        
        for node in nodes:
            i = node2id[node]
            
            n_links = len(graph[node])
            if n_links == 0:
                continue
            
            weight = 1.0 / n_links
            for link in graph[node]:
                j = node2id[link]
                matrix.append([weight, i, j])
        
        matrix = np.array(matrix)
        matrix = scipy.sparse.coo_matrix((matrix[:,0], (matrix[:,1], matrix[:,2])), (n_nodes, n_nodes))
        
        times = []
        result_row = ['%d' % n_nodes]
        
        # Benchmark different matrix algebra implementations
        for t in sorted(matrix_types.keys()):
            start      = time.time()
            has_cycles = ((matrix_types[t](matrix) ** n_nodes).sum() > 0).tolist()
            duration   = time.time() - start
            
            result_row.append('%.6f' % duration)
            times.append({'type': t, 'has_cycles': has_cycles, 'duration': duration})
        
        print ';'.join(result_row)
        sys.stdout.flush()


if __name__ == '__main__':
    main(sys.argv)

