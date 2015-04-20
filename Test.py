__author__ = 'roger'

import networkx as nx
import community

g = nx.read_graphml("testun.graphml")
part = community.best_partition(g)
for com in part.values():
    print "hello"
print 'hello'

nx.write_gml(g, "test.gml")