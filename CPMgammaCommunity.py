__author__ = 'roger'

import igraph as ig
import louvain
import pandas as pd
import matplotlib.pyplot as plt

G = ig.read("test.graphml")

partition = louvain.find_partition(G,method='CPM', resolution_parameter=0.018)
subs = partition.subgraphs()
community = 1
for com in subs:
    for node in com.vs:
        ogNode = G.vs.find(id=node['id'])
        ogNode['cpmNumber'] = community
    community += 1

ig.write(G, "mathCPM.graphml")