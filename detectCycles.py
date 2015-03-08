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
        
        'arr': lambda A: np.array(A),
        'bsr': lambda A: scipy.sparse.bsr_matrix(A),
        'csc': lambda A: scipy.sparse.csc_matrix(A),
        'csr': lambda A: scipy.sparse.csr_matrix(A)
    }
    
    results = [';'.join(['#'] + sorted(matrix_types.keys()) + ['has_cycles'])]
    print results[-1]
    
    for fname in sorted(glob.glob('graphs/*.json')):
        init_times = {}
        
        start = time.time()
        with open(fname) as file:
            graph = json.load(file)
        init_times['1_load'] = time.time() - start
        
        #print json.dumps(graph, indent=4, sort_keys=True); return
        
        start = time.time()
        nodes   = graph.keys()
        n_nodes = len(nodes)
        node2id = {nodes[i]: i for i in range(n_nodes)}
        id2node = {i: nodes[i] for i in range(n_nodes)}
        
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
        init_times['2_array'] = time.time() - start
        
        start = time.time()
        matrix = np.array(matrix)
        matrix = scipy.sparse.coo_matrix((matrix[:,0], (matrix[:,1], matrix[:,2])), (n_nodes, n_nodes))
        init_times['3_sparse'] = time.time() - start
        
        times = []
        result_row = ['%d' % n_nodes]
        
        for t in sorted(matrix_types.keys()):
            start      = time.time()
            has_cycles = ((matrix_types[t](matrix) ** n_nodes).sum() > 0).tolist()
            duration   = time.time() - start
            
            result_row.append('%.6f' % duration)
            times.append({'type': t, 'has_cycles': has_cycles, 'duration': duration})
        
        result_row.append('%d' % (1 if has_cycles else 0))
        results.append(';'.join(result_row))
        
        print results[-1]
        sys.stdout.flush()
        
        '''
        times.sort(key=lambda i: i['duration'])
        print json.dumps({
            'n_nodes':    n_nodes,
            'init_times': init_times,
            'times':      times
        }, indent=4, sort_keys=True);
        '''
    
    #print '\n'.join(results + [''])

if __name__ == '__main__':
    main(sys.argv)

