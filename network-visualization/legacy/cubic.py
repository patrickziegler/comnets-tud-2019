import numpy as np


def get_topology(u=3, v=3, w=3, l=200, p=25, c=(10, 1)):
    """
    (nodes, edges) = get_topology(u=3, v=3, w=3, l=200, p=25, c=(10, 1))

    u, v, w ..... are the number of nodes in each dimension
    l ........... is the length of one edge in pixels
    p ........... is the angle of view
    c ........... is a tuple of mean value and standard deviation
                  for computing random edge costs (gaussian distribution)
    """
    N = np.ones((u, v, w))
    N[0,0,:] = 110 * N[0,0,:] + np.cumsum(N[0,0,:])
    N[0,1:,:] = 10
    N[1:,:,:] = 100
    N[0,:,:] = np.cumsum(N[0,:,:], axis=0)
    N = np.cumsum(N, axis=0)
    N = np.transpose(N, (2,0,1))
    
    x = l * np.tile(np.arange(0,u), (w,v,1)) + \
        (l * np.cos(np.pi * p / 180) / 2) * \
        np.transpose(np.tile(np.arange(0,u), (w,v,1)), (2,1,0))

    y = l * np.tile(np.arange(0,u).reshape((u,1)), (v,1,w)) - \
        (l * np.sin(np.pi * p / 180) / 2) * \
        np.transpose(np.tile(np.arange(0,u), (w,v,1)), (2,1,0))
    
    n = N.reshape(np.prod(N.shape))
    x = x.reshape(np.prod(x.shape))
    y = y.reshape(np.prod(y.shape))
    
    nodes = np.column_stack((n, x, y))
    nodes = nodes[nodes[:,0].argsort(),]  # sortrows first col
    
    e1 = n[np.column_stack((np.arange(0,len(n)-1), np.arange(1,len(n))))]
    mask = np.ones(len(e1), dtype=bool)
    mask[np.arange(u-1,len(e1),u)] = False
    e1 = e1[mask]
    
    n = np.transpose(N, (2,0,1)).reshape(np.prod(N.shape))
    e2 = n[np.column_stack((np.arange(0,len(n)-1), np.arange(1,len(n))))]
    mask = np.ones(len(e2), dtype=bool)
    mask[np.arange(v-1,len(e2),v)] = False
    e2 = e2[mask]

    n = np.transpose(N, (1,2,0)).reshape(np.prod(N.shape))
    e3 = n[np.column_stack((np.arange(0,len(n)-1), np.arange(1,len(n))))]
    mask = np.ones(len(e3), dtype=bool)
    mask[np.arange(w-1,len(e3),w)] = False
    e3 = e3[mask]
    
    edges = np.concatenate((e1, e2, e3), axis=0)
    edges = edges[edges[:,0].argsort(),]  # sortrows first col
    
    # append costs of gaussian distribution
    cost = np.random.normal(c[0], c[1], edges.shape[0])
    edges = np.column_stack((edges, cost))
    
    return nodes, edges


def write_json(topology, path="topo.json"):
    (nodes, edges) = topology
    
    with open(path, "w") as fo:
        
        fo.write("{\n\t\"nodes\": [\n")
        
        for i in range(0, nodes.shape[0]):
            fo.write("\t\t{\n")
            fo.write("\t\t\t\"id\": " + str(int(nodes[i,0])) + ",\n")
            fo.write("\t\t\t\"label\": \"" + str(int(nodes[i,0])) + "\",\n")
            fo.write("\t\t\t\"x\": " + str(nodes[i,1]) + ",\n")
            fo.write("\t\t\t\"y\": " + str(nodes[i,2]) + "\n")
            if i == nodes.shape[0] - 1:
                break
            fo.write("\t\t},\n")
        
        fo.write("\t\t}\n\t],\n\t\"edges\": [\n")
        
        for i in range(0, edges.shape[0]):
            fo.write("\t\t{\n")
            fo.write("\t\t\t\"from\": " + str(int(edges[i,0])) + ",\n")
            fo.write("\t\t\t\"to\": " + str(int(edges[i,1])) + ",\n")
            fo.write("\t\t\t\"cost\": " + str(edges[i,2]) + "\n")
            if i == edges.shape[0] - 1:
                break
            fo.write("\t\t},\n")
            
        fo.write("\t\t}\n\t]\n}")
    
    
if __name__ == "__main__":
    write_json(get_topology())
