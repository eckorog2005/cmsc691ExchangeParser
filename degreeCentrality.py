import networkx as nx


G = nx.read_gexf("graph.gexf")
cent = nx.out_degree_centrality(G)
nx.set_node_attributes(G, 'degreeCentrality', cent)
nx.write_gexf(G, "graphDegreeCent.gexf")

max = 0
outDegree = list(G.out_degree().values())
for value in outDegree:
    if value > max:
        max = value

result = 0
numOfNodes = nx.number_of_nodes(G)
for value in outDegree:
    result += (max - value)

result /= (numOfNodes - 1) * float(numOfNodes - 2)
print result
